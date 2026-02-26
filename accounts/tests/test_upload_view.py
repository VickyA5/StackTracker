from __future__ import annotations

from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Supplier
from accounts.tests.utils import make_excel_bytes


class _FakeSupabaseService:
    def __init__(self):
        self.uploads = []

    def upload(self, path: str, content: bytes):
        # store only metadata to keep tests light
        self.uploads.append((path, len(content)))
        return path

    def download(self, path: str) -> bytes:  # pragma: no cover
        raise AssertionError("download() should not be called in these view tests")

    def delete(self, path: str) -> None:  # pragma: no cover
        return


@override_settings(
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT="/tmp/stacktracker-test-media",
)
class SupplierUploadViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u1", password="pw")
        self.client.login(username="u1", password="pw")

        self.supplier = Supplier.objects.create(
            owner=self.user,
            name="Proveedor",
            product_id_column="COD. INTERNO",
            stock_column="STOCK",
            product_name_column="DESC",
        )

    def _upload(self, excel_bytes: bytes, filename: str = "stock.xlsx"):
        url = reverse("supplier_upload", args=[self.supplier.id])
        f = SimpleUploadedFile(
            filename,
            excel_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        return self.client.post(url, {"file": f}, follow=True)

    @patch("accounts.views.get_supabase_storage_service", autospec=True)
    def test_first_upload_no_previous_file(self, mock_get_service):
        mock_get_service.return_value = _FakeSupabaseService()
        excel_bytes = make_excel_bytes(
            [{"id": "A1", "stock": 1, "name": "Prod A"}],
            columns=("COD. INTERNO", "STOCK", "DESC"),
        )
        resp = self._upload(excel_bytes, filename="primero.xlsx")
        self.assertEqual(resp.status_code, 200)
        self.supplier.refresh_from_db()
        self.assertTrue(bool(self.supplier.current_file))
        self.assertEqual(self.supplier.last_uploaded_filename, "primero.xlsx")

        # session should have comparison results for this supplier
        session_data = self.client.session.get("comparison_results")
        self.assertEqual(session_data.get("supplier_id"), self.supplier.id)

    @patch("accounts.views.get_supabase_storage_service", autospec=True)
    def test_second_upload_uses_previous_file(self, mock_get_service):
        mock_get_service.return_value = _FakeSupabaseService()

        base_bytes = make_excel_bytes(
            [
                {"id": "A1", "stock": 1, "name": "Prod A"},
                {"id": "B2", "stock": 1, "name": "Prod B"},
            ],
            columns=("COD. INTERNO", "STOCK", "DESC"),
        )
        self._upload(base_bytes, filename="base.xlsx")

        second_bytes = make_excel_bytes(
            [
                {"id": "A1", "stock": 0, "name": "Prod A"},
                {"id": "B2", "stock": 1, "name": "Prod B"},
            ],
            columns=("COD. INTERNO", "STOCK", "DESC"),
        )
        resp = self._upload(second_bytes, filename="segundo.xlsx")
        self.assertEqual(resp.status_code, 200)

        session_data = self.client.session.get("comparison_results")
        self.assertEqual(session_data.get("supplier_id"), self.supplier.id)
        self.assertEqual(session_data.get("new_file_name"), "segundo.xlsx")
        # must not treat all as "new" products
        self.assertEqual(len(session_data.get("new_products") or []), 0)

    @patch("accounts.views.get_supabase_storage_service", autospec=True)
    def test_when_previous_file_corrupt_it_shows_error_and_aborts(self, mock_get_service):
        mock_get_service.return_value = _FakeSupabaseService()

        # First upload valid file
        base_bytes = make_excel_bytes(
            [{"id": "A1", "stock": 1, "name": "Prod A"}],
            columns=("COD. INTERNO", "STOCK", "DESC"),
        )
        self._upload(base_bytes, filename="base.xlsx")

        # Corrupt the stored current_file on disk by overwriting it with junk
        self.supplier.refresh_from_db()
        stored_path = self.supplier.current_file.path
        with open(stored_path, "wb") as fh:
            fh.write(b"NOT AN EXCEL")

        # Upload a new valid Excel; the view should fail while reading previous and not proceed.
        new_bytes = make_excel_bytes(
            [{"id": "A1", "stock": 0, "name": "Prod A"}],
            columns=("COD. INTERNO", "STOCK", "DESC"),
        )
        resp = self._upload(new_bytes, filename="nuevo.xlsx")

        # stays on upload page (200) and contains an error message
        self.assertEqual(resp.status_code, 200)
        msgs = list(resp.context.get("messages"))
        self.assertTrue(any("No se pudo leer el archivo anterior" in str(m) for m in msgs))

        # and must not overwrite the stored file
        with open(stored_path, "rb") as fh:
            self.assertEqual(fh.read(), b"NOT AN EXCEL")

    @patch("accounts.views.get_supabase_storage_service", autospec=True)
    def test_upload_missing_expected_columns_shows_error_and_does_not_overwrite(self, mock_get_service):
        mock_get_service.return_value = _FakeSupabaseService()

        # First upload a valid file so there's something to overwrite.
        base_bytes = make_excel_bytes(
            [
                {"id": "A1", "stock": 1, "name": "Prod A"},
                {"id": "B2", "stock": 1, "name": "Prod B"},
            ],
            columns=("COD. INTERNO", "STOCK", "DESC"),
        )
        self._upload(base_bytes, filename="base.xlsx")
        self.supplier.refresh_from_db()
        stored_path = self.supplier.current_file.path
        with open(stored_path, "rb") as fh:
            old_content = fh.read()

        # Now upload an excel that does NOT contain STOCK column.
        bad_bytes = make_excel_bytes(
            [
                {"id": "A1", "stock": 0, "name": "Prod A"},
            ],
            columns=("COD. INTERNO", "SIN_STOCK", "DESC"),
        )
        resp = self._upload(bad_bytes, filename="sin_columna.xlsx")
        self.assertEqual(resp.status_code, 200)
        msgs = list(resp.context.get("messages"))
        self.assertTrue(any("Missing expected columns" in str(m) for m in msgs))

        # Should not overwrite previous stored file.
        with open(stored_path, "rb") as fh:
            self.assertEqual(fh.read(), old_content)
