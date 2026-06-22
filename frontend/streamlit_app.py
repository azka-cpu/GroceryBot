import streamlit as st
import requests
import uuid
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="GroceryBot",
    page_icon="",
    layout="wide"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background-color: #f0f2f8;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2d1b69 0%, #4a2c9e 50%, #6b3fa0 100%);
    padding-top: 20px;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.welcome-banner {
    background: linear-gradient(135deg, #ff9800 0%, #ff5722 100%);
    border-radius: 20px;
    padding: 25px 30px;
    color: white;
    margin-bottom: 25px;
}

.welcome-banner h1 {
    margin: 0;
    font-size: 28px;
    font-weight: 700;
}

.welcome-banner p {
    margin: 5px 0 0 0;
    opacity: 0.9;
    font-size: 14px;
}

.stat-card {
    border-radius: 16px;
    padding: 20px;
    color: white;
    text-align: center;
    margin-bottom: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.card-orange { background: linear-gradient(135deg, #ff9800, #ff5722); }
.card-purple { background: linear-gradient(135deg, #9c27b0, #673ab7); }
.card-blue { background: linear-gradient(135deg, #2196f3, #1976d2); }
.card-green { background: linear-gradient(135deg, #4caf50, #388e3c); }
.card-pink { background: linear-gradient(135deg, #e91e63, #c2185b); }
.card-teal { background: linear-gradient(135deg, #009688, #00796b); }

.stat-card .stat-number {
    font-size: 32px;
    font-weight: 800;
    margin: 5px 0;
}

.stat-card .stat-label {
    font-size: 13px;
    opacity: 0.9;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.slip-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    border-left: 5px solid #9c27b0;
}

.slip-card h4 {
    margin: 0 0 8px 0;
    color: #2d1b69;
    font-size: 16px;
}

.slip-card .slip-meta {
    color: #666;
    font-size: 13px;
    margin: 3px 0;
}

.slip-card .slip-total {
    font-size: 22px;
    font-weight: 700;
    color: #ff5722;
    margin-top: 8px;
}

.user-msg {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0;
    text-align: right;
    font-size: 14px;
    box-shadow: 0 2px 8px rgba(102,126,234,0.3);
}

.bot-msg {
    background: white;
    color: #333;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 0;
    border: 1px solid #e8e8e8;
    font-size: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.login-container {
    max-width: 420px;
    margin: 60px auto;
    background: white;
    border-radius: 24px;
    padding: 40px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.login-logo {
    text-align: center;
    margin-bottom: 30px;
}

.login-logo h1 {
    color: #2d1b69;
    font-size: 32px;
    margin: 10px 0 5px 0;
}

.login-logo p {
    color: #888;
    font-size: 14px;
}

.section-title {
    color: #2d1b69;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e8e8f0;
}

.stButton button {
    border-radius: 10px !important;
    font-weight: 600 !important;
}

.upload-area {
    background: white;
    border: 2px dashed #9c27b0;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    margin: 20px 0;
}

.upload-area h3 {
    color: #2d1b69;
    margin-bottom: 5px;
}

.upload-area p {
    color: #888;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

if "token" not in st.session_state:
    st.session_state.token = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "page" not in st.session_state:
    st.session_state.page = "dashboard"


def api_post(endpoint, data, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.post(
            f"{API_URL}{endpoint}",
            json=data,
            headers=headers,
            timeout=60
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def api_get(endpoint, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            headers=headers,
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def show_login():
    _, center, _ = st.columns([1, 1.2, 1])

    with center:
        st.markdown("""
        <div class="login-container">
            <div class="login-logo">
                <h1>GroceryBot</h1>
                <p>Smart Grocery Assistant</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            email = st.text_input(
                "Email address",
                key="li_email",
                placeholder="you@email.com"
            )
            password = st.text_input(
                "Password",
                type="password",
                key="li_pass",
                placeholder="••••••••"
            )

            if st.button("Login", use_container_width=True, type="primary"):
                if not email or not password:
                    st.warning("Please fill in all fields.")
                    return
                
                with st.spinner("Logging in..."):
                    response = api_post(
                        "/auth/login",
                        {"email": email, "password": password}
                    )
                
                if "token" in response:
                    st.session_state.token = response["token"]
                    st.session_state.user_name = response["user_name"]
                    st.session_state.user_id = response["user_id"]
                    st.rerun()
                else:
                    st.error(response.get("detail", "Login failed."))

        with tab2:
            name = st.text_input(
                "Full Name",
                key="rg_name",
                placeholder="Ahmad Ali"
            )
            email = st.text_input(
                "Email",
                key="rg_email",
                placeholder="you@email.com"
            )
            phone = st.text_input(
                "Phone",
                key="rg_phone",
                placeholder="03001234567"
            )
            password = st.text_input(
                "Password",
                type="password",
                key="rg_pass",
                placeholder="min 6 characters"
            )

            if st.button("Create Account", use_container_width=True, type="primary"):
                if not name or not email or not password:
                    st.warning("Please fill all required fields.")
                    return
                
                with st.spinner("Creating your account..."):
                    response = api_post(
                        "/auth/register",
                        {
                            "name": name,
                            "email": email,
                            "password": password,
                            "phone": phone
                        }
                    )
                
                if "token" in response:
                    st.session_state.token = response["token"]
                    st.session_state.user_name = response["user_name"]
                    st.session_state.user_id = response["user_id"]
                    st.rerun()
                else:
                    st.error(response.get("detail", "Registration failed."))


def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 10px 0 30px 0;">
            <h2 style="color:white; margin:5px 0; font-size:22px;">GroceryBot</h2>
            <p style="color:rgba(255,255,255,0.7); font-size:12px; margin:0;">
                Smart Grocery Assistant
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.15); border-radius:12px;
                    padding:12px; margin-bottom:25px; text-align:center;">
            <div style="color:white; font-weight:600; font-size:15px;">
                {st.session_state.user_name}
            </div>
            <div style="color:rgba(255,255,255,0.7); font-size:12px;">
                Active Member
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<p style='color:rgba(255,255,255,0.5); font-size:11px; "
            "letter-spacing:2px; margin-bottom:10px;'>MENU</p>",
            unsafe_allow_html=True
        )

        pages = {
            "Dashboard": "dashboard",
            "Chat": "chat",
            "Upload Slip": "upload",
            "My Slips": "slips",
        }

        for label, page_key in pages.items():
            is_active = st.session_state.page == page_key
            btn_color = "rgba(255,255,255,0.25)" if is_active else "transparent"
            btn_text_color = "white" if is_active else "rgba(255,255,255,0.8)"
            
            st.markdown(f"""
            <div style="margin:3px 0; border-radius:10px; 
                        background:{btn_color}; padding:10px 15px; 
                        text-align:left;">
                <span style="color:{btn_text_color}; font-weight:600; font-size:15px;">
                    {label}
                </span>
            </div>""", unsafe_allow_html=True)
            
            if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)

        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def show_dashboard():
    hour = datetime.now().hour
    greeting = (
        "Good Morning" if hour < 12
        else "Good Afternoon" if hour < 18
        else "Good Evening"
    )

    st.markdown(f"""
    <div class="welcome-banner">
        <div>
            <h1>Hello, {st.session_state.user_name}!</h1>
            <p>{greeting} - Welcome back to GroceryBot</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    result = api_get("/slips", token=st.session_state.token)
    slips = result.get("slips", [])

    total_slips = len(slips)
    total_spent = sum(s["total"] for s in slips)
    avg_monthly = total_spent / total_slips if total_slips else 0
    this_month = slips[-1]["total"] if slips else 0

    st.markdown('<p class="section-title">Overview</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="stat-card card-orange">
            <div class="stat-number">{total_slips}</div>
            <div class="stat-label">Total Slips</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="stat-card card-purple">
            <div class="stat-number">Rs.{total_spent:,.0f}</div>
            <div class="stat-label">Total Spent</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="stat-card card-blue">
            <div class="stat-number">Rs.{avg_monthly:,.0f}</div>
            <div class="stat-label">Monthly Avg</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="stat-card card-green">
            <div class="stat-number">Rs.{this_month:,.0f}</div>
            <div class="stat-label">This Month</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<p class="section-title">Recent Slips</p>', unsafe_allow_html=True)

        if not slips:
            st.markdown("""
            <div style="background:white; border-radius:16px; padding:40px;
                        text-align:center; color:#aaa;">
                <p>No slips yet - upload your first receipt!</p>
            </div>""", unsafe_allow_html=True)
        else:
            colors = ["#9c27b0", "#2196f3", "#ff9800", "#4caf50", "#e91e63"]
            for i, slip in enumerate(reversed(slips[-5:])):
                color = colors[i % len(colors)]
                st.markdown(f"""
                <div class="slip-card" style="border-left-color:{color};">
                    <h4>{slip['month']} - {slip['store']}</h4>
                    <div class="slip-meta">{slip['item_count']} items purchased</div>
                    <div class="slip-total">Rs. {slip['total']:,.2f}</div>
                </div>""", unsafe_allow_html=True)

    with col_right:
        st.markdown('<p class="section-title">Quick Actions</p>', unsafe_allow_html=True)

        actions = [
            ("Upload New Slip", "upload"),
            ("Ask GroceryBot", "chat"),
            ("View All Slips", "slips"),
        ]
        for label, page_key in actions:
            if st.button(label, key=f"qa_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()


def show_chat():
    st.markdown('<p class="section-title">Chat with GroceryBot</p>', unsafe_allow_html=True)

    st.divider()

    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align:center; padding:40px; color:#aaa;">
                <p>Ask me anything about your grocery spending!</p>
                <p style="font-size:12px;">
                    Try: "How much did I spend on Rice?" or "Compare January and February"
                </p>
            </div>""", unsafe_allow_html=True)

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="user-msg">You: {msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                content = msg["content"].replace("\n", "<br>")
                st.markdown(
                    f'<div class="bot-msg">GroceryBot: {content}</div>',
                    unsafe_allow_html=True
                )

    if st.session_state.messages:
        if st.button("New Conversation", use_container_width=False):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()

    st.markdown("Ask anything about your grocery spending:")
    user_input = st.chat_input("Type your question here...")
    if user_input:
        send_message(user_input)


def send_message(text):
    st.session_state.messages.append({"role": "user", "content": text})
    with st.spinner("Thinking..."):
        response = api_post(
            "/chat",
            {"message": text, "thread_id": st.session_state.thread_id},
            token=st.session_state.token
        )
    reply = response.get("reply", "Sorry, something went wrong.")
    st.session_state.messages.append({"role": "bot", "content": reply})
    st.rerun()


def show_upload():
    st.markdown('<p class="section-title">Upload Grocery Slip</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="upload-area">
        <h3>Upload Your Receipt</h3>
        <p>Groq Vision AI will read it automatically in 2-5 seconds</p>
        <p>Supports: JPG, PNG, WEBP</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Choose receipt photo",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )

    if uploaded:
        col_img, col_info = st.columns([1, 1])

        with col_img:
            st.image(uploaded, caption="Your Receipt")

        with col_info:
            st.markdown(f"""
            <div style="background:white; border-radius:16px; padding:25px;
                        box-shadow:0 2px 10px rgba(0,0,0,0.08);">
                <h4 style="color:#2d1b69; margin-bottom:20px;">File Details</h4>
                <p><b>Name:</b> {uploaded.name}</p>
                <p><b>Size:</b> {len(uploaded.getvalue())//1024} KB</p>
                <p><b>Type:</b> {uploaded.type}</p>
                <br>
                <p style="color:#666; font-size:13px;">
                    Groq Vision will extract all items and prices automatically
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Process Slip Now", use_container_width=True, type="primary"):
                with st.spinner("Reading your slip..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/slips/upload",
                            files={
                                "file": (
                                    uploaded.name,
                                    uploaded.getvalue(),
                                    uploaded.type
                                )
                            },
                            headers={
                                "Authorization": f"Bearer {st.session_state.token}"
                            },
                            timeout=120,
                        )
                        result = response.json()
                        message = result.get("message", "")
                        
                        if message:
                            st.success(message)
                        else:
                            st.info("Slip processed successfully!")
                    except Exception as e:
                        st.error(f"Upload failed: {str(e)}")


def show_slips():
    st.markdown('<p class="section-title">My Grocery Slips</p>', unsafe_allow_html=True)

    with st.spinner("Loading your slips..."):
        result = api_get("/slips", token=st.session_state.token)

    slips = result.get("slips", [])

    if not slips:
        st.markdown("""
        <div style="background:white; border-radius:16px; padding:60px;
                    text-align:center; color:#aaa;">
            <h3 style="color:#ccc;">No slips yet</h3>
            <p>Upload your grocery receipts to get started</p>
        </div>""", unsafe_allow_html=True)
        return

    total = sum(s["total"] for s in slips)
    avg = total / len(slips)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="stat-card card-purple">
            <div class="stat-number">{len(slips)}</div>
            <div class="stat-label">Total Slips</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card card-orange">
            <div class="stat-number">Rs.{total:,.0f}</div>
            <div class="stat-label">Total Spent</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card card-blue">
            <div class="stat-number">Rs.{avg:,.0f}</div>
            <div class="stat-label">Monthly Avg</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    colors = ["#9c27b0", "#2196f3", "#ff9800", "#4caf50", "#e91e63", "#009688"]
    for i, slip in enumerate(reversed(slips)):
        color = colors[i % len(colors)]
        with st.expander(f"{slip['month']} | {slip['store']} | Rs.{slip['total']:,.2f}"):
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"""
            <div class="stat-card" style="background:linear-gradient(135deg,{color},{color}aa)">
                <div class="stat-number" style="font-size:18px;">{slip['store']}</div>
                <div class="stat-label">Store</div>
            </div>""", unsafe_allow_html=True)
            col2.markdown(f"""
            <div class="stat-card card-orange">
                <div class="stat-number">Rs.{slip['total']:,.0f}</div>
                <div class="stat-label">Total</div>
            </div>""", unsafe_allow_html=True)
            col3.markdown(f"""
            <div class="stat-card card-green">
                <div class="stat-number">{slip['item_count']}</div>
                <div class="stat-label">Items</div>
            </div>""", unsafe_allow_html=True)


if st.session_state.token is None:
    show_login()
else:
    show_sidebar()

    nav_col1, nav_col2, nav_col3, nav_col4, nav_spacer = st.columns([1, 1, 1, 1, 3])
    
    with nav_col1:
        if st.button("Dashboard", use_container_width=True, key="nav_top_dash"):
            st.session_state.page = "dashboard"
            st.rerun()
    
    with nav_col2:
        if st.button("Chat", use_container_width=True, key="nav_top_chat"):
            st.session_state.page = "chat"
            st.rerun()
    
    with nav_col3:
        if st.button("Upload", use_container_width=True, key="nav_top_upload"):
            st.session_state.page = "upload"
            st.rerun()
    
    with nav_col4:
        if st.button("Slips", use_container_width=True, key="nav_top_slips"):
            st.session_state.page = "slips"
            st.rerun()

    page = st.session_state.page

    if page == "dashboard":
        show_dashboard()
    elif page == "chat":
        show_chat()
    elif page == "upload":
        show_upload()
    elif page == "slips":
        show_slips()