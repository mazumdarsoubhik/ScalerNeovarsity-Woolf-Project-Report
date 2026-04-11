from __future__ import annotations

import streamlit as st

from client import BackendClient
from state import init_state
from ui_chat import render_chat_tab
from ui_history import render_history_tab
from ui_settings import render_settings_tab
from ui_today import render_today_tab


st.set_page_config(
    page_title="NutriFlow",
    page_icon="NF",
    layout="wide",
)

init_state()

st.title("NutriFlow")
st.caption("Low-friction meal logging, dashboard tracking, and nutrition chat.")

last_error = st.session_state.get("last_error")
if last_error:
    st.error(last_error)

client = BackendClient(
    base_url=st.session_state["backend_url"],
    user_id=st.session_state["user_id"],
)

tabs = st.tabs(["Today", "History", "Chat", "Settings"])

with tabs[0]:
    render_today_tab(client)
with tabs[1]:
    render_history_tab(client)
with tabs[2]:
    render_chat_tab(client)
with tabs[3]:
    render_settings_tab()
