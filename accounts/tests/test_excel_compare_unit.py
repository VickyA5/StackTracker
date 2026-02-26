import pandas as pd

from django.test import SimpleTestCase

from accounts.services.excel_compare import read_excel_dynamic, normalize_columns, compare_stock
from accounts.tests.utils import make_excel_bytes, DummyFile


class ExcelCompareUnitTests(SimpleTestCase):
    def test_header_row_missing_raises(self):
        # Build a workbook where the key header never appears.
        excel_bytes = make_excel_bytes(
            [{"id": "A1", "stock": 1, "name": "Prod A"}],
            columns=("OTRA", "STOCK", "DESC"),
        )
        with self.assertRaises(ValueError):
            read_excel_dynamic(excel_bytes, "COD. INTERNO")

    def test_separator_rows_filtered(self):
        # Separator-like row contains only one non-empty cell across relevant columns.
        df = pd.DataFrame(
            {
                "COD. INTERNO": ["A1", "---", "B2"],
                "STOCK": ["1", "", "2"],
                "DESC": ["P1", "", "P2"],
            }
        )
        out = normalize_columns(
            df,
            product_id="COD. INTERNO",
            stock_col="STOCK",
            price_col=None,
            name_col="DESC",
        )
        # '---' row should go away
        self.assertEqual(set(out["id"].tolist()), {"A1", "B2"})

    def test_stock_text_mapping_in_out(self):
        df = pd.DataFrame(
            {
                "COD. INTERNO": ["A1", "B2"],
                "STOCK": ["EN STOCK", "AGOTADO"],
            }
        )
        out = normalize_columns(
            df,
            product_id="COD. INTERNO",
            stock_col="STOCK",
            price_col=None,
            stock_in_text="EN STOCK",
            stock_out_text="AGOTADO",
        )
        stocks = dict(zip(out["id"], out["stock"]))
        self.assertEqual(stocks["A1"], 1.0)
        self.assertEqual(stocks["B2"], 0.0)

    def test_duplicate_ids_aggregate_stock(self):
        df = pd.DataFrame(
            {
                "COD. INTERNO": ["A1", "A1", "B2"],
                "STOCK": ["1", "2", "3"],
            }
        )
        out = normalize_columns(df, product_id="COD. INTERNO", stock_col="STOCK", price_col=None)
        stocks = dict(zip(out["id"], out["stock"]))
        self.assertEqual(stocks["A1"], 3)
        self.assertEqual(stocks["B2"], 3)

    def test_price_parsing_various_formats(self):
        df = pd.DataFrame(
            {
                "COD. INTERNO": ["A1", "B2", "C3"],
                "STOCK": ["1", "1", "1"],
                "PRECIO": ["$ 1.234,50", "1234.50", "1,234.50"],
            }
        )
        out = normalize_columns(
            df,
            product_id="COD. INTERNO",
            stock_col="STOCK",
            price_col="PRECIO",
        )
        prices = dict(zip(out["id"], out["price"]))
        self.assertAlmostEqual(prices["A1"], 1234.50, places=2)
        self.assertAlmostEqual(prices["B2"], 1234.50, places=2)
        self.assertAlmostEqual(prices["C3"], 1234.50, places=2)

    def test_empty_id_rows_removed(self):
        df = pd.DataFrame({"COD. INTERNO": ["A1", "", None], "STOCK": ["1", "2", "3"]})
        out = normalize_columns(df, product_id="COD. INTERNO", stock_col="STOCK", price_col=None)
        self.assertEqual(out["id"].tolist(), ["A1"])

    def test_compare_removed_vs_out_of_stock(self):
        old = pd.DataFrame({"id": ["A1", "B2"], "stock": [2, 1]})
        new = pd.DataFrame({"id": ["A1"], "stock": [0]})
        comp = compare_stock(old, new)
        # A1 should be out_of_stock, B2 should be removed
        removed_ids = set(comp["removed_or_out_of_stock"]["id"].tolist())
        self.assertEqual(removed_ids, {"A1", "B2"})
        # No new products
        self.assertEqual(len(comp["new_products"]), 0)

    def test_read_excel_dynamic_accepts_non_seekable_stream(self):
        excel_bytes = make_excel_bytes(
            [{"id": "A1", "stock": 1, "name": "Prod A"}],
            columns=("COD. INTERNO", "STOCK", "DESC"),
        )
        stream = DummyFile(excel_bytes)
        df_raw = read_excel_dynamic(stream, "COD. INTERNO")
        self.assertIn("COD. INTERNO", list(df_raw.columns))

    def test_normalize_columns_missing_expected_columns_raises(self):
        df = pd.DataFrame({"COD. INTERNO": ["A1"], "OTRA": ["x"]})
        with self.assertRaises(ValueError) as ctx:
            normalize_columns(
                df,
                product_id="COD. INTERNO",
                stock_col="STOCK",  # missing
                price_col=None,
                name_col="DESC",  # missing
            )
        self.assertIn("Missing expected columns", str(ctx.exception))
