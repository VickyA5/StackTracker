"""Development settings (local).

Goal: let anyone run the project locally without Supabase credentials by
switching uploaded media storage to the local filesystem.

Production continues using `stacktracker.settings` (Supabase storage).
"""

from .settings import *  # noqa: F401,F403

# Local media is stored on disk.
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Keep media under project root (already defined in base settings), but it's
# useful to make it explicit that this is expected in dev.
MEDIA_ROOT = BASE_DIR / "supplier_files"
