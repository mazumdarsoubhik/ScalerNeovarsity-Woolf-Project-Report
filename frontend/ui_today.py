from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

import streamlit as st

from client import ApiError, BackendClient
from state import clear_error, set_error


def _iso_or_none(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.replace(microsecond=0).isoformat()


def _combine_date_time(selected_date: date, selected_time: time) -> datetime:
    return datetime.combine(selected_date, selected_time)


def _render_macro_card(label: str, macro: dict[str, Any], unit: str) -> None:
    consumed = macro.get("consumed", 0)
    target = macro.get("target", 0)
    remaining = macro.get("remaining", 0)
    st.metric(
        label=label,
        value=f"{consumed:.1f} {unit}",
        delta=f"Remaining {remaining:.1f} {unit} / Target {target:.1f}",
    )


def _render_meal_row(client: BackendClient, meal: dict[str, Any]) -> None:
    meal_id = meal["id"]
    totals = meal.get("totals", {})
    title = meal.get("meal_type") or "meal"
    subtitle = meal.get("original_text", "")
    eaten_at = meal.get("eaten_at", "")
    confidence = meal.get("parse_confidence", 0)

    with st.expander(f"{title} | {eaten_at} | conf {confidence:.2f}"):
        st.write(subtitle)
        st.caption(
            f"Calories: {totals.get('calories', 0):.1f}, "
            f"P: {totals.get('protein', 0):.1f}, C: {totals.get('carbs', 0):.1f}, "
            f"F: {totals.get('fat', 0):.1f}, Fi: {totals.get('fibre', 0):.1f}"
        )

        col1, col2 = st.columns([2, 1])
        with col1:
            with st.form(f"edit_today_{meal_id}"):
                updated_text = st.text_input("Edit text", value=subtitle)
                updated_meal_type = st.text_input("Meal type", value=meal.get("meal_type") or "")
                updated_time = st.text_input("Eaten at (ISO, optional)", value=eaten_at)
                submitted = st.form_submit_button("Save Edit")
                if submitted:
                    if not updated_text.strip():
                        st.warning("Meal text cannot be empty.")
                    else:
                        try:
                            clear_error()
                            client.update_meal(
                                meal_id=meal_id,
                                text=updated_text.strip(),
                                meal_type=updated_meal_type.strip() or None,
                                eaten_at_iso=updated_time.strip() or None,
                            )
                            st.success("Meal updated.")
                            st.rerun()
                        except ApiError as exc:
                            if exc.status_code == 404:
                                st.warning("Meal no longer exists. Refreshing list.")
                                st.rerun()
                            set_error(exc.message)
                            st.error(exc.message)
        with col2:
            if st.button("Delete", key=f"delete_today_{meal_id}", type="secondary"):
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


def render_today_tab(client: BackendClient) -> None:
    st.subheader("Log Meal")
    with st.form("log_meal_form", clear_on_submit=True):
        meal_text = st.text_area("Meal text", placeholder="2 roti, dal, one bowl curd")
        meal_type = st.selectbox(
            "Meal type",
            options=["", "breakfast", "lunch", "snack", "dinner"],
            index=0,
        )
        include_eaten_time = st.checkbox("Set eaten time")
        now = datetime.now()
        eat_cols = st.columns(2)
        with eat_cols[0]:
            eaten_date = st.date_input("Eaten date", value=now.date(), disabled=not include_eaten_time)
        with eat_cols[1]:
            eaten_time = st.time_input("Eaten time", value=now.time().replace(microsecond=0), disabled=not include_eaten_time)
        submitted = st.form_submit_button("Log Meal")

        if submitted:
            if not meal_text.strip():
                st.warning("Meal text is required.")
            else:
                try:
                    clear_error()
                    client.create_meal(
                        text=meal_text.strip(),
                        meal_type=meal_type or None,
                        eaten_at_iso=_iso_or_none(
                            _combine_date_time(eaten_date, eaten_time) if include_eaten_time else None
                        ),
                    )
                    st.success("Meal logged.")
                    st.rerun()
                except ApiError as exc:
                    set_error(exc.message)
                    st.error(exc.message)

    st.divider()

    top_cols = st.columns([1, 1, 1])
    with top_cols[0]:
        selected_day = st.date_input("Dashboard day", value=date.today())
    with top_cols[1]:
        st.write("")
    with top_cols[2]:
        if st.button("Refresh Dashboard", use_container_width=True):
            st.rerun()

    try:
        dashboard = client.get_dashboard_today(day=selected_day.isoformat())
    except ApiError as exc:
        set_error(exc.message)
        st.error(exc.message)
        return

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        _render_macro_card("Calories", dashboard.get("calories", {}), "kcal")
    with c2:
        _render_macro_card("Protein", dashboard.get("protein", {}), "g")
    with c3:
        _render_macro_card("Carbs", dashboard.get("carbs", {}), "g")
    with c4:
        _render_macro_card("Fat", dashboard.get("fat", {}), "g")
    with c5:
        _render_macro_card("Fibre", dashboard.get("fibre", {}), "g")

    st.caption(
        f"Meals: {dashboard.get('meal_count', 0)} | Streak: {dashboard.get('streak_days', 0)} days | Day: {dashboard.get('day')}"
    )

    st.divider()
    st.subheader("Today's Meals")
    try:
        meals_payload = client.get_meal_history(
            start_date=selected_day.isoformat(),
            end_date=selected_day.isoformat(),
            limit=100,
            offset=0,
        )
    except ApiError as exc:
        set_error(exc.message)
        st.error(exc.message)
        return

    items = meals_payload.get("items", [])
    if not items:
        st.info("No meals for this day yet.")
        return
    for meal in items:
        _render_meal_row(client, meal)
