# StackTracker Frontend (Streamlit)

Minimal multipage Streamlit skeleton for the StackTracker app. UI only; assumes a FastAPI backend handles auth and data processing.

## Structure
- `front/streamlit_app.py`: Landing page with Login/Register.
- `front/pages/Login.py`: Login form; sets session state and redirects.
- `front/pages/Register.py`: Registration form; sets session state and redirects.
- `front/pages/Dashboard.py`: Auth-gated dashboard with sidebar and upload placeholder.

## Session State
Tracks `authenticated`, `jwt_token` (placeholder), `current_page`, and a temporary `suppliers` list. Token is stored only in memory for this mock.

## Run Locally
```bash
python -m venv .venv
. .venv/Scripts/Activate
pip install -r front/requirements.txt
streamlit run front/streamlit_app.py
```

If using WSL, activate your environment in WSL and run the same `streamlit run` command.

## Notes
- No real authentication logic or data processing is implemented.
- Page navigation uses `st.switch_page`. Depending on Streamlit version, you may need to use names or paths like `pages/Login`.
- Replace placeholder behaviors once the FastAPI backend endpoints are available.
