# ==========================================
# AI STUDY BUDDY – FINAL FULL VERSION
# ==========================================

import streamlit as st
import pandas as pd
import os
import time
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from pypdf import PdfReader

REMEMBER_FILE = "remember_user.txt"

def remember_user(username):
    with open(REMEMBER_FILE, "w") as f:
        f.write(username)

def forget_user():
    if os.path.exists(REMEMBER_FILE):
        os.remove(REMEMBER_FILE)

def get_remembered_user():
    if os.path.exists(REMEMBER_FILE):
        with open(REMEMBER_FILE, "r") as f:
            return f.read().strip()
    return None

# ------------------------------------------
# PAGE CONFIG
# ------------------------------------------
st.set_page_config(page_title="AI Study Buddy", page_icon="📘", layout="centered")

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📘",
    layout="centered"
)
st.markdown(
    """
    <style>
    :root {
        --primary: #4f46e5;
        --primary-dark: #4338ca;
        --accent: #6366f1;
        --bg-soft: #eef2ff;
        --text-main: #1f2937;
        --text-muted: #6b7280;
    }

    html, body {
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont;
        color: var(--text-main);
    }

    /* Headings */
    h1, h2, h3 {
        font-weight: 700;
        color: var(--primary);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent), var(--primary));
        color: white;
        border-radius: 14px;
        padding: 0.6rem 1.2rem;
        border: none;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        transform: translateY(-1px);
    }

    /* Inputs */
    input {
        border-radius: 12px !important;
        padding: 0.55rem !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-soft);
        padding-top: 1.2rem;
    }

    /* Chat cards */
    .chat-card {
        background: white;
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    }

    .chat-user {
        font-weight: 600;
        margin-bottom: 0.3rem;
    }

    .chat-ai {
        color: var(--text-muted);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------
# LOAD CSS FILE
# ------------------------------------------
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# ------------------------------------------
# SESSION STATE INIT
# ------------------------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "quiz_start" not in st.session_state:
    st.session_state.quiz_start = None

if "theme" not in st.session_state:
    st.session_state.theme = "Light"
    
# ------------------------------------------
# AUTO LOGIN (REMEMBERED USER)
# ------------------------------------------
if st.session_state.current_user is None:
    remembered = get_remembered_user()
    if remembered and remembered in st.session_state.users:
        st.session_state.current_user = remembered
    
# ------------------------------------------
# LOGIN GATE 
# ------------------------------------------
if st.session_state.current_user is None:
    st.markdown(
        """
        <style>
        /* Hide sidebar before login */
        [data-testid="stSidebar"] { display: none; }

        .login-wrapper {
            min-height: 100vh;
            min-height: 100svh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1rem;
            background: linear-gradient(135deg, #eef2ff, #e0e7ff);
        }

        .login-card {
            width: 100%;
            max-width: 420px;
            background: white;
            padding: 2.4rem;
            border-radius: 18px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            text-align: center;
        }

        .login-card h2 {
            color: #4f46e5;
            margin-bottom: 0.4rem;
        }

        .login-card p {
            color: #6b7280;
            margin-bottom: 1.6rem;
        }

        .hint {
            font-size: 0.85rem;
            color: #6b7280;
            margin-top: 0.4rem;
        }

        .forgot {
            font-size: 0.85rem;
            color: #4f46e5;
            margin-top: 1rem;
            cursor: pointer;
        }

        .forgot:hover {
            text-decoration: underline;
        }

        @media (max-width: 480px) {
            .login-card {
                padding: 1.8rem 1.4rem;
            }
        }
        </style>

        <div class="login-wrapper">
            <div class="login-card">
                <h2>📘 AI Study Buddy</h2>
                <p>Sign in to continue learning</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------- Streamlit-safe form (LOGIC ONLY) --------
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        # Password strength (Python-based, reliable)
        strength = "Weak"
        if len(password) >= 8 and any(c.isupper() for c in password) and any(c.isdigit() for c in password):
            strength = "Strong"
        elif len(password) >= 6:
            strength = "Medium"

        st.markdown(f"<div class='hint'>🔒 Password strength: <b>{strength}</b></div>", unsafe_allow_html=True)
       
        remember = st.checkbox("Remember me")
        login = st.form_submit_button("Login")
        signup = st.form_submit_button("Sign Up")

    if login:
        if username in st.session_state.users and \
            st.session_state.users[username]["password"] == password:
        
            st.session_state.current_user = username

        # ✅ REMEMBER USER
        if remember:
            remember_user(username)

        st.rerun()
    else:
        st.error("Invalid username or password")


        if signup:
            if strength == "Weak":
                st.error("Password too weak (min 6 chars)")
            elif username not in st.session_state.users:
                st.session_state.users[username] = {
                    "password": password,
                    "history": []
                }
                st.success("Account created. Please login.")
            else:
                st.error("User already exists")

    st.markdown(
        """
        <div style="text-align:center;">
            <div class="forgot">🧾 Forgot password? (re-register for now)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------- Guest Login (DESKTOP SAFE) --------
    if st.button("📲 Continue as Guest"):
        st.session_state.current_user = "__guest__"
        st.rerun()

    st.stop()


# ------------------------------------------
# APPLY DARK MODE CLASS
# ------------------------------------------
if st.session_state.theme == "Dark":
    st.markdown(
        "<script>document.body.classList.add('dark');</script>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<script>document.body.classList.remove('dark');</script>",
        unsafe_allow_html=True
    )

# ------------------------------------------
# LOAD ENV (.env for local, Secrets for cloud)
# ------------------------------------------
load_dotenv()

# ------------------------------------------
# SIDEBAR (AFTER LOGIN)
# ------------------------------------------
st.sidebar.title("📘 AI Study Buddy")
st.sidebar.success(f"Logged in as {st.session_state.current_user}")

if st.sidebar.button("Logout"):
    forget_user()  # ✅ clear remembered login
    st.session_state.current_user = None
    st.rerun()


# ------------------------------------------
# SIDEBAR – THEME
# ------------------------------------------
if st.session_state.current_user == "__guest__":
    st.sidebar.caption("👤 Guest mode")
else:
    st.sidebar.caption(f"👤 {st.session_state.current_user}")


# ------------------------------------------
# SIDEBAR – MODES
# ------------------------------------------
mode = st.sidebar.radio(
    "📚 Study Modes",
    [
        "📖 Explain Topic",
        "🧠 MCQ Generator",
        "⏱️ Timed Quiz",
        "📝 PDF Summarizer"
    ]
)

# ------------------------------------------
# LOAD DATASETS
# ------------------------------------------
@st.cache_data
def load_all_datasets():
    dataframes = []
    for file in os.listdir("datasets"):
        if file.endswith(".csv"):
            try:
                df = pd.read_csv(
                    os.path.join("datasets", file),
                    sep=None,
                    engine="python",
                    on_bad_lines="skip"
                )
                df.columns = df.columns.str.lower().str.strip()

                if "question" in df.columns and "answer" in df.columns:
                    df = df[["question", "answer"]]
                elif "problem" in df.columns and "solution" in df.columns:
                    df = df.rename(columns={
                        "problem": "question",
                        "solution": "answer"
                    })[["question", "answer"]]
                else:
                    continue

                dataframes.append(df.dropna())
            except Exception:
                continue

    return pd.concat(dataframes, ignore_index=True)

# ------------------------------------------
# LOAD LLaMA 3.1 (CHAT API)
# ------------------------------------------
@st.cache_resource
def load_llama():
    api_token = os.getenv("HF_TOKEN")
    if not api_token:
        st.error("HF_TOKEN not found!")
        st.stop()

    return InferenceClient(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        token=api_token
    )

llama = load_llama()

# ------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------
def get_dataset_context(query):
    dataset = load_all_datasets()
    matches = dataset[
        dataset["question"].str.contains(query, case=False, na=False)
    ]
    return matches.iloc[0]["answer"] if not matches.empty else ""

def generate_with_llama(prompt, max_tokens=400):
    response = llama.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.6,
        top_p=0.9,
    )
    return response.choices[0].message.content

def extract_pdf_text(pdf_file):
    reader = PdfReader(pdf_file)
    return "".join(page.extract_text() or "" for page in reader.pages)

def save_chat(user_msg, ai_msg, mode):
    user = st.session_state.current_user

    # Do not save history for guest
    if user and user != "__guest__":
        st.session_state.users[user]["history"].append({
            "mode": mode,
            "user": user_msg,
            "ai": ai_msg
        })

# ------------------------------------------
# MAIN UI
# ------------------------------------------
st.markdown(
    """
    <h1 style="margin-bottom:0;">AI Study Buddy</h1>
    <p style="color:#6b7280; margin-top:0.2rem;">
        Smart, focused learning — powered by AI
    </p>
    """,
    unsafe_allow_html=True
)

# ==========================================
# EXPLAIN TOPIC
# ==========================================
if mode == "📖 Explain Topic":
    question = st.text_input("Enter a topic or question:")

    if st.button("Explain"):
        context = get_dataset_context(question)

        prompt = f"""
You are an AI Study Buddy.
Explain clearly in simple language.

Question:
{question}

Reference:
{context}
"""
        response = generate_with_llama(prompt)
        st.write(response)
        save_chat(question, response, "Explain Topic")

# ==========================================
# MCQ GENERATOR
# ==========================================
elif mode == "🧠 MCQ Generator":
    topic = st.text_input("Enter topic for quiz:")

    if st.button("Generate MCQs"):
        context = get_dataset_context(topic)

        prompt = f"""
Create 5 MCQs with 4 options.
Clearly mention the correct answer.

Topic:
{topic}

Reference:
{context}
"""
        response = generate_with_llama(prompt, 500)
        st.write(response)
        save_chat(topic, response, "MCQ Generator")

# ==========================================
# TIMED QUIZ
# ==========================================
elif mode == "⏱️ Timed Quiz":
    topic = st.text_input("Quiz topic")
    duration = st.slider("Time (seconds)", 30, 180, 60)

    if st.button("Start Quiz"):
        st.session_state.quiz_start = time.time()

        prompt = f"""
Create 3 MCQs on {topic}.
Include the correct answer after each question.
"""
        quiz = generate_with_llama(prompt, 500)
        st.write(quiz)
        save_chat(topic, quiz, "Timed Quiz")

    if st.session_state.quiz_start:
        elapsed = time.time() - st.session_state.quiz_start
        remaining = int(duration - elapsed)

        if remaining > 0:
            st.warning(f"⏳ Time left: {remaining} seconds")
        else:
            st.error("⏰ Time's up!")
            st.session_state.quiz_start = None

# ==========================================
# PDF SUMMARIZER
# ==========================================
elif mode == "📝 PDF Summarizer":
    pdf = st.file_uploader("Upload a PDF", type=["pdf"])

    if st.button("Summarize") and pdf:
        text = extract_pdf_text(pdf)

        prompt = f"""
Summarize the following into clear,
exam-oriented bullet points:

{text}
"""
        summary = generate_with_llama(prompt, 500)
        st.write(summary)
        save_chat("Uploaded PDF", summary, "PDF Summarizer")

# ==========================================
# CHAT HISTORY
# ==========================================
st.markdown("### 💬 Example")
user = st.session_state.current_user

if user == "__guest__":
    st.info("Guest mode: chat history is not saved.")
elif user:
    for chat in st.session_state.users[user]["history"]:
        st.markdown(
            f"""
            <div class="chat-card">
                <div class="chat-user">🧑 You ({chat['mode']}):</div>
                <div>{chat['user']}</div>

                <div class="chat-ai">
                    <b>🤖 AI:</b><br>{chat['ai']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("Login to view your chat history")


