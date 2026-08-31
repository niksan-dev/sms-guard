from pathlib import Path

import streamlit as st


# =========================================================
# CSS
# =========================================================

_CSS_LOADED = False


def _load_css() -> None:
    global _CSS_LOADED

    if _CSS_LOADED:
        return

    css_path = (
        Path(__file__).resolve().parent.parent
        / "css"
        / "button.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Button CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )

    _CSS_LOADED = True


# =========================================================
# COMMON BUTTON
# =========================================================

def button(
    label: str,
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
    Common application button.

    Parameters
    ----------
    label:
        Button text.

    key:
        Unique Streamlit widget key.

    help:
        Optional tooltip.

    on_click:
        Optional callback function.

        Example:
            on_click=my_function

        Do NOT pass:
            on_click="my_function"

    args:
        Optional callback positional arguments.

    kwargs:
        Optional callback keyword arguments.

    type:
        Streamlit button type:
            primary
            secondary
            tertiary

    icon:
        Optional button icon.

    disabled:
        Disable the button.

    width:
        Modern Streamlit width:
            "stretch"
            "content"

    use_container_width:
        Backward-compatible width option.
    """

    _load_css()

    return st.button(
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