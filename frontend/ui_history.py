from __future__ import annotations

from datetime import date
from typing import Any

import streamlit as st

from client import ApiError, BackendClient
from state import clear_error, set_error


def _render_history_row(client: BackendClient, meal: dict[str, Any]) -> None:
    meal_id = meal["id"]
    totals = meal.get("totals", {})
    with st.expander(f"{meal.get('eaten_at')} | {meal.get('meal_type') or 'meal'} | {meal_id[:8]}"):
        st.write(meal.get("original_text", ""))
        st.caption(
            f"Conf: {meal.get('parse_confidence', 0):.2f} | "
            f"Calories {totals.get('calories', 0):.1f} | "
            f"P {totals.get('protein', 0):.1f} C {totals.get('carbs', 0):.1f} "
            f"F {totals.get('fat', 0):.1f} Fi {totals.get('fibre', 0):.1f}"
        )

        cols = st.columns([2, 1])
        with cols[0]:
            with st.form(f"history_edit_{meal_id}"):
                edited_text = st.text_input("Edit text", value=meal.get("original_text", ""))
                edited_type = st.text_input("Meal type", value=meal.get("meal_type") or "")
                edited_eaten = st.text_input("Eaten at (ISO, optional)", value=meal.get("eaten_at", ""))
                submit = st.form_submit_button("Save Edit")
                if submit:
                    if not edited_text.strip():
                        st.warning("Meal text cannot be empty.")
                    else:
                        try:
                            clear_error()
                            client.update_meal(
                                meal_id=meal_id,
                                text=edited_text.strip(),
                                meal_type=edited_type.strip() or None,
                                eaten_at_iso=edited_eaten.strip() or None,
                            )
                            st.success("Meal updated.")
                            st.rerun()
                        except ApiError as exc:
                            if exc.status_code == 404:
                                st.warning("Meal no longer exists. Refreshing list.")
                                st.rerun()
                            set_error(exc.message)
                            st.error(exc.message)
        with cols[1]:
            if st.button("Delete", key=f"history_delete_{meal_id}", type="secondary"):
                try:
                    clear_error()
                    client.delete_meal(meal_id)
                    st.success("Meal deleted.")
                    st.rerun()
                except ApiError as exc:
                    if exc.status_code == 404:
                        st.warning("Meal already removed. Refreshing list.")
                        st.rerun()
                    set_error(exc.message)
                    st.error(exc.message)


def render_history_tab(client: BackendClient) -> None:
    st.subheader("Meal History")

    filters = st.session_state["history_filters"]
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        start_date = st.date_input("Start Date", value=filters["start_date"], key="history_start_date")
    with col2:
        end_date = st.date_input("End Date", value=filters["end_date"], key="history_end_date")
    with col3:
        limit = st.number_input("Limit", min_value=1, max_value=100, value=int(filters["limit"]), step=1)
    with col4:
        st.write("")
        st.write("")
        apply_filters = st.button("Apply Filter", use_container_width=True)

    if apply_filters:
        if start_date > end_date:
            set_error("Invalid date range: start_date must be <= end_date.")
            st.error(st.session_state["last_error"])
            return
        filters["start_date"] = start_date
        filters["end_date"] = end_date
        filters["limit"] = int(limit)
        filters["offset"] = 0
        clear_error()

    try:
        payload = client.get_meal_history(
            start_date=filters["start_date"].isoformat() if isinstance(filters["start_date"], date) else None,
            end_date=filters["end_date"].isoformat() if isinstance(filters["end_date"], date) else None,
            limit=int(filters["limit"]),
            offset=int(filters["offset"]),
        )
    except ApiError as exc:
        set_error(exc.message)
        st.error(exc.message)
        return

    total = payload.get("total", 0)
    items = payload.get("items", [])
    st.caption(f"Total records: {total} | Offset: {filters['offset']} | Limit: {filters['limit']}")

    nav1, nav2, nav3 = st.columns([1, 1, 3])
    with nav1:
        if st.button("Previous", use_container_width=True, disabled=filters["offset"] <= 0):
            filters["offset"] = max(0, int(filters["offset"]) - int(filters["limit"]))
            st.rerun()
    with nav2:
        if st.button(
            "Next",
            use_container_width=True,
            disabled=(int(filters["offset"]) + int(filters["limit"]) >= int(total)),
        ):
            filters["offset"] = int(filters["offset"]) + int(filters["limit"])
            st.rerun()
    with nav3:
        st.write("")

    if not items:
        st.info("No meals found for selected filters.")
        return

    for meal in items:
        _render_history_row(client, meal)
