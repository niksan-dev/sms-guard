from pathlib import Path
import html

import streamlit as st


def _load_css() -> None:
    """
    Load the common sub-header CSS.

    CSS is intentionally loaded on every Streamlit rerun.
    Do not cache this with a module-level flag because
    Streamlit rebuilds the page on every interaction.
    """

    css_path = (
        Path(__file__).resolve().parent.parent
        / "css"
        / "sub_header.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Sub header CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def sub_header(
    title: str,
    description: str = "",
    icon: str = "",
) -> None:
    """
    Render a common section/sub header.

    Parameters
    ----------
    title:
        Section title.

    description:
        Optional description displayed below the title.

    icon:
        Optional emoji/icon displayed before the title.
    """

    _load_css()

    safe_title = html.escape(
        str(title)
    )

    safe_description = html.escape(
        str(description)
    )

    safe_icon = html.escape(
        str(icon)
    )

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    title_html = (
        '<div class="sub-header-title">'
        f'{safe_icon} {safe_title}'
        '</div>'
    )

    # --------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------

    description_html = ""

    if safe_description:
        description_html = (
            '<div class="sub-header-subtitle">'
            f'{safe_description}'
            '</div>'
        )

    # --------------------------------------------------
    # COMPLETE HEADER
    # --------------------------------------------------

    header_html = (
        '<div class="sub-header">'
        f'{title_html}'
        f'{description_html}'
        '</div>'
    )

    st.markdown(
        header_html,
        unsafe_allow_html=True,
    )