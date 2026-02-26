"""Test settings.

These settings allow running the test suite without requiring Postgres.
We switch to SQLite in-memory, which makes tests fast and CI-friendly.

Supabase is not used by tests: view tests mock the service and storage is
forced to local FileSystemStorage via override_settings.
"""

from .settings import *  # noqa: F401,F403

# Use SQLite (in-memory) for tests to avoid needing a Postgres service.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# In tests we don't run collectstatic, so the manifest storage will raise when
# templates reference static assets (e.g. stacktracker.png). Use the standard
# staticfiles storage backend.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Don't use Supabase storage in tests.
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
