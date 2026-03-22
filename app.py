import sys
import sqlite3
import pandas as pd
from datetime import datetime

# 1. Compatibility Fix
try:
    import cgi
except ImportError:
    import legacy_cgi as cgi
    sys.modules['cgi'] = cgi

import streamlit as st
import streamlit_authenticator as stauth
from llmlingua import PromptCompressor
from googletrans import Translator

# 2. Database Setup
def init_db():
    conn = sqlite3.connect('legislative_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, name TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history (username TEXT, timestamp TEXT, role TEXT, summary TEXT)')
    conn.commit()
    return conn, c

conn, cursor = init_db()

# 3. Page Config & CSS
st.set_page_config(page_title="AI Legislative Analyzer Dashboard", layout="wide")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%); }
    html, body, [data-testid="stWidgetLabel"] p, h1, h2, h3 { color: #ffffff !important; }
    div[data-baseweb="select"] > div { background-color: #334155 !important; color: #ffffff !important; border-radius: 8px; }
    section[data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.95); }
    section[data-testid="stSidebar"] * { color: #f8fafc !important; }
    .stTextArea textarea { background-color: #1e293b !important; color: #ffffff !important; }
    .stButton>button { border-radius: 20px; background-color: #10b981; color: white; padding: 10px 24px; border: none; }
    .main-title { text-align: center; color: #ffffff; font-size: 3rem; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 4. Auth Logic
users_query = pd.read_sql_query("SELECT * FROM users", conn)
credentials = {'usernames': {row['username']: {'name': row['username'], 'password': row['password']} for _, row in users_query.iterrows()}}
authenticator = stauth.Authenticate(credentials, 'auth_cookie', 'auth_key', cookie_expiry_days=1)

# Check session state properly
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None

# --- LOGIN / REGISTER UI ---
if not st.session_state['authentication_status']:
    st.markdown('<h1 class="main-title">⚖️ AI Legislative Analyzer</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Register", "Login"])
    
    with tab1:
        st.header("Create New Account")
        reg_u, reg_p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Sign Up"):
            if reg_u and reg_p:
                hashed = stauth.Hasher([reg_p]).generate()[0]
                try:
                    cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (reg_u, reg_u, hashed))
                    conn.commit()
                    st.success("Success! Please switch to Login tab.")
                except: st.error("User already exists.")
    
    with tab2:
        name, auth_status, username = authenticator.login(fields={'Form name': 'Login'})
        if auth_status:
            st.session_state['username'] = username
            st.rerun()
        elif auth_status == False: 
            st.error("Incorrect credentials.")

# --- MAIN APP UI ---
else:
    if 'step' not in st.session_state: st.session_state.step = 1
    if 'bill_text' not in st.session_state: st.session_state.bill_text = ""
    
    @st.cache_resource
    def load_compressor():
        return PromptCompressor(model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank", use_llmlingua2=True, device_map="cpu")
    
    compressor, translator = load_compressor(), Translator()

    with st.sidebar:
        st.title("⚖️ Dashboard")
        st.write(f"Logged in: **{st.session_state['username']}**")
        
        # CRITICAL FIX: Only call logout if session is still active
        if st.session_state.get('authentication_status'):
            authenticator.logout('Logout', 'sidebar')
            
        st.markdown("---")
        st.write(f"### Current Step: {st.session_state.step} / 3")
        for i, label in enumerate(["Preferences", "Document Upload", "Analysis Result"], 1):
            st.markdown(f"{'🔵' if st.session_state.step == i else '⚪'} {i}. {label}")

    # STEP 1: PREFERENCES
    if st.session_state.step == 1:
        st.header("Step 1: Set Your Profile")
        role = st.selectbox("Select Your Role:", ["Student", "Farmer", "Business", "Senior Citizen"], index=None)
        lang = st.selectbox("Select Language:", [("English", "en"), ("Hindi", "hi"), ("Marathi", "mr")], format_func=lambda x: x[0], index=None)
        if role and lang:
            st.session_state.persona, st.session_state.lang = role, lang
            if st.button("Next: Upload Document ➡️"):
                st.session_state.step = 2
                st.rerun()

    # STEP 2: UPLOAD
    elif st.session_state.step == 2:
        st.header("Step 2: Provide Legal Document")
        st.subheader("Option A: Paste Text")
        st.session_state.bill_text = st.text_area("Enter content:", height=200, value=st.session_state.bill_text)
        st.subheader("Option B: Upload File")
        uploaded_file = st.file_uploader("Choose a .txt file", type=["txt"])
        if uploaded_file:
            st.session_state.bill_text = uploaded_file.read().decode("utf-8")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"): st.session_state.step = 1; st.rerun()
        with col2:
            if st.button("🚀 Start Analysis"):
                with st.spinner("Analyzing..."):
                    comp = compressor.compress_prompt(st.session_state.bill_text, rate=0.05)
                    summary = translator.translate(comp['compressed_prompt'], dest=st.session_state.lang[1]).text
                    cursor.execute("INSERT INTO history VALUES (?, ?, ?, ?)", (st.session_state['username'], datetime.now().strftime("%Y-%m-%d %H:%M"), st.session_state.persona, summary))
                    conn.commit()
                    st.session_state.results = {"summary": summary, "score": "🟢 Positive", "savings": 95.0}
                    st.session_state.step = 3; st.rerun()

    # STEP 3: RESULTS
    elif st.session_state.step == 3:
        st.header("Step 3: Final Insights")
        res = st.session_state.results
        c1, c2 = st.columns(2)
        c1.metric(f"Impact for {st.session_state.persona}", res['score'])
        c2.metric("Efficiency Gain", f"{res['savings']:.1f}%")
        st.write(res['summary'])
        if st.button("⬅️ Back"): st.session_state.step = 2; st.rerun()