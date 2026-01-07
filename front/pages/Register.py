"""
Registration page (UI only)
- Collects minimal fields; no validation or backend calls here
- On submit: sets session_state placeholders and redirects to Dashboard
"""
import streamlit as st

st.set_page_config(page_title="StackTracker - Register", page_icon="📝", layout="centered")


def init_session_state():
    """Ensure required session_state keys exist."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "jwt_token" not in st.session_state:
        st.session_state.jwt_token = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Register"
    if "suppliers" not in st.session_state:
        st.session_state.suppliers = ["Supplier A", "Supplier B"]


init_session_state()

st.title("Create your StackTracker account")

st.write("This is a UI-only mock. Backend will create the account and return a JWT.")

with st.form("register_form"):
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Register")

    if submitted:
        # Simulate success: backend would return a JWT.
        st.session_state.authenticated = True
        st.session_state.jwt_token = "mock.jwt.token"
        st.session_state.current_page = "Dashboard"
        st.success("Registration successful. Redirecting to dashboard...")
        st.switch_page("pages/Dashboard")

st.caption("No data is persisted; for structure only.")
