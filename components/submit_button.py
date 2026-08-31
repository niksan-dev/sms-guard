from pathlib import Path

import streamlit as st


def _load_css() -> None:
    css_path = (
        Path(__file__).resolve().parent.parent
        / "css"
        / "submit_button.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Submit button CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def submit_button(
    label: str = "Submit",
    *,
    key: str | None = None,
    help: str | None = None,
    on_click=None,
    args=None,
    kwargs=None,
    type: str = "secondary",
    icon: str | None = None,
    disabled: bool = False,
    use_container_width: bool | None = None,
    width: str | None = None,
) -> bool:
    """
    Common form submit button.

    Designed to preserve the native Streamlit
    st.form_submit_button() API while applying
    the application's common styling.
    """

    _load_css()

    return st.form_submit_button(
        label=label,
        key=key,
        help=help,
        on_click=on_click,
        args=args,
        kwargs=kwargs,
        type=type,
        icon=icon,
        disabled=disabled,
        use_container_width=use_container_width,
        width=width,
    )