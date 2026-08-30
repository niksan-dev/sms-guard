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
        / "page_header.css"
    )

    if not css_path.exists():
        raise FileNotFoundError(
            f"Page header CSS not found: {css_path}"
        )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.html(
        f"<style>{css}</style>"
    )

    _CSS_LOADED = True


def page_header(
    title: str,
    description: str = "",
    icon: str = "",
) -> None:

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

    description_html = ""

    if safe_description:
        description_html = f"""
            <div class="page-header-subtitle">
                {safe_description}
            </div>
        """

    st.html(
        f"""
        <div class="page-header">

            <div class="page-header-title">
                {safe_icon} {safe_title}
            </div>

            {description_html}

        </div>
        """
    )