# StackTracker
StackTracker is a web application designed to help small businesses monitor daily stock and price changes from multiple suppliers.

The system allows users to configure supplier-specific Excel schemas, upload daily stock files, and automatically detect product additions, removals, and price updates.

StackTracker focuses on simplicity and clarity, providing a clean interface for non-technical users while maintaining a well-structured backend architecture suitable for scaling.

## Basic Authentication (Django)

This repo includes a minimal Django app with:
- Home page offering options to log in or register.
- User registration (username + password) backed by Postgres.
- Basic error handling and logs.

### Requirements
- Python 3.12+
- Docker + Docker Compose

### Quick Start (Docker)

```bash
# Build and start Postgres + Django app
chmod +x entrypoint.sh
docker compose up --build

# App will be available at
# http://localhost:8000/
```

Environment defaults are set in the `Dockerfile` and overridden in `docker-compose.yml`.

### URLs
- `/` Home (if authenticated, shows greeting; otherwise, links to login/register)
- `/login/` Log in
- `/register/` Register
- `/logout/` Logout

### Logging
`LOGGING` is configured to send messages to console using a simple formatter. Levels are adjusted based on `DEBUG`.

