from pathlib import Path

import streamlit as st


def _load_css() -> None:

    css_path = (
        Path(__file__).resolve().parent.parent
        / "css"
        / "number_input.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Number input CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def number_input(
    label: str,
    min_value=None,
    max_value=None,
    value=0,
    step=1,
    format=None,
    key=None,
    help=None,
    on_change=None,
    args=None,
    kwargs=None,
    *,
    placeholder=None,
    disabled=False,
    label_visibility="visible",
) -> int | float:

    _load_css()

    return st.number_input(
        label=label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        format=format,
        key=key,
        help=help,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        placeholder=placeholder,
        disabled=disabled,
        label_visibility=label_visibility,
    )