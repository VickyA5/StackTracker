"""
Streamlit app: Pre-auth views managed via session_state (Landing, Login, Register)
Post-auth navigation uses Streamlit's multipage (Dashboard in pages/)
No real authentication logic; placeholders only.
"""
import streamlit as st

# Basic page config for the main (pre-auth) views
st.set_page_config(page_title="StackTracker - Login", page_icon="📦", layout="centered")


def init_session_state():
    """Initialize app-wide session state keys."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "jwt_token" not in st.session_state:
        # Placeholder only. The real token should be set by backend integration.
        st.session_state.jwt_token = None
    if "current_view" not in st.session_state:
        # landing | login | register
        st.session_state.current_view = "landing"
    if "suppliers" not in st.session_state:
        # Placeholder list for sidebar; remove/replace when backend is wired.
        st.session_state.suppliers = ["Supplier A", "Supplier B"]


init_session_state()


def show_landing():
    # Centered title and description
    st.markdown(
        "<h1 style='text-align:center;'>Welcome to StackTracker</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;'>Manage multiple suppliers, upload stock Excel files, and compare changes.</p>",
        unsafe_allow_html=True,
    )

    # Center the buttons using columns
    left_spacer, center_col, right_spacer = st.columns([1, 1, 1])
    with center_col:
        b1, b2 = st.columns([1, 1])
        with b1:
            if st.button("Log in", type="primary"):
                st.session_state.current_view = "login"
                st.rerun()
        with b2:
            if st.button("Register"):
                st.session_state.current_view = "register"
                st.rerun()

    st.divider()

    if st.session_state.authenticated:
        st.success("You're already authenticated.")
        if st.button("Go to Dashboard", type="secondary"):
            st.switch_page("pages/Dashboard.py")


def show_login():
    st.markdown(
        "<h2 style='text-align:center;'>Log in to StackTracker</h2>",
        unsafe_allow_html=True,
    )

    # If already authenticated, offer a quick jump to dashboard
    if st.session_state.authenticated:
        st.success("Already logged in.")
        if st.button("Go to Dashboard", type="primary"):
            st.switch_page("pages/Dashboard.py")

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
            st.success("Login successful. Redirecting to dashboard...")
            st.switch_page("pages/Dashboard.py")

    if st.button("Back to Landing"):
        st.session_state.current_view = "landing"
        st.rerun()

    st.caption("No credentials are stored; this is a UI-only mockup.")


def show_register():
    st.markdown(
        "<h2 style='text-align:center;'>Create your StackTracker account</h2>",
        unsafe_allow_html=True,
    )

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
            st.success("Registration successful. Redirecting to dashboard...")
            st.switch_page("pages/Dashboard.py")

    if st.button("Back to Landing"):
        st.session_state.current_view = "landing"
        st.rerun()

    st.caption("No data is persisted; for structure only.")


# Router for pre-auth views
view = st.session_state.current_view
if view == "landing":
    show_landing()
elif view == "login":
    show_login()
elif view == "register":
    show_register()
else:
    # Fallback to landing for any unknown view value
    st.session_state.current_view = "landing"
    show_landing()