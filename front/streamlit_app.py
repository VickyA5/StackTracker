"""
Streamlit multipage app: Landing page
- Displays Log in and Register buttons
- Uses st.session_state to track auth and current page
- No real authentication logic; redirects only
"""
import streamlit as st

# Basic page config for the landing page
st.set_page_config(page_title="StackTracker - Landing", page_icon="📦", layout="centered")


def init_session_state():
    """Initialize app-wide session state keys."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "jwt_token" not in st.session_state:
        # Placeholder only. The real token should be set by backend integration.
        st.session_state.jwt_token = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Landing"
    if "suppliers" not in st.session_state:
        # Placeholder list for sidebar; remove/replace when backend is wired.
        st.session_state.suppliers = ["Supplier A", "Supplier B"]


init_session_state()

st.title("Welcome to StackTracker")
st.write("Manage multiple suppliers, upload stock Excel files, and compare changes.")

col1, col2 = st.columns(2)
with col1:
    if st.button("Log in", type="primary"):
        st.session_state.current_page = "Login"
        # Note: st.switch_page works with the page name or path depending on Streamlit version.
        # If this fails, try st.switch_page("pages/Login") or ensure your Streamlit version supports it.
        st.switch_page("pages/Login")

with col2:
    if st.button("Register"):
        st.session_state.current_page = "Register"
        st.switch_page("pages/Register")

st.divider()

if st.session_state.authenticated:
    st.success("You're already authenticated.")
    if st.button("Go to Dashboard", type="secondary"):
        st.session_state.current_page = "Dashboard"
        st.switch_page("pages/Dashboard")
