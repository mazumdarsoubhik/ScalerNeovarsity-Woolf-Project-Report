from __future__ import annotations

import streamlit as st

from client import ApiError, BackendClient
from state import clear_auth, clear_error, set_error


def render_settings_tab(client: BackendClient) -> None:
    st.subheader("Settings")

    backend_url = st.text_input("Backend URL", value=st.session_state["backend_url"])

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Save", use_container_width=True):
            new_url = backend_url.strip() or "http://localhost:8080"
            if new_url != st.session_state["backend_url"]:
                st.session_state["backend_url"] = new_url
                clear_auth()
                st.success("Backend URL saved. Please login again.")
                st.rerun()
            clear_error()

    with col2:
        if st.button("Test Connection", use_container_width=True):
            test_client = BackendClient(
                base_url=(backend_url.strip() or "http://localhost:8080"),
            )
            try:
                clear_error()
                payload = test_client.health()
                st.success(f"Backend reachable: {payload}")
            except ApiError as exc:
                set_error(exc.message)
                st.error(exc.message)

    with col3:
        if st.button("Logout", use_container_width=True, type="secondary"):
            try:
                clear_error()
                client.logout()
            except ApiError:
                pass
            clear_auth()
            st.success("Logged out.")
            st.rerun()

    st.caption(f"User: {st.session_state.get('auth_email') or '-'}")
    st.caption(f"User ID: {st.session_state.get('auth_user_id') or '-'}")
