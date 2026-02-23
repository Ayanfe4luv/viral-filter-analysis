# -*- coding: utf-8 -*-
"""
utils/minimal_i18n.py

Startup-cached translation engine. Loads EN/RU JSON files once at app
startup and stores them in st.session_state. All subsequent lookups are
pure in-memory dictionary access (<1ms per lookup).

Lookup order: user_terminology override → translations[lang] → key fallback.
"""

import json
import os
import streamlit as st

# Resolve paths relative to this file so the app works regardless of
# the working directory. Handles Windows cp1252 default encoding safely.
_UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_UTILS_DIR)
_EN_PATH = os.path.join(_ROOT_DIR, "assets", "translations", "en.json")
_RU_PATH = os.path.join(_ROOT_DIR, "assets", "translations", "ru.json")


@st.cache_data
def load_all_translations() -> dict:
    """Load both language files once at app startup.

    encoding='utf-8' is mandatory — on Windows (cp1252 default) this
    prevents UnicodeDecodeError when reading Cyrillic characters.
    Never call this outside of init_translations().
    """
    return {
        "en": json.load(open(_EN_PATH, "r", encoding="utf-8")),
        "ru": json.load(open(_RU_PATH, "r", encoding="utf-8")),
    }


def init_translations() -> None:
    """Call ONCE in app.py startup before any T() calls.

    Populates st.session_state['translations'] and sets the default language.
    Safe to call on every rerun — the if-guard prevents redundant work.
    """
    if "translations" not in st.session_state:
        st.session_state["translations"] = load_all_translations()
    if "language" not in st.session_state:
        st.session_state["language"] = "en"


def T(key: str, **kwargs) -> str:
    """Zero-latency translation lookup.

    Args:
        key: Translation key string.
        **kwargs: Format arguments for placeholder substitution,
                  e.g. T('filter_result', count=42) → "Filtered to 42 sequences"

    Returns:
        Translated and formatted string, or the key itself as fallback.
    """
    lang = st.session_state.get("language", "en")

    # Institutional override: custom Rospotrebnadzor / user-defined terms
    user_terms = st.session_state.get("user_terminology", {})

    # Translation dict (may be empty if init_translations not yet called)
    translations = st.session_state.get("translations", {})
    lang_dict = translations.get(lang) or translations.get("en") or {}

    text = user_terms.get(key) or lang_dict.get(key, key)

    try:
        return text.format(**kwargs) if kwargs else text
    except (KeyError, ValueError):
        # Malformed format string — return raw text rather than crashing
        return text
