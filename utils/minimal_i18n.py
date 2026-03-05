# -*- coding: utf-8 -*-
"""
utils/minimal_i18n.py

Two-tier translation engine — always returns real text, never raw keys.

Supports all six United Nations official languages:
  English (en), Russian (ru), French (fr), Spanish (es),
  Chinese (zh), Arabic (ar).

Tier 1 (module-level): JSON files loaded once at import time → available
  the moment any page imports T(), before app.py has even run.

Tier 2 (session-state cache): init_translations() writes a hash-refreshed
  copy into st.session_state on every app.py run. T() prefers this tier
  so language changes take effect instantly without a server restart.

Lookup order:
  user_terminology override → target language → English fallback → key itself
  (keys missing from a partial translation always display in English, never
  as raw key strings)
"""

import hashlib
import json
import os
import streamlit as st

# ── Path resolution ──────────────────────────────────────────────────────────
_UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR  = os.path.dirname(_UTILS_DIR)
_TRANS_DIR = os.path.join(_ROOT_DIR, "assets", "translations")

# All supported UN official languages
_SUPPORTED_LANGS = ["en", "ru", "fr", "es", "zh", "ar"]
_LANG_PATHS: dict = {
    lang: os.path.join(_TRANS_DIR, f"{lang}.json")
    for lang in _SUPPORTED_LANGS
}


# ── Tier 1: module-level load (import-time, once per server process) ─────────
def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


_MODULE_TRANS: dict = {
    lang: _load_json(path)
    for lang, path in _LANG_PATHS.items()
}


# ── Tier 2: session-state cache helpers ──────────────────────────────────────
def _file_md5(path: str) -> str:
    """Short MD5 of a file — used as a cache-bust discriminator."""
    try:
        return hashlib.md5(open(path, "rb").read()).hexdigest()[:12]
    except Exception:
        return "missing"


@st.cache_data(show_spinner=False)
def _load_all_cached(combined_hash: str) -> dict:
    """Cache-data wrapper — re-invoked only when any translation JSON changes.

    combined_hash is a concatenation of all language file MD5s, acting as
    a single cache-key discriminator.  Body reads files directly from disk.
    """
    del combined_hash  # cache-key only
    return {
        lang: _load_json(path)
        for lang, path in _LANG_PATHS.items()
    }


def init_translations() -> None:
    """Call once in app.py before any T() calls.

    Refreshes translations from disk whenever any language JSON file changes,
    without requiring a server restart.  Falls back to the module-level dict
    on any I/O or JSON error.
    """
    try:
        combined = "".join(_file_md5(p) for p in _LANG_PATHS.values())
        st.session_state["translations"] = _load_all_cached(combined)
    except Exception:
        st.session_state["translations"] = _MODULE_TRANS

    if "language" not in st.session_state:
        st.session_state["language"] = "en"


# ── T(): zero-latency lookup with guaranteed English fallback ─────────────────
def T(key: str, **kwargs) -> str:
    """Translate *key* into the current language.

    Falls back to English when a key is missing from the active language file
    (supporting partial/stub translations for new languages).  Never returns
    a bare key string when an English translation exists.

    Args:
        key:      Translation key string.
        **kwargs: Format placeholders, e.g. T('result', count=42).

    Returns:
        Translated string.  Fallback chain:
          user_terminology override → target language → English → key itself.
    """
    lang = st.session_state.get("language", "en")

    # Institutional / user-defined overrides
    user_terms = st.session_state.get("user_terminology", {})

    # Tier 2: session-state dict (preferred — reflects language changes live)
    sess_trans = st.session_state.get("translations") or {}
    lang_dict = sess_trans.get(lang) or {}
    en_dict   = sess_trans.get("en") or {}

    # Tier 1 fallback: module-level dict loaded at import time
    if not lang_dict:
        lang_dict = _MODULE_TRANS.get(lang) or {}
    if not en_dict:
        en_dict = _MODULE_TRANS.get("en") or {}

    # Key lookup: user override → target language → English → key itself
    text = (
        user_terms.get(key)
        or lang_dict.get(key)
        or en_dict.get(key)
        or key
    )

    try:
        return text.format(**kwargs) if kwargs else text
    except (KeyError, ValueError):
        return text
