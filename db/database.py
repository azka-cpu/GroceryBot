import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    # Build from parts if DATABASE_URL not set
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    port = port.strip() if port else "5432"
    name = os.getenv("DB_NAME", "grocery_db")
    user = os.getenv("DB_USER", "postgres")
    pwd = os.getenv("DB_PASSWORD", "")
    DATABASE_URL = f"postgresql://{user}:{pwd}@{host}:{port}/{name}"

print(f"DB URL: {DATABASE_URL[:40]}...")

engine = create_engine(
    DATABASE_URL,
    connect_args = {"sslmode": "require"},
    echo = False
)

SessionLocal = sessionmaker(
    bind = engine,
    autocommit = False,
    autoflush = False
)

def init_db():
    from db.models import Base
    Base.metadata.create_all(bind=engine)
    print("Database ready!")


def get_session() -> Session:
    return SessionLocal()


def test_connection() -> bool:
    try:
        s = get_session()
        s.execute(text("SELECT 1"))
        s.close()
        print("Connected!")
        return True
    except Exception as e:
        print(f" Failed: {e}")
        return False