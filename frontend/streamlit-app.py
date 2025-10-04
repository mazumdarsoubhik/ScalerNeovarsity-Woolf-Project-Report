import time
from datetime import datetime

import requests
import streamlit as st

# ---------- Page setup ----------
st.set_page_config(
    page_title="InsightMesh — Research & Data Agents",
    page_icon="🧠",
    layout="wide"
)

# ---------- Minimal styling ----------
st.markdown("""
<style>
/* Tighter, cleaner layout */
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 980px; }
.stChatMessage { font-size: 0.98rem; }
[data-testid="stHeader"] { background: transparent; }
/* Subtle card look for sidebar panels */
.sidebar .stButton>button, .sidebar .stDownloadButton>button { width: 100%; }
.kpi { padding: 0.6rem 0.8rem; border: 1px solid rgba(0,0,0,0.08); border-radius: 10px; }
.small { font-size: 0.85rem; opacity: 0.8; }
.caption-tight { margin-top: -0.5rem; color: var(--text-color-secondary); font-size: 0.85rem; }
hr { margin: 0.6rem 0 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ---------- App header ----------
c1, c2 = st.columns([1, 3], vertical_alignment="center")
with c1:
    st.markdown("### 🧠 InsightMesh")
with c2:
    st.markdown(
        "<div class='caption-tight'>Agentic Research + Data Agents — MVP chat shell (echo mode)</div>",
        unsafe_allow_html=True
    )

st.markdown("---")

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.markdown(
        "This is the **minimal chat shell** aligned to your project. "
        "It keeps only core UX and state management. No external LLM calls yet."
    )

    def _clear_chat():
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I’ll echo back what you type. The real agents plug in next."}
        ]
        st.session_state.run_stats = {"turns": 0, "started_at": datetime.utcnow().isoformat() + "Z"}

    st.button("🧹 Clear Chat", on_click=_clear_chat)

    st.markdown("### 📊 Run Stats")
    if "run_stats" not in st.session_state:
        st.session_state.run_stats = {"turns": 0, "started_at": datetime.utcnow().isoformat() + "Z"}
    rs = st.session_state.run_stats
    st.markdown(
        f"""
        <div class='kpi'>
          <div><b>Turns</b>: {rs.get('turns', 0)}</div>
          <div class='small'>Started: {rs.get('started_at', '—')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("### ℹ️ About")
    st.markdown(
        "- Clean chat UI\n"
        "- Session history\n"
        "- Echo response (placeholder)\n"
        "- Ready to wire to your Orchestrator/Agents later"
    )

# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I’ll echo back what you type. The real agents plug in next."}
    ]

# ---------- Chat history renderer ----------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# ---------- Echo backend (placeholder) ----------
def fake_backend_echo(user_text: str) -> str:
    """
    Stand-in for orchestrator/agent pipeline.
    Replace this with your actual API call later.
    """
    try:
        response = requests.post(
            "http://localhost:8080/chat/",
            headers={"Content-Type": "application/json"},
            json={"message": user_text},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("response", "⚠️ No response field found.")
        else:
            return f"⚠️ API returned status {response.status_code}: {response.text}"

    except requests.exceptions.RequestException as e:
        return f"🚫 Error reaching backend: {e}"

# ---------- Input box ----------
user_prompt = st.chat_input("Type your question…")
if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    # Assistant "response"
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            reply = fake_backend_echo(user_prompt)
            st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.run_stats["turns"] = st.session_state.run_stats.get("turns", 0) + 1
