from pathlib import Path
from datetime import date

import streamlit as st


def _load_css() -> None:

    css_path = (
        Path(__file__).resolve().parent.parent
        / "css"
        / "date_input.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Date input CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def date_input(
    label: str,
    value=None,
    min_value=None,
    max_value=None,
    key: str | None = None,
    help=None,
    on_change=None,
    args=None,
    kwargs=None,
    disabled: bool = False,
    label_visibility: str = "visible",
    format: str = "YYYY/MM/DD",
):
    """
    Common date input component.
    """

    _load_css()

    return st.date_input(
        label=label,
        value=value,
        min_value=min_value,
        max_value=max_value,
        key=key,
        help=help,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        disabled=disabled,
        label_visibility=label_visibility,
        format=format,
    )