from pathlib import Path

import streamlit as st


def _load_css() -> None:

    css_path = (
        Path(__file__).resolve().parent.parent
        / "css"
        / "search_box.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Search box CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def search_box(
    label: str = "Search",
    value: str = "",
    placeholder: str = "Search...",
    max_chars: int | None = None,
    key: str | None = None,
    help=None,
    on_change=None,
    args=None,
    kwargs=None,
    disabled: bool = False,
    label_visibility: str = "visible",
) -> str:
    """
    Common search box component.
    """

    _load_css()

    return st.text_input(
        label=label,
        value=value,
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