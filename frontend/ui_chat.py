from __future__ import annotations

from datetime import date

import streamlit as st

from client import ApiError, BackendClient
from state import clear_error, reset_chat, set_error


def render_chat_tab(client: BackendClient) -> None:
    st.subheader("Nutrition Chat")

    top_cols = st.columns([2, 1])
    with top_cols[0]:
        context_day = st.date_input("Context day (optional)", value=date.today(), key="chat_context_day")
    with top_cols[1]:
        st.write("")
        if st.button("Clear Chat", use_container_width=True):
            reset_chat()
            st.rerun()

    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_prompt = st.chat_input("Ask for simple meal guidance...")
    if not user_prompt:
        return

    st.session_state["chat_messages"].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                clear_error()
                response = client.chat(
                    message=user_prompt,
                    context_day=context_day.isoformat() if context_day else None,
                )
                reply = response.get("response", "")
                if not reply:
                    reply = "No response from backend."
                st.write(reply)
                st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
            except ApiError as exc:
                set_error(exc.message)
                error_text = f"Error: {exc.message}"
                st.write(error_text)
                st.session_state["chat_messages"].append({"role": "assistant", "content": error_text})
