from __future__ import annotations

import streamlit as st

from client import ApiError, BackendClient
from state import clear_error, set_auth, set_error


def _save_auth_from_payload(payload: dict) -> None:
    set_auth(
        access_token=payload.get("access_token"),
        user_id=payload.get("user_id"),
        email=payload.get("email"),
    )


def render_auth_panel(client: BackendClient) -> None:
    st.subheader("Login")
    st.caption("Use your email and password to access meals, dashboard, and chat.")

    auth_mode = st.radio("Auth action", options=["Login", "Register"], horizontal=True)
    with st.form("auth_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Minimum 8 characters")
        submitted = st.form_submit_button(auth_mode)

    if not submitted:
        return
    if not email.strip() or not password.strip():
        st.warning("Email and password are required.")
        return

    try:
        clear_error()
        if auth_mode == "Register":
            payload = client.register(email=email.strip(), password=password)
        else:
            payload = client.login(email=email.strip(), password=password)
        _save_auth_from_payload(payload)
        st.success(f"{auth_mode} successful.")
        st.rerun()
    except ApiError as exc:
        set_error(exc.message)
        st.error(exc.message)
