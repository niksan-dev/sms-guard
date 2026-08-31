from pathlib import Path

import streamlit as st


def _load_css() -> None:

    css_path = (
        Path(__file__).resolve().parent.parent
        / "css"
        / "text_input.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Text input CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def text_input(
    label: str,
    value: str = "",
    max_chars: int | None = None,
    key: str | None = None,
    type: str = "default",
    help_text: str | None = None,
    autocomplete: str | None = None,
    on_change=None,
    args=None,
    kwargs=None,
    placeholder: str | None = None,
    disabled: bool = False,
    label_visibility: str = "visible",
) -> str:
    """
    Common text input component.

    Supports normal and password inputs while
    keeping the application's common styling.
    """

    _load_css()

    return st.text_input(
        label=label,
        value=value,
        max_chars=max_chars,
        key=key,
        type=type,
        help=help_text,
        autocomplete=autocomplete,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        placeholder=placeholder,
        disabled=disabled,
        label_visibility=label_visibility,
    )