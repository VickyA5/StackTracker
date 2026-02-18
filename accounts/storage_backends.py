import io
import logging
from typing import Optional

from django.core.files.base import File
from django.core.files.storage import Storage

from .services.supabase_storage import (
	SupabaseStorageError,
	get_supabase_storage_service,
)


logger = logging.getLogger(__name__)


class SupabaseDjangoStorage(Storage):
	"""Django Storage backend that stores files in Supabase Storage.

	This backend delegates the actual I/O to SupabaseStorageService and focuses on
	conforming to Django's Storage API.
	"""

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		try:
			self._service = get_supabase_storage_service()
		except SupabaseStorageError as exc:
			logger.exception("Supabase storage initialisation failed: %s", exc)
			raise

	def _open(self, name: str, mode: str = "rb") -> File:  # type: ignore[override]
		try:
			data = self._service.download(name)
		except SupabaseStorageError as exc:
			logger.error("Failed to open '%s' from Supabase: %s", name, exc)
			raise
		buffer = io.BytesIO(data)
		return File(buffer, name)

	def _save(self, name: str, content) -> str:  # type: ignore[override]
		stored_name = self._service.upload(name, content)
		return stored_name

	def delete(self, name: str) -> None:
		try:
			self._service.delete(name)
		except SupabaseStorageError as exc:
			# Deletion errors are non-fatal but logged
			logger.warning("Failed to delete '%s' from Supabase: %s", name, exc)

	def exists(self, name: str) -> bool:
		"""Return False so Django does not try to generate unique names.

		We rely on Supabase's upsert behaviour and the fixed naming scheme
		(user_X/supplier_Y/stock.xlsx) to overwrite files intentionally.
		"""
		return False

	def url(self, name: str) -> str:
		url: Optional[str] = self._service.public_url(name)
		return url or name

	def get_valid_name(self, name: str) -> str:
		# Keep the original name; path is already normalised in the service
		return name

	def get_available_name(self, name: str, max_length: Optional[int] = None) -> str:
		# Always reuse the same name; we intentionally overwrite existing objects
		return name
