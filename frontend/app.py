import streamlit as st
import requests
import uuid
import os
import json
from datetime import datetime
import streamlit.components.v1 as components

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Vyoma",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS for ChatGPT-like UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Premium Glassmorphism Dark Theme */
.stApp {
    background: radial-gradient(circle at top left, #0b1120, #040814) !important;
    color: #F8FAFC;
}

/* Premium Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.4) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Sticky Top Container for Sidebar */
[data-testid="stSidebarUserContent"] {
    padding-top: 0 !important;
}
/* Make the first container (holding Title and Button) sticky */
[data-testid="stSidebarUserContent"] > div > div > div:nth-child(1) {
    position: sticky;
    top: 0;
    z-index: 999;
    background-color: rgb(15, 23, 42); /* Matches sidebar bg */
    padding-top: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

/* Remove gradient texts, use clean whites/grays */
.premium-title {
    font-size: 2.2rem;
    font-weight: 600;
    text-align: center;
    color: #FFFFFF;
    margin-bottom: 0.2rem;
}
.premium-subtitle {
    text-align: center;
    color: #9B9B9B;
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 2.5rem;
}

/* Form Container (Global fallback) */
div[data-testid="stForm"] {
    background-color: transparent !important;
    border: none !important;
}

/* Main Action Buttons */
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
    transform: translateY(-2px);
}
[data-testid="stFormSubmitButton"] button p {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

/* Robust Sticky Logout Button */
[data-testid="stSidebarUserContent"] {
    padding-bottom: 80px !important; /* Give space so history doesn't hide behind button */
}
[data-testid="stSidebar"] div:has(> button[kind="primary"]) {
    position: fixed !important;
    bottom: 15px !important;
    left: 15px !important;
    width: 250px !important;
    background-color: #0E1117 !important;
    padding: 10px 0 !important;
    z-index: 99999 !important;
}
[data-testid="stSidebar"] button[kind="primary"] {
    background-color: #262730 !important;
    border: 1px solid #ff4b4b !important;
    color: #ff4b4b !important;
}
[data-testid="stSidebar"] button[kind="primary"]:hover {
    background-color: #ff4b4b !important;
    color: white !important;
}

/* Sidebar History Buttons (Glass Type) */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #ECECEC !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 400 !important;
    transition: all 0.3s ease !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
    transform: translateX(3px) !important;
}

/* Hide annoying "Press Enter to submit form" text that overlaps password eye icon */
div[data-testid="InputInstructions"] {
    display: none !important;
}

/* Primary buttons (like Book Now) */
button[kind="primary"] {
    background: #0B0B2A !important; /* Deep dark purple/black from the image */
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
}
button[kind="primary"]:hover {
    box-shadow: 0 4px 15px rgba(11, 11, 42, 0.4) !important;
    background: #1A1A40 !important;
}

/* Inputs */
.stTextInput > div > div > input, .stNumberInput > div > div > input {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid #E2E8F0 !important;
    color: #0F172A !important;
    border-radius: 8px !important;
    padding: 12px 14px !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.2) !important;
    background-color: #ffffff !important;
}

/* Labels */
.stTextInput label, .stNumberInput label {
    color: #94A3B8 !important;
    font-weight: 500 !important;
}

/* Tabs Segmented Control */
.stTabs [data-baseweb="tab-list"] {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border-radius: 50px !important;
    padding: 6px !important;
    gap: 0 !important;
    display: flex !important;
    justify-content: space-between !important;
}
.stTabs [data-baseweb="tab"] {
    flex: 1 !important;
    justify-content: center !important;
    border-radius: 50px !important;
    padding: 16px 0 !important;
    margin: 0 !important;
    color: #E2E8F0 !important;
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    border: none !important;
    background-color: transparent !important;
    transition: all 0.3s ease !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #FFFFFF !important;
    box-shadow: none !important;
    border-bottom: none !important;
    border: none !important;
}

/* Aeroluxe-style White Flight Cards */
.flight-card {
    background: #ffffff !important;
    border: 1px solid #F1F5F9;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    color: #0F172A;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.flight-card:hover {
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
}
.fc-left {
    flex: 1;
}
.fc-airline {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0F172A;
    text-transform: uppercase;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.fc-airline-span {
    color: #64748B;
    font-size: 0.9rem;
    font-weight: 500;
    text-transform: none;
}
.fc-route-container {
    display: flex;
    align-items: center;
    gap: 20px;
    max-width: 400px;
}
.fc-port {
    text-align: center;
    min-width: 80px;
}
.fc-code {
    font-size: 1.5rem;
    font-weight: 800;
    color: #0F172A;
}
.fc-time {
    font-size: 0.85rem;
    color: #64748B;
    margin-top: 4px;
    white-space: nowrap;
}
.fc-divider {
    flex: 1;
    display: flex;
    align-items: center;
    color: #CBD5E1;
}
.fc-line {
    flex: 1;
    height: 1px;
    background-color: #CBD5E1;
    position: relative;
}
.fc-plane {
    margin: 0 10px;
    font-size: 1.2rem;
    color: #94A3B8;
}
.fc-right {
    text-align: right;
    min-width: 150px;
}
.fc-price {
    font-size: 1.8rem;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 10px;
}
.weather-badge, .prob-badge {
    display: inline-block;
    background: #F1F5F9;
    color: #475569;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-left: 8px;
    margin-bottom: 10px;
}

/* Chat Input Global Base */
[data-testid="stChatInput"] {
    background: transparent !important;
}

/* Chat Messages */
[data-testid="chatAvatarIcon-user"] {
    background-color: #404040 !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background-color: #10A37F !important;
}
/* Popover 3-dot menu tweaks */
div[data-testid="stPopover"] button svg {
    display: none !important; /* Hide the dropdown arrow */
}
div[data-testid="stPopover"] button {
    background: transparent !important;
    border: none !important;
    color: #888 !important;
    box-shadow: none !important;
    padding: 0 !important;
}
div[data-testid="stPopover"] button:hover {
    color: #fff !important;
}
/* Only show popover on hover of the row */
div[data-testid="stPopover"] {
    opacity: 0;
    transition: opacity 0.2s;
}
div[data-testid="stHorizontalBlock"]:hover div[data-testid="stPopover"] {
    opacity: 1;
}
</style>
""", unsafe_allow_html=True)

import re

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"
if "selected_flight" not in st.session_state:
    st.session_state.selected_flight = None
if "order_details" not in st.session_state:
    st.session_state.order_details = None

def login_user(email, password):
    try:
        response = requests.post(f"{API_URL}/login", data={"username": email, "password": password})
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.user_id = data["user_id"]
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error(f"Login failed: Incorrect email or password.")
    except Exception as e:
        st.error(f"Backend error: {e}")

def register_user(username, email, password):
    try:
        response = requests.post(f"{API_URL}/register", json={"username": username, "email": email, "password": password})
        if response.status_code == 200:
            st.success("Registration successful! Please log in.")
        else:
            st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"Backend error: {e}")

# If not logged in, show Auth Page
if not st.session_state.logged_in:
    import os
    import base64
    
    # Load from the new assets folder!
    file_path = os.path.join(os.path.dirname(__file__), "assets", "bg.png")
    with open(file_path, 'rb') as f:
        bg_base64 = base64.b64encode(f.read()).decode()
    bg_image_css = f'url("data:image/png;base64,{bg_base64}")'

    st.markdown(f"""
    <style>
    .stApp {{
        background-color: #0b1120 !important;
        background-image: none !important;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; 
        left: 0;
        width: 55%; 
        height: 100vh;
        background-image: {bg_image_css};
        background-size: cover;
        background-position: center;
        z-index: 0;
    }}
    [data-testid="stAppViewContainer"] {{
        background: transparent !important;
        z-index: 1;
        position: relative;
    }}
    
    @media (max-width: 768px) {{
        .stApp::before {{
            display: none;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    /* Sleek Premium Dark Card for Login Form */
    div[data-testid="stForm"] {
        background: rgba(20, 25, 40, 0.8) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 2.5rem !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4) !important;
    }
    
    .premium-title {
        font-size: 4rem !important;
        font-weight: 800 !important;
        color: #F8FAFC !important;
        text-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        text-align: left !important;
        line-height: 1.1 !important;
        letter-spacing: -1.5px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="height: 4vh;"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([5.8, 3.5, 0.7])
    
    with col2:
        st.markdown('<div class="premium-title">VYOMA</div>', unsafe_allow_html=True)
        st.markdown('<div style="height: 2vh;"></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Secure Login", "Create Account"])
        
        with tab1:
            with st.form("login_form"):
                l_email = st.text_input("Email Address")
                l_password = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Login to Vyoma ✈️", use_container_width=True)
                if submit_login:
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", l_email):
                        st.error("Please enter a valid email address.")
                    elif len(l_password) < 1:
                        st.error("Please enter a password.")
                    else:
                        with st.spinner("Authenticating and securely loading dashboard..."):
                            login_user(l_email, l_password)
                
        with tab2:
            with st.form("register_form"):
                r_username = st.text_input("Username")
                r_email = st.text_input("Email Address")
                r_password = st.text_input("Password", type="password")
                submit_register = st.form_submit_button("Join Vyoma ✈️", use_container_width=True)
                if submit_register:
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", r_email):
                        st.error("Please enter a valid email address.")
                    elif len(r_username) < 3:
                        st.error("Username must be at least 3 characters.")
                    elif len(r_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        register_user(r_username, r_email, r_password)

# If logged in, show ChatGPT-style UI
else:
    import base64
    chk_file_path = os.path.join(os.path.dirname(__file__), "assets", "checkout_bg.png")
    try:
        with open(chk_file_path, 'rb') as f:
            chk_bg_base64 = base64.b64encode(f.read()).decode()
        chk_bg_css = f'url("data:image/png;base64,{chk_bg_base64}")'
    except Exception as e:
        chk_bg_css = "none"

    # SIDEBAR
    with st.sidebar:
        top_container = st.container()
        with top_container:
            st.title("✈️ Vyoma")
            
            if st.button("➕ New Conversation", use_container_width=True):
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.messages = []
                st.rerun()
                
            st.markdown("---")
            st.markdown("### Past Conversations")
        
        try:
            res = requests.get(f"{API_URL}/sessions/{st.session_state.user_id}")
            if res.status_code == 200:
                sessions = res.json()
                
                pinned = [s for s in sessions if s['is_pinned']]
                unpinned = [s for s in sessions if not s['is_pinned']]
                
                def render_session(sess):
                    sid = sess['session_id']
                    menu_key = f"menu_{sid}"
                    
                    if st.session_state.get(menu_key, False):
                        col1, col2, col3, col4 = st.columns([1.5, 3.5, 2.5, 2.5])
                        with col1:
                            if st.button("✖", key=f"close_{sid}", use_container_width=True):
                                st.session_state[menu_key] = False
                                st.rerun()
                        with col2:
                            st.markdown(f"<div style='padding-top:10px; font-size:12px; color:#888;'>Options</div>", unsafe_allow_html=True)
                        with col3:
                            pin_label = "📍" if sess['is_pinned'] else "📌"
                            if st.button(pin_label, key=f"pin_{sid}", use_container_width=True):
                                requests.post(f"{API_URL}/sessions/{sid}/pin")
                                st.session_state[menu_key] = False
                                st.rerun()
                        with col4:
                            if st.button("🗑️", key=f"del_{sid}", use_container_width=True):
                                requests.delete(f"{API_URL}/sessions/{sid}")
                                if st.session_state.session_id == sid:
                                    st.session_state.session_id = str(uuid.uuid4())
                                    st.session_state.messages = []
                                st.session_state[menu_key] = False
                                st.rerun()
                    else:
                        col1, col2 = st.columns([8.5, 1.5])
                        with col1:
                            title = sess['title'][:20] + "..." if len(sess['title']) > 20 else sess['title']
                            if st.button(f"{title}", key=f"btn_{sid}", use_container_width=True):
                                st.session_state.session_id = sid
                                history_res = requests.get(f"{API_URL}/history/{sid}")
                                if history_res.status_code == 200:
                                    st.session_state.messages = []
                                    for pair in history_res.json():
                                        st.session_state.messages.append({"role": "user", "content": pair["intent"]})
                                        if pair["response"]:
                                            st.session_state.messages.append({"role": "assistant", "content": pair["response"]})
                                st.rerun()
                        with col2:
                            if st.button("⋮", key=f"dots_{sid}", use_container_width=True):
                                st.session_state[menu_key] = True
                                st.rerun()
                
                with st.container():
                    st.markdown("<div id='history-scroll-container'></div>", unsafe_allow_html=True)
                    if pinned:
                        st.markdown("<small style='color: #888;'>Pinned</small>", unsafe_allow_html=True)
                        for sess in pinned:
                            render_session(sess)
                        st.markdown("<br>", unsafe_allow_html=True)
                    
                    if unpinned:
                        st.markdown("<small style='color: #888;'>Recent</small>", unsafe_allow_html=True)
                        for sess in unpinned:
                            render_session(sess)
                        
        except Exception as e:
            st.error(f"Could not load history: {str(e)}")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Logout", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.messages = []
            st.rerun()

    def render_chat_message(content, is_history=False, msg_idx=0):
        try:
            import re
            import json
            match = re.search(r'\[\s*\{.*\}\s*\]', content, re.DOTALL)
            if match:
                json_str = match.group(0)
                data_objects = json.loads(json_str)
                if isinstance(data_objects, list) and len(data_objects) > 0 and "type" in data_objects[0]:
                    for i, item in enumerate(data_objects):
                        if item.get('type') == 'weather':
                            st.markdown(f"""
                            <div style='background: rgba(0, 201, 255, 0.1); border: 1px solid #00C9FF; border-radius: 12px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>
                              <h4 style='color: #00C9FF; margin:0;'>🌤️ Weather in {item.get('city', '')} on {item.get('date', '')}</h4>
                              <p style='color: #e0e0e0; margin: 5px 0 0 0; font-size: 1.1rem;'>{item.get('info', '')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        elif item.get('type') == 'flight':
                            weather_html = f"<div class='weather-badge'>🌤️ {item.get('weather_celsius', 'N/A')}</div>" if item.get('weather_celsius') else ""
                            prob_html = f"<div class='prob-badge'>⏱️ {item.get('on_time_probability', 'N/A')}</div>" if item.get('on_time_probability') else ""
                            try:
                                from datetime import datetime as dt
                                f_date = dt.strptime(item.get('date', ''), "%Y-%m-%d").strftime("%d %b")
                            except:
                                f_date = item.get('date', '')
                                
                            # Try to extract route codes
                            route_str = item.get('route', 'DEP to ARR')
                            parts = route_str.split(' to ')
                            dep_code = parts[0][:3].upper() if len(parts) > 0 else "DEP"
                            arr_code = parts[1][:3].upper() if len(parts) > 1 else "ARR"
                            
                            snippet = item.get('snippet', '')
                            dep_time = f_date
                            arr_time = "Arrives"
                            
                            if " - " in snippet:
                                try:
                                    time_part = snippet.split(' • ')[0] # "03:00 PM - 04:20 PM"
                                    times = time_part.split(' - ')
                                    if len(times) == 2:
                                        dep_time = times[0]
                                        arr_time = times[1]
                                except:
                                    pass
                            
                            st.markdown(f"""
                            <div class='flight-card'>
                                <div class='fc-left'>
                                    <div class='fc-airline'>✈️ {item.get('airline', '')} <span class='fc-airline-span'>{item.get('flight_number', 'N/A')} &nbsp;•&nbsp; {route_str}</span></div>
                                    <div class='fc-route-container'>
                                        <div class='fc-port'>
                                            <div class='fc-code'>{dep_code}</div>
                                            <div class='fc-time'>{dep_time}</div>
                                        </div>
                                        <div class='fc-divider'>
                                            <div class='fc-line'></div>
                                            <div class='fc-plane'>✈</div>
                                            <div class='fc-line'></div>
                                        </div>
                                        <div class='fc-port'>
                                            <div class='fc-code'>{arr_code}</div>
                                            <div class='fc-time'>{arr_time}</div>
                                        </div>
                                    </div>
                                </div>
                                <div class='fc-right'>
                                    <div class='fc-price'>{item.get('price', '')}</div>
                                    <div style='color: #64748B; font-size: 0.9rem; margin-bottom: 10px; font-weight: 500;'>{snippet}</div>
                                    <div>{weather_html}{prob_html}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button(f"Booking Now", key=f"book_msg{msg_idx}_idx{i}_{item.get('flight_number', '')}", type="primary"):
                                st.session_state.selected_flight = item
                                st.session_state.current_page = "checkout"
                                st.rerun()
                    return True
        except Exception as e:
            pass
            
        # Fallback to standard markdown
        st.markdown(content, unsafe_allow_html=True)
        return False

    # MAIN UI ROUTING
    if st.session_state.current_page == "chat":
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #02111E, #0A192F) !important;
        }
        
        /* Floating Glass Chat Box */
        [data-testid="stChatInput"] {
            background-color: transparent !important;
            padding-bottom: 20px !important;
        }
        
        /* Kill Streamlit's ugly native gray backgrounds and red borders */
        [data-testid="stChatInput"] [data-baseweb="input"],
        [data-testid="stChatInput"] [data-baseweb="input"]:focus-within {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        /* Our custom pill container */
        .stChatInputContainer {
            background: rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 40px !important;
            box-shadow: 0 15px 45px rgba(0, 0, 0, 0.4) !important;
            overflow: hidden !important; /* Forces inner elements to respect rounded corners */
        }
        
        /* Custom focus glow */
        .stChatInputContainer:focus-within {
            border: 1px solid #64FFDA !important;
            box-shadow: 0 0 25px rgba(100, 255, 218, 0.3) !important;
            background: rgba(255, 255, 255, 0.12) !important;
        }
        
        /* Force text colors */
        .stChatInputContainer textarea {
            font-size: 1.2rem !important;
            font-weight: 500 !important;
            color: #FFFFFF !important;
        }
        .stChatInputContainer textarea:focus {
            outline: none !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        .stChatInputContainer textarea::placeholder {
            color: rgba(255, 255, 255, 0.5) !important;
        }
        
        /* Main Title Gradient */
        h1 {
            background: linear-gradient(90deg, #64FFDA, #00B4DB, #0083B0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            letter-spacing: -0.5px !important;
            margin-bottom: 20px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.title("How can I help you travel today?")
        
        for idx, message in enumerate(st.session_state.messages):
            avatar = "✈️" if message["role"] == "assistant" else "🧑‍💻"
            with st.chat_message(message["role"], avatar=avatar):
                render_chat_message(message["content"], is_history=True, msg_idx=idx)

        prompt = st.chat_input("Ask me anything...")
        final_prompt = prompt

            
        if final_prompt:
            st.session_state.messages.append({"role": "user", "content": final_prompt})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(final_prompt)

            with st.chat_message("assistant", avatar="✈️"):
                with st.spinner("Searching live flights..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/chat",
                            json={
                                "user_id": st.session_state.user_id,
                                "session_id": st.session_state.session_id,
                                "message": final_prompt,
                                "history": st.session_state.messages[:-1]
                            }
                        )
                        if response.status_code == 200:
                            ai_reply = response.json().get("response", "No response received.")
                            render_chat_message(ai_reply, msg_idx=len(st.session_state.messages))
                            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                        else:
                            st.error(f"Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Backend error: {e}")

    elif st.session_state.current_page == "checkout":
        st.markdown("""
        <style>
        /* Simple Light Theme Background */
        .stApp, .main, [data-testid="stAppViewContainer"] {
            background: #F8FAFC !important;
            background-image: none !important;
        }
        [data-testid="stHeader"] {
            background: transparent !important;
        }
        
        /* Force sidebar to be solid dark so it doesn't become white/transparent */
        [data-testid="stSidebar"] {
            background-color: #0b1120 !important;
            border-right: 1px solid #1e293b !important;
        }
        
        /* Default all text to dark for the main page */
        .stMarkdown, p, h1, h2, h3, label, span {
            color: #0F172A !important;
        }
        
        /* Protect the sidebar text (keep it white) */
        [data-testid="stSidebar"] .stMarkdown, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] span {
            color: #F8FAFC !important;
        }
        
        div[data-testid="stForm"] {
            background: #FFFFFF !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 2.5rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        }
        
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input, 
        .stSelectbox > div > div > div {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            color: #0F172A !important;
            border-radius: 6px !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #008cff !important;
            box-shadow: 0 0 0 2px rgba(0,140,255,0.2) !important;
        }
        
        /* Top Header Buttons (Back Button) */
        button[kind="secondary"] {
            background: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 8px 16px !important;
            transition: all 0.2s;
        }
        
        button[kind="secondary"]:hover {
            background: #F1F5F9 !important;
            border-color: #94A3B8 !important;
            color: #0F172A !important;
        }
        
        /* Main Action Button (MMT Blue Gradient) */
        button[kind="primary"] {
            background: linear-gradient(90deg, #008cff 0%, #005bf7 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            padding: 12px 24px !important;
            box-shadow: 0 4px 15px rgba(0, 140, 255, 0.3) !important;
        }
        
        button[kind="primary"]:hover {
            box-shadow: 0 6px 20px rgba(0, 140, 255, 0.5) !important;
            transform: translateY(-1px);
        }
        </style>
        """, unsafe_allow_html=True)
        
        col_title, col_btn = st.columns([8, 2])
        with col_title:
            st.markdown("<h1 style='color: #0F172A; font-weight: 800; margin-bottom: 0; letter-spacing: -0.5px;'>🔒 Secure Checkout</h1>", unsafe_allow_html=True)
        with col_btn:
            if st.button("← Back to Chat"):
                st.session_state.current_page = "chat"
                st.rerun()
            
        flight = st.session_state.selected_flight
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 24px; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-top: 20px;">
            <h3 style="margin-top: 0; color: #0F172A; display: flex; align-items: center; gap: 10px; font-weight: 700;">
                <span style="font-size: 1.5rem;">✈️</span> 
                {flight.get('airline')} 
                <span style="font-size: 1rem; color: #64748B; font-weight: 500;">({flight.get('flight_number')})</span>
            </h3>
            <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 15px;">
                <p style="margin: 0; color: #334155; font-size: 1.1rem;"><strong>Route:</strong> {flight.get('route')}</p>
                <p style="margin: 0; color: #334155; font-size: 1.1rem;"><strong>Date:</strong> {flight.get('date')}</p>
                <div style="background: #F8FAFC; padding: 14px; border-radius: 8px; margin-top: 10px; border: 1px solid #E2E8F0;">
                    <p style="margin: 0; color: #0F172A; font-weight: 600;">{flight.get('snippet')}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Strip ₹ and commas for numeric parsing
        price_str = str(flight.get("price", "5000")).replace("₹", "").replace(",", "").strip()
        try:
            amount = int(float(price_str))
        except:
            amount = 5000
            
        num_passengers = st.number_input("Number of Passengers", min_value=1, max_value=9, value=1)
        total_amount = amount * num_passengers
        st.markdown(f"<h3 style='color: #0F172A; text-align: right; font-weight: 700;'>Total Price: <span style='color: #2563EB;'>₹{total_amount}</span></h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.form("checkout_form"):
            st.markdown("<h3 style='color: #0F172A; margin-top: 0; margin-bottom: 20px; font-weight: 700;'>📋 Passenger Details</h3>", unsafe_allow_html=True)
            passengers_data = []
            for i in range(num_passengers):
                st.markdown(f"<div style='background: #F1F5F9; padding: 8px 12px; border-radius: 6px; margin-bottom: 15px; font-weight: 600; color: #334155;'>👤 Passenger {i+1}</div>", unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
                with col1:
                    name = st.text_input("Full Name", key=f"name_{i}")
                with col2:
                    email = st.text_input("Email Address", key=f"email_{i}")
                with col3:
                    phone = st.text_input("Phone Number", key=f"phone_{i}")
                with col4:
                    age = st.number_input("Age", min_value=0, max_value=120, value=0, key=f"age_{i}")
                
                seat_pref = st.selectbox("Seat Preference", ["No Preference", "Window", "Aisle", "Middle", "Extra Legroom"], key=f"seat_{i}")
                st.markdown("<hr style='border-top: 1px dashed #CBD5E1; margin: 20px 0;'>", unsafe_allow_html=True)
                passengers_data.append({"name": name, "email": email, "phone": phone, "age": age, "seat_preference": seat_pref})
                

            submit_btn = st.form_submit_button("💳 Proceed to Secure Payment", type="primary", use_container_width=True)
            
        if submit_btn:
            if not passengers_data[0]["name"] or not passengers_data[0]["email"]:
                st.error("Please fill in your Name and Email for Passenger 1!")
            else:
                with st.spinner("Initializing Secure Payment..."):
                    try:
                        flight["passengers"] = passengers_data
                        order_req = {
                            "user_id": st.session_state.user_id,
                            "amount": total_amount,
                            "flight_details": flight
                        }
                        res = requests.post(f"{API_URL}/create_order", json=order_req)
                        if res.status_code == 200:
                            st.session_state.order_details = res.json()
                            st.session_state.current_page = "payment"
                            st.rerun()
                        else:
                            st.error(f"Failed to create order: {res.text}")
                    except Exception as e:
                        st.error(f"Error creating order: {e}")
                        
    elif st.session_state.current_page == "payment":
        st.markdown("""
        <style>
        /* Simple Light Theme Background */
        .stApp, .main, [data-testid="stAppViewContainer"] {
            background: #F8FAFC !important;
            background-image: none !important;
        }
        [data-testid="stHeader"] {
            background: transparent !important;
        }
        
        /* Force sidebar to be solid dark so it doesn't become white/transparent */
        [data-testid="stSidebar"] {
            background-color: #0b1120 !important;
            border-right: 1px solid #1e293b !important;
        }
        
        /* Default all text to dark for the main page */
        .stMarkdown, p, h1, h2, h3, label, span {
            color: #0F172A !important;
        }
        
        /* Protect the sidebar text (keep it white) */
        [data-testid="stSidebar"] .stMarkdown, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] span {
            color: #F8FAFC !important;
        }
        
        /* Top Header Buttons (Cancel Button) */
        button[kind="secondary"] {
            background: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 8px 16px !important;
            transition: all 0.2s;
        }
        
        button[kind="secondary"]:hover {
            background: #F1F5F9 !important;
            border-color: #94A3B8 !important;
            color: #0F172A !important;
        }
        
        /* Main Action Button (MMT Blue Gradient) */
        button[kind="primary"] {
            background: linear-gradient(90deg, #008cff 0%, #005bf7 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            padding: 12px 24px !important;
            box-shadow: 0 4px 15px rgba(0, 140, 255, 0.3) !important;
        }
        
        button[kind="primary"]:hover {
            box-shadow: 0 6px 20px rgba(0, 140, 255, 0.5) !important;
            transform: translateY(-1px);
        }
        /* Custom Info/Success boxes for light theme */
        div[data-testid="stInfo"] {
            background-color: #EFF6FF !important;
            color: #1E3A8A !important;
            border: 1px solid #BFDBFE !important;
        }
        div[data-testid="stSuccess"] {
            background-color: #F0FDF4 !important;
            color: #166534 !important;
            border: 1px solid #BBF7D0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col_title, col_btn = st.columns([8, 2])
        with col_title:
            st.markdown("<h1 style='color: #0F172A; font-weight: 800; margin-bottom: 0; letter-spacing: -0.5px;'>💳 Secure Payment Gateway</h1>", unsafe_allow_html=True)
        with col_btn:
            if st.button("← Cancel Payment"):
                st.session_state.current_page = "checkout"
                st.rerun()
                
        st.markdown("<p style='color: #475569; font-size: 1.1rem; margin-top: 5px;'>Please securely complete your payment to confirm your booking.</p>", unsafe_allow_html=True)
        
        order = st.session_state.order_details
        st.info(f"**Order ID**: {order['razorpay_order_id']}")
        st.success(f"**Amount Due**: ₹{order['amount'] / 100}")
        
        flight = st.session_state.selected_flight
        passengers = flight.get("passengers", [])
        passenger_name = passengers[0].get("name", "Passenger") if passengers else "Passenger"
        passenger_email = passengers[0].get("email", "bhaskarmanikanta10@gmail.com") if passengers else "bhaskarmanikanta10@gmail.com"
        passenger_phone = passengers[0].get("phone", "9999999999") if passengers else "9999999999"
        
        st.markdown("<hr style='border-top: 1px solid #E2E8F0; margin: 30px 0;'>", unsafe_allow_html=True)
        
        # Razorpay HTML Component
        components.html(f"""
            <button id="rzp-button1" style="background: linear-gradient(135deg, #0ea5e9, #2563eb); color: white; border: none; padding: 16px 32px; font-size: 1.2rem; font-weight: 700; border-radius: 12px; cursor: pointer; width: 100%; box-shadow: 0 10px 25px rgba(37,99,235,0.3);">💳 Pay Securely ₹{order['amount'] / 100}</button>
            <div id="status" style="margin-top: 15px; color: #475569; font-family: sans-serif; text-align: center; font-weight: 500;"></div>
            <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
            <script>
            var options = {{
                "key": "rzp_test_T5kLvAFhsGG5fv",
                "amount": "{order['amount']}",
                "currency": "INR",
                "name": "Vyoma",
                "description": "Flight Booking",
                "order_id": "{order['razorpay_order_id']}",
                "handler": function (response){{
                    document.getElementById("status").innerHTML = "Payment successful! Verifying with server...";
                    fetch("http://localhost:8000/verify_payment", {{
                        method: "POST",
                        headers: {{
                            "Content-Type": "application/json"
                        }},
                        body: JSON.stringify({{
                            "razorpay_order_id": response.razorpay_order_id,
                            "razorpay_payment_id": response.razorpay_payment_id,
                            "razorpay_signature": response.razorpay_signature,
                            "booking_id": {order['booking_id']}
                        }})
                    }}).then(res => {{
                        if(res.ok) {{
                            document.getElementById("status").innerHTML = "<h3 style='color: #00ff00;'>✅ Payment Verified & Email Sent! You may click 'Confirm Booking' below.</h3>";
                        }} else {{
                            document.getElementById("status").innerHTML = "<h3 style='color: red;'>❌ Verification Failed.</h3>";
                        }}
                    }});
                }},
                "prefill": {{
                    "name": "{passenger_name}",
                    "email": "{passenger_email}",
                    "contact": "{passenger_phone}"
                }},
                "theme": {{
                    "color": "#00C9FF"
                }}
            }};
            var rzp1 = new Razorpay(options);
            document.getElementById('rzp-button1').onclick = function(e){{
                rzp1.open();
                e.preventDefault();
            }}
            </script>
        """, height=600)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=2000, limit=100, key="payment_status_check")
        
        st.info("⏳ Waiting for you to complete the payment above...")
        
        try:
            res = requests.get(f"{API_URL}/booking_status/{order['booking_id']}")
            if res.status_code == 200 and res.json().get("status") == "PAID":
                st.session_state.current_page = "success"
                st.rerun()
        except Exception as e:
            pass
                
    elif st.session_state.current_page == "success":
        st.balloons()
        st.title("🎉 Booking Confirmed!")
        st.success("Your payment was successful and your ticket has been issued.")
        flight = st.session_state.selected_flight
        passengers = flight.get("passengers", [])
        passenger_name = passengers[0].get("name", "Passenger") if passengers else "Passenger"
        passenger_seat = passengers[0].get("seat_preference", "Standard") if passengers else "Standard"
        
        # New Idea: Visual Boarding Pass Preview!
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2F2F2F, #1A1A1A); border-left: 8px solid #00C9FF; border-radius: 12px; padding: 25px; margin: 20px 0; box-shadow: 0 10px 20px rgba(0,0,0,0.5); font-family: sans-serif;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2 style="margin: 0; color: #ECECEC; font-size: 28px;">{flight.get('airline')}</h2>
                <h3 style="margin: 0; color: #00C9FF;">✈️ Flight {flight.get('flight_number')}</h3>
            </div>
            <hr style="border: 0; border-top: 1px dashed #404040; margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                <div>
                    <p style="margin: 0; color: #888; font-size: 12px; text-transform: uppercase;">Passenger</p>
                    <p style="margin: 0; color: #ECECEC; font-size: 18px; font-weight: bold;">{passenger_name}</p>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 0; color: #888; font-size: 12px; text-transform: uppercase;">Date</p>
                    <p style="margin: 0; color: #ECECEC; font-size: 18px; font-weight: bold;">{flight.get('date')}</p>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                <div>
                    <p style="margin: 0; color: #888; font-size: 12px; text-transform: uppercase;">Route</p>
                    <p style="margin: 0; color: #ECECEC; font-size: 16px;">{flight.get('route')}</p>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 0; color: #888; font-size: 12px; text-transform: uppercase;">Time</p>
                    <p style="margin: 0; color: #ECECEC; font-size: 16px;">{flight.get('snippet').split('•')[0]}</p>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <p style="margin: 0; color: #888; font-size: 12px; text-transform: uppercase;">Seat Type</p>
                    <p style="margin: 0; color: #00C9FF; font-size: 16px; font-weight: bold;">{passenger_seat}</p>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 0; color: #888; font-size: 12px; text-transform: uppercase;">Status</p>
                    <p style="margin: 0; color: #10A37F; font-size: 16px; font-weight: bold;">CONFIRMED</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("A confirmation email with your PDF ticket attached has been sent to your address.")
        
        order = st.session_state.order_details
        if order and "booking_id" in order:
            booking_id = order["booking_id"]
            pdf_url = f"{API_URL}/download_ticket/{booking_id}"
            st.markdown(f'''
            <a href="{pdf_url}" download="Ticket.pdf" style="display: inline-block; background-color: #10A37F; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-bottom: 20px;">
                📥 Download PDF Ticket
            </a>
            ''', unsafe_allow_html=True)
        
        if st.button("← Back to Chat"):
            st.session_state.current_page = "chat"
            st.session_state.selected_flight = None
            st.session_state.order_details = None
            st.rerun()
