from __future__ import annotations

import streamlit as st

from client import ApiError, BackendClient
from state import clear_error, set_error


def render_settings_tab() -> None:
    st.subheader("Settings")

    backend_url = st.text_input("Backend URL", value=st.session_state["backend_url"])
    user_id = st.text_input("User ID", value=st.session_state["user_id"])

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Save", use_container_width=True):
            st.session_state["backend_url"] = backend_url.strip() or "http://localhost:8080"
            st.session_state["user_id"] = user_id.strip() or "demo-user"
            clear_error()
            st.success("Settings saved.")

    with col2:
        if st.button("Test Connection", use_container_width=True):
            test_client = BackendClient(
                base_url=(backend_url.strip() or "http://localhost:8080"),
                user_id=(user_id.strip() or "demo-user"),
            )
            try:
                clear_error()
                payload = test_client.health()
                st.success(f"Backend reachable: {payload}")
            except ApiError as exc:
                set_error(exc.message)
                st.error(exc.message)
