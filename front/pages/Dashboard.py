"""
Dashboard page (UI-only skeleton)
- Requires user to be authenticated (session_state)
- Sidebar placeholder for suppliers navigation
- Upload widget for Excel (no processing here)
"""
import streamlit as st

st.set_page_config(page_title="StackTracker - Dashboard", page_icon="📊", layout="wide")


def init_session_state():
    """Ensure required session_state keys exist."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "jwt_token" not in st.session_state:
        st.session_state.jwt_token = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if "suppliers" not in st.session_state:
        st.session_state.suppliers = ["Supplier A", "Supplier B"]


init_session_state()

# Guard: redirect to Login if not authenticated
if not st.session_state.authenticated:
    st.warning("Please log in to access the dashboard.")
    if st.button("Go to Login", type="primary"):
        st.session_state.current_page = "Login"
        st.switch_page("pages/Login")
    st.stop()

# Sidebar: placeholders for suppliers navigation
st.sidebar.header("Suppliers")
selected_supplier = st.sidebar.selectbox(
    "Select a supplier",
    st.session_state.get("suppliers", ["Supplier A", "Supplier B"]),
)

# Optional logout for convenience (UI-only)
if st.sidebar.button("Log out"):
    st.session_state.authenticated = False
    st.session_state.jwt_token = None
    st.session_state.current_page = "Landing"
    st.info("Logged out. Returning to landing page...")
    st.switch_page("streamlit_app")

st.title("Dashboard")
st.write(f"Current supplier: {selected_supplier}")

st.subheader("Upload latest stock (Excel)")
uploaded_file = st.file_uploader("Upload .xlsx file", type=["xlsx"])
if uploaded_file:
    st.info("File received. Backend will process this upload.")

st.subheader("Stock Differences")
st.write(
    "When the backend finishes processing, visual comparisons between the latest and previous stock will appear here."
)
