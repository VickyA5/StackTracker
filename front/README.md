# StackTracker Frontend (Streamlit)

Minimal multipage Streamlit skeleton for the StackTracker app. UI only; assumes a FastAPI backend handles auth and data processing.

## Structure
- `front/Login.py`: Pre-auth views (Landing, Login, Register) managed via `st.session_state` and buttons.
- `front/pages/Dashboard.py`: Post-auth dashboard with sidebar and upload placeholder.
	- Note: Login/Register are not pages anymore to avoid showing them in the sidebar.
	- `front/streamlit_app.py` exists only as a forwarder to `Login.py` (safe to delete).

## Session State
Tracks `authenticated`, `jwt_token` (placeholder), `current_page`, and a temporary `suppliers` list. Token is stored only in memory for this mock.

## Run Locally

Windows (PowerShell):
```powershell
python -m venv .venv
. .venv\Scripts\Activate
pip install -r front\requirements.txt
streamlit run front\Login.py
```

WSL / Linux:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r front/requirements.txt
streamlit run front/Login.py
```

## Notes
- No real authentication logic or data processing is implemented.
- Page navigation uses `st.switch_page`. Use file-relative paths (e.g., `pages/Dashboard.py`).
- Replace placeholder behaviors once the FastAPI backend endpoints are available.
