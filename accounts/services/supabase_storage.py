import io
import logging
import os
from typing import Optional

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


class SupabaseStorageError(Exception):
	"""Custom exception for Supabase storage-related issues."""


class SupabaseStorageService:
	"""HTTP-based wrapper around Supabase Storage operations.

	Evita depender del cliente oficial de Supabase (y sus dependencias de httpx),
	consumiendo directamente la API de Storage vía requests.
	"""

	def __init__(self, base_url: str, api_key: str, bucket: str):
		if not bucket:
			raise ValueError("Supabase bucket name must be provided.")
		if not base_url or not api_key:
			raise ValueError("Supabase base URL and API key must be provided.")
		self._base_url = base_url.rstrip("/")
		self._api_key = api_key
		self._bucket = bucket
		self._session = requests.Session()
		self._session.headers.update({
			"apikey": api_key,
			"Authorization": f"Bearer {api_key}",
		})

	@classmethod
	def from_django_settings(cls) -> "SupabaseStorageService":
		"""Build service instance using Django settings / environment variables.

		Expected configuration (via settings or env vars):
		- SUPABASE_URL or SUPABASE_PROJECT_ID
		- SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY
		- SUPABASE_BUCKET
		"""

		project_id = getattr(settings, "SUPABASE_PROJECT_ID", None) or os.environ.get("SUPABASE_PROJECT_ID")
		url = getattr(settings, "SUPABASE_URL", None) or os.environ.get("SUPABASE_URL")
		if not url and project_id:
			url = f"https://{project_id}.supabase.co"

		service_key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None) or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
		anon_key = getattr(settings, "SUPABASE_ANON_KEY", None) or os.environ.get("SUPABASE_ANON_KEY")
		api_key = service_key or anon_key

		bucket = getattr(settings, "SUPABASE_BUCKET", None) or os.environ.get("SUPABASE_BUCKET")

		if not url or not api_key or not bucket:
			raise SupabaseStorageError(
				"Supabase storage is misconfigured. Ensure SUPABASE_URL/SUPABASE_PROJECT_ID, "
				"SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY, and SUPABASE_BUCKET are set."
			)

		if not service_key:
			logger.warning(
				"Using Supabase anon key for storage operations; consider using SUPABASE_SERVICE_ROLE_KEY "
				"for full bucket access in backend environments."
			)

		logger.info("Supabase HTTP storage client initialised for bucket '%s'", bucket)
		return cls(base_url=url, api_key=api_key, bucket=bucket)

	def _object_url(self, path: str, *, public: bool = False) -> str:
		base = f"{self._base_url}/storage/v1/object"
		if public:
			base = f"{base}/public"
		normalized_path = path.replace("\\", "/").lstrip("/")
		return f"{base}/{self._bucket}/{normalized_path}"

	def upload(self, path: str, content) -> str:
		"""Upload a file-like object or bytes to Supabase storage.

		Returns the stored path (key) on success.
		"""
		if not path:
			raise SupabaseStorageError("A non-empty storage path is required for upload.")

		# Normalise to POSIX-style paths for Supabase
		normalized_path = path.replace("\\", "/").lstrip("/")

		if hasattr(content, "read"):
			try:
				data = content.read()
				if hasattr(content, "seek"):
					content.seek(0)
			except Exception as exc:
				logger.exception("Failed to read upload content for '%s': %s", normalized_path, exc)
				raise SupabaseStorageError("Unable to read upload content.") from exc
		else:
			data = content

		if isinstance(data, str):
			data = data.encode("utf-8")

		if not isinstance(data, (bytes, bytearray, memoryview)):
			raise SupabaseStorageError("Upload content must be bytes, str, or a file-like object.")

		url = self._object_url(normalized_path)
		try:
			resp = self._session.put(url, data=data, headers={"x-upsert": "true"})
			if resp.status_code >= 400:
				logger.error("Supabase upload failed (%s) for '%s': %s", resp.status_code, normalized_path, resp.text)
				raise SupabaseStorageError("Failed to upload file to Supabase.")
			logger.info("Uploaded file to Supabase at '%s'", normalized_path)
			return normalized_path
		except requests.RequestException as exc:  # pragma: no cover - external service
			logger.exception("Error uploading file to Supabase at '%s': %s", normalized_path, exc)
			raise SupabaseStorageError("Failed to upload file to Supabase.") from exc

	def download(self, path: str) -> bytes:
		"""Download a file from Supabase storage and return its bytes."""
		if not path:
			raise SupabaseStorageError("A non-empty storage path is required for download.")
		url = self._object_url(path)
		try:
			resp = self._session.get(url)
			if resp.status_code == 404:
				raise SupabaseStorageError("File not found in Supabase.")
			if resp.status_code >= 400:
				logger.error("Supabase download failed (%s) for '%s': %s", resp.status_code, path, resp.text)
				raise SupabaseStorageError("Failed to download file from Supabase.")
			logger.info("Downloaded file from Supabase at '%s'", path)
			return resp.content
		except requests.RequestException as exc:  # pragma: no cover - external service
			logger.exception("Error downloading file from Supabase at '%s': %s", path, exc)
			raise SupabaseStorageError("Failed to download file from Supabase.") from exc

	def delete(self, path: str) -> None:
		"""Delete a file from Supabase storage. Silently succeeds if it does not exist."""
		if not path:
			return
		normalized_path = path.replace("\\", "/").lstrip("/")
		url = f"{self._base_url}/storage/v1/object/{self._bucket}"
		payload = {"prefixes": [normalized_path]}
		try:
			resp = self._session.delete(url, json=payload)
			if resp.status_code >= 400:
				logger.warning("Supabase delete failed (%s) for '%s': %s", resp.status_code, normalized_path, resp.text)
			else:
				logger.info("Deleted file from Supabase at '%s'", normalized_path)
		except requests.RequestException as exc:  # pragma: no cover - external service
			# Deletion failures are logged but not raised to avoid cascading errors
			logger.warning("Failed to delete file from Supabase at '%s': %s", normalized_path, exc)

	def public_url(self, path: str) -> Optional[str]:
		"""Return a public URL for the stored object, if available.

		Supabase expone objetos públicos via /storage/v1/object/public/BUCKET/PATH
		cuando el bucket es público. Si el bucket es privado, esta URL puede no ser
		accesible directamente.
		"""
		if not path:
			return None
		url = self._object_url(path, public=True)
		logger.info("Generated public URL for Supabase object '%s'", path)
		return url


_cached_service: Optional[SupabaseStorageService] = None


def get_supabase_storage_service() -> SupabaseStorageService:
	"""Return a cached SupabaseStorageService instance.

	This avoids recreating the underlying HTTP client for each storage operation.
	"""
	global _cached_service
	if _cached_service is None:
		_cached_service = SupabaseStorageService.from_django_settings()
	return _cached_service
