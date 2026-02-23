import streamlit as st
import json
import os

@st.cache_data
def load_all_translations():
    """Load once at app startup, never touch disk again."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    en_path = os.path.join(base_dir, 'assets', 'translations', 'en.json')
    ru_path = os.path.join(base_dir, 'assets', 'translations', 'ru.json')
    
    with open(en_path, 'r', encoding='utf-8') as f:
        en = json.load(f)
        
    with open(ru_path, 'r', encoding='utf-8') as f:
        ru = json.load(f)
        
    return {'en': en, 'ru': ru}

def init_translations():
    """Call ONCE in app.py startup to initialize session state i18n defaults."""
    if 'translations' not in st.session_state:
        st.session_state['translations'] = load_all_translations()
        st.session_state['language'] = 'en'  # Default language
        
def set_language(lang_code):
    if lang_code in st.session_state['translations']:
        st.session_state['language'] = lang_code
        
def toggle_language():
    current = st.session_state.get('language', 'en')
    new_lang = 'ru' if current == 'en' else 'en'
    st.session_state['language'] = new_lang

def T(key, **kwargs):
    """
    Zero-latency translation lookup (<1ms).
    Returns the translation formatted with kwargs if provided.
    Falls back to the key itself if not found.
    """
    lang = st.session_state.get('language', 'en')
    # Try fetching translated string, fallback to english, then fallback to key
    text = st.session_state.get('translations', {}).get(lang, {}).get(key)
    if text is None:
        text = st.session_state.get('translations', {}).get('en', {}).get(key, key)
        
    return text.format(**kwargs) if kwargs else text
