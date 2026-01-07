"""
Login page (UI only)
- Collects username and password via a simple form
- On submit: sets session_state placeholders and redirects to Dashboard
- No backend logic here; FastAPI will handle real auth
"""
import streamlit as st

st.set_page_config(page_title="StackTracker - Login", page_icon="🔐", layout="centered")


def init_session_state():
    """Ensure required session_state keys exist."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "jwt_token" not in st.session_state:
        st.session_state.jwt_token = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Login"
    if "suppliers" not in st.session_state:
        st.session_state.suppliers = ["Supplier A", "Supplier B"]


init_session_state()

st.title("Log in to StackTracker")

# If already authenticated, offer a quick jump to dashboard
if st.session_state.authenticated:
    st.success("Already logged in.")
    if st.button("Go to Dashboard", type="primary"):
        st.session_state.current_page = "Dashboard"
        st.switch_page("pages/Dashboard")

st.write("Enter your credentials (UI only; backend will handle authentication).")

with st.form("login_form"):
    username = st.text_input("Email or Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Log in")

    if submitted:
        # Simulate success: backend should verify credentials and return a JWT.
        st.session_state.authenticated = True
        # Placeholder token stored in memory; replace with real backend token later.
        st.session_state.jwt_token = "mock.jwt.token"
        st.session_state.current_page = "Dashboard"
        st.success("Login successful. Redirecting to dashboard...")
        st.switch_page("pages/Dashboard")

st.caption("No credentials are stored; this is a UI-only mockup.")
