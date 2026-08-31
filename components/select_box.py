from pathlib import Path

import streamlit as st


def _load_css() -> None:

    css_path = (
        Path(__file__).resolve().parent.parent
        / "css"
        / "select_box.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Select box CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def select_box(
    label: str,
    options,
    index: int = 0,
    format_func=None,
    key: str | None = None,
    help=None,
    on_change=None,
    args=None,
    kwargs=None,
    disabled: bool = False,
    label_visibility: str = "visible",
):
    """
    Common select box component.
    """

    _load_css()

    # Streamlit expects format_func to be callable.
    # If the caller does not provide one, use the
    # identity function.
    if format_func is None:
        format_func = str

    return st.selectbox(
        label=label,
        options=options,
        index=index,
        format_func=format_func,
        key=key,
        help=help,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        disabled=disabled,
        label_visibility=label_visibility,
    )