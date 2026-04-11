from __future__ import annotations

from datetime import date

import streamlit as st


def init_state() -> None:
    defaults = {
        "backend_url": "http://localhost:8080",
        "user_id": "demo-user",
        "chat_messages": [],
        "history_filters": {
            "start_date": date.today(),
            "end_date": date.today(),
            "limit": 20,
            "offset": 0,
        },
        "last_error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_error(message: str | None) -> None:
    st.session_state["last_error"] = message


def clear_error() -> None:
    st.session_state["last_error"] = None


def reset_chat() -> None:
    st.session_state["chat_messages"] = []
