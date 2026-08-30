from pathlib import Path
import html

import streamlit as st


_CSS_LOADED = False


def _load_css() -> None:
    global _CSS_LOADED

    if _CSS_LOADED:
        return

    css_path = (
        Path(__file__).resolve().parent.parent
        / "css"
        / "sub_header.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Section header CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.html(
        f"<style>{css}</style>"
    )

    _CSS_LOADED = True


def sub_header(
    title: str,
    icon: str = "",
) -> None:
    """
    Render a common section header.

    Parameters
    ----------
    title:
        Section title.

    icon:
        Optional emoji/icon displayed before the title.
    """

    _load_css()

    safe_title = html.escape(
        str(title)
    )

    safe_icon = html.escape(
        str(icon)
    )

    st.html(
        f"""
        <div class="section-header">

            <div class="section-header-title">
                {safe_icon} {safe_title}
            </div>

        </div>
        """
    )