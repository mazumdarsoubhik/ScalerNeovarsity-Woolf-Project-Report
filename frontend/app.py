from __future__ import annotations

import streamlit as st

from client import ApiError, BackendClient
from state import clear_auth, init_state, set_auth
from ui_auth import render_auth_panel
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
    access_token=st.session_state["access_token"],
)

if st.session_state["access_token"] and not st.session_state.get("auth_user_id"):
    try:
        me_payload = client.me()
        set_auth(
            access_token=st.session_state["access_token"],
            user_id=me_payload.get("user_id"),
            email=me_payload.get("email"),
        )
    except ApiError:
        clear_auth()
        st.warning("Session expired. Please login again.")
        st.rerun()

if not st.session_state["access_token"]:
    render_auth_panel(client)
    st.stop()

st.caption(
    f"Signed in as {st.session_state.get('auth_email') or 'user'}"
    f" ({(st.session_state.get('auth_user_id') or '')[:8]})"
)

tabs = st.tabs(["Today", "History", "Chat", "Settings"])

with tabs[0]:
    render_today_tab(client)
with tabs[1]:
    render_history_tab(client)
with tabs[2]:
    render_chat_tab(client)
with tabs[3]:
    render_settings_tab(client)
