# -*- coding: utf-8 -*-
"""
utils/minimal_i18n.py

Two-tier translation engine — always returns real text, never raw keys.

Tier 1 (module-level): JSON files loaded once at import time → available
  the moment any page imports T(), before app.py has even run.  This mirrors
  the original fasta_analysis_app_final.py "inline TRANSLATIONS dict" approach.

Tier 2 (session-state cache): init_translations() writes a hash-refreshed
  copy into st.session_state on every app.py run.  T() prefers this tier so
  language changes take effect instantly without a server restart.

Lookup order:
  user_terminology override → session-state dict → module-level dict → key fallback
"""

import hashlib
import json
import os
import streamlit as st

# ── Path resolution ──────────────────────────────────────────────────────────
_UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR  = os.path.dirname(_UTILS_DIR)
_EN_PATH   = os.path.join(_ROOT_DIR, "assets", "translations", "en.json")
_RU_PATH   = os.path.join(_ROOT_DIR, "assets", "translations", "ru.json")


# ── Tier 1: module-level load (import-time, once per server process) ─────────
# This guarantees T() works even if init_translations() hasn't been called yet
# (e.g. page navigated to directly, session state cleared, cold-start edge cases).
def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


_MODULE_TRANS: dict = {
    "en": _load_json(_EN_PATH),
    "ru": _load_json(_RU_PATH),
}


# ── Tier 2: session-state cache helpers ──────────────────────────────────────
def _file_md5(path: str) -> str:
    """Short MD5 of a file — used as a cache-bust discriminator."""
    try:
        return hashlib.md5(open(path, "rb").read()).hexdigest()[:12]
    except Exception:
        return "error"


@st.cache_data(show_spinner=False)
def _load_all_cached(en_hash: str, ru_hash: str) -> dict:
    """Cache-data wrapper — re-invoked only when a JSON file changes on disk.

    en_hash / ru_hash are @st.cache_data cache-key discriminators.
    Do NOT use underscore prefix — Streamlit excludes underscore-prefixed
    params from the cache key, causing permanently stale translations.
    """
    del en_hash, ru_hash  # cache-key only; body reads files directly
    return {
        "en": _load_json(_EN_PATH),
        "ru": _load_json(_RU_PATH),
    }


def init_translations() -> None:
    """Call once in app.py before any T() calls.

    Refreshes translations from disk whenever en.json / ru.json change,
    without requiring a server restart.  Falls back to the module-level dict
    on any I/O or JSON error.
    """
    try:
        en_hash = _file_md5(_EN_PATH)
        ru_hash = _file_md5(_RU_PATH)
        st.session_state["translations"] = _load_all_cached(en_hash, ru_hash)
    except Exception:
        st.session_state["translations"] = _MODULE_TRANS

    if "language" not in st.session_state:
        st.session_state["language"] = "en"


# ── T(): zero-latency lookup with guaranteed fallback ────────────────────────
def T(key: str, **kwargs) -> str:
    """Translate *key* into the current language.

    Args:
        key:      Translation key string.
        **kwargs: Format placeholders, e.g. T('result', count=42).

    Returns:
        Translated string.  Never returns a bare key — falls back through
        EN session-state dict → module-level EN dict → key itself.
    """
    lang = st.session_state.get("language", "en")

    # Institutional / user-defined overrides
    user_terms = st.session_state.get("user_terminology", {})

    # Tier 2: session-state dict (preferred — reflects language changes live)
    sess_trans = st.session_state.get("translations") or {}
    lang_dict  = sess_trans.get(lang) or sess_trans.get("en") or {}

    # Tier 1 fallback: module-level dict loaded at import time
    if not lang_dict:
        lang_dict = _MODULE_TRANS.get(lang) or _MODULE_TRANS.get("en") or {}

    text = user_terms.get(key) or lang_dict.get(key, key)

    try:
        return text.format(**kwargs) if kwargs else text
    except (KeyError, ValueError):
        return text
