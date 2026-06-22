import os
import uuid
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import jwt

load_dotenv()

# Logging Setup
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s",
    handlers = [
        logging.StreamHandler(), # terminal
        logging.FileHandler("grocerybot.log") # log file
    ]
)
logger = logging.getLogger("grocerybot")

# App Setup
app = FastAPI(
    title = "GroceryBot API",
    description = "Smart grocery tracking chatbot",
    version = "1.0.0"
)
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8501"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins = ALLOWED_ORIGINS,
    allow_credentials = True,
    allow_methods = ["GET", "POST"], 
    allow_headers = ["*"],
)
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret-in-production")
JWT_EXPIRE = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

_graphs = {}

_login_attempts: dict = defaultdict(list)
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOGIN_WINDOW_SECONDS = int(os.getenv("LOGIN_WINDOW_SECONDS", "300")) # 5 minutes

def check_rate_limit(client_ip: str):
    """Block IP if too many login attempts in time window."""
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=LOGIN_WINDOW_SECONDS)

    _login_attempts[client_ip] = [
        t for t in _login_attempts[client_ip]
        if t > window_start
    ]

    if len(_login_attempts[client_ip]) >= MAX_LOGIN_ATTEMPTS:
        logger.warning(f"Rate limit hit for IP: {client_ip}")
        raise HTTPException(
            status_code = 429,
            detail = (
                f"Too many login attempts. "
                f"Please wait {LOGIN_WINDOW_SECONDS // 60} minutes."
            )
        )

    _login_attempts[client_ip].append(now)
# JWT Helpers
def create_token(user_id: int, user_name: str) -> str:
    payload = {
        "user_id" : user_id,
        "user_name": user_name,
        "exp" : datetime.utcnow() + timedelta(hours=JWT_EXPIRE)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please login again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    return decode_token(credentials.credentials)

class RegisterRequest(BaseModel):
    name : str
    email : str
    password: str
    phone : Optional[str] = None

class LoginRequest(BaseModel):
    email : str
    password: str

class ChatRequest(BaseModel):
    message : str
    thread_id: Optional[str] = None

@app.get("/health")
def health():
    logger.info("Health check called")
    return {
        "status" : "ok",
        "message": "GroceryBot API is running ",
        "version": "1.0.0"
    }
@app.post("/auth/register")
def register(req: RegisterRequest):
    logger.info(f"Register attempt: {req.email}")
    from db.database import get_session
    from db.crud import create_user
    from db.schemas import UserCreate
    session = get_session()
    try:
        result = create_user(session, UserCreate(
            name = req.name,
            email = req.email,
            password = req.password,
            phone = req.phone
        ))
        if isinstance(result, str):
            logger.warning(f"Register failed: {result}")
            raise HTTPException(status_code=400, detail=result)

        token = create_token(result.id, result.name)
        logger.info(f"User registered: {result.email} (id={result.id})")
        return {
            "message" : "Account created successfully!",
            "token" : token,
            "user_id" : result.id,
            "user_name": result.name,
            "email" : result.email
        }
    finally:
        session.close()

@app.post("/auth/login")
def login(req: LoginRequest):
    """Login with rate limiting — max 5 attempts per 5 minutes."""
    logger.info(f"Login attempt: {req.email}")
    check_rate_limit(req.email)

    from db.database import get_session
    from db.crud import login_user
    session = get_session()
    try:
        result = login_user(session, req.email, req.password)
        if isinstance(result, str):
            logger.warning(f"Login failed: {req.email} — {result}")
            raise HTTPException(status_code=401, detail=result)

        token = create_token(result.id, result.name)
        logger.info(f"Login success: {result.email}")
        _login_attempts[req.email] = []
        return {
            "message" : f"Welcome back, {result.name}!",
            "token" : token,
            "user_id" : result.id,
            "user_name": result.name,
            "email" : result.email
        }
    finally:
        session.close()
@app.post("/chat")
def chat(req: ChatRequest, user: dict = Depends(get_current_user)):
    """Send message to real LangGraph agent."""
    user_id = user["user_id"]
    user_name = user["user_name"]
    thread_id = req.thread_id or str(uuid.uuid4())

    logger.info(f"Chat: user={user_id} thread={thread_id[:8]} msg={req.message[:50]}")

    if user_id not in _graphs:
        from app.graph import build_graph
        _graphs[user_id] = build_graph()
        logger.info(f"New graph created for user {user_id}")

    graph = _graphs[user_id]
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = graph.invoke(
            {
                "messages" : [{"role": "user", "content": req.message}],
                "thread_id": thread_id,
                "user_id" : user_id,
                "user_name": user_name,
            },
            config=config
        )
        response = result["messages"][-1].content

        from db.database import get_session
        from db.crud import save_message
        session = get_session()
        try:
            save_message(session, user_id, thread_id, "user", req.message)
            save_message(session, user_id, thread_id, "bot", response)
        finally:
            session.close()

        logger.info(f"Chat response sent: user={user_id}")
        return {
            "reply" : response,
            "thread_id": thread_id
        }
    except Exception as e:
        logger.error(f"Chat error: user={user_id} error={e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/history/{thread_id}")
def chat_history(thread_id: str, user: dict = Depends(get_current_user)):
    user_id = user["user_id"]
    if user_id not in _graphs:
        return {"messages": []}

    graph = _graphs[user_id]
    config = {"configurable": {"thread_id": thread_id}}
    try:
        state = graph.get_state(config)
        msgs = []
        for m in state.values.get("messages", []):
            msgs.append({
                "role" : "user" if m.type == "human" else "bot",
                "content": m.content
            })
        return {"messages": msgs}
    except Exception as e:
        logger.error(f"History error: {e}")
        return {"messages": []}

@app.get("/slips")
def get_slips(
    user: dict = Depends(get_current_user)):
    from db.database import get_session
    from db.crud import get_slip_summary

    session = get_session()
    try:
        all_slips = get_slip_summary(session, int(user["user_id"]))
        return {"slips": all_slips}
    finally:
        session.close()

@app.post("/slips/upload")
async def upload_slip(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """Upload and process a grocery slip photo."""
    logger.info(f"Slip upload: user={user['user_id']} file={file.filename}")

    from slips.slip_parser import process_slip_image

    folder = os.getenv("SLIPS_FOLDER", "./slips_folder")
    os.makedirs(folder, exist_ok=True)

    unique_name = f"{user['user_id']}_{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(folder, unique_name)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    result = process_slip_image(file_path, user_id=user["user_id"])
    logger.info(f"Slip processed: {result}")
    return {"message": result}

@app.on_event("startup")
async def startup():
    """Initialize DB on startup."""
    from db.database import init_db
    init_db()
    logger.info("GroceryBot API started ")

@app.on_event("shutdown")
async def shutdown():
    logger.info("GroceryBot API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host = "0.0.0.0",
        port = int(os.getenv("PORT", "8000")),
        reload = True,
        workers = 1
    )

