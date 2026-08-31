from pathlib import Path

import streamlit as st


def _load_css() -> None:

    css_path = (
        Path(__file__).resolve().parent.parent
        / "css"
        / "text_area.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Text area CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def text_area(
    label: str,
    value: str = "",
    height: int | None = None,
    max_chars: int | None = None,
    key: str | None = None,
    help=None,
    on_change=None,
    args=None,
    kwargs=None,
    placeholder: str | None = None,
    disabled: bool = False,
    label_visibility: str = "visible",
) -> str:
    """
    Common text area component.
    """

    _load_css()

    return st.text_area(
        label=label,
        value=value,
        height=height,
        max_chars=max_chars,
        key=key,
        help=help,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        placeholder=placeholder,
        disabled=disabled,
        label_visibility=label_visibility,
    )