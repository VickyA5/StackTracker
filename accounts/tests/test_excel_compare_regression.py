import pandas as pd
from io import BytesIO

from django.test import SimpleTestCase

from accounts.services.excel_compare import read_excel_dynamic, normalize_columns, compare_stock


def _make_excel_bytes(rows, header_row_index: int = 4):
    """Create an xlsx with a header row at `header_row_index` and data below."""
    # We'll build a DataFrame that includes a few junk rows before the header.
    # read_excel_dynamic reads with header=None and locates the header row by key column name.
    pre = [[None, None, None] for _ in range(header_row_index)]
    header = ["COD. INTERNO", "STOCK", "DESC"]
    data = [[r["id"], r["stock"], r.get("name", "")] for r in rows]

    raw = pre + [header] + data
    df = pd.DataFrame(raw)

    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, header=False)
    out.seek(0)
    return out.getvalue()


class ExcelCompareRegressionTests(SimpleTestCase):
    def test_read_excel_dynamic_accepts_bytes_without_extension(self):
        excel_bytes = _make_excel_bytes([
            {"id": "A1", "stock": 1, "name": "Prod A"},
            {"id": "B2", "stock": 0, "name": "Prod B"},
        ])
        df_raw = read_excel_dynamic(excel_bytes, "COD. INTERNO")
        self.assertIn("COD. INTERNO", list(df_raw.columns))
        df = normalize_columns(df_raw, product_id="COD. INTERNO", stock_col="STOCK", price_col=None, name_col="DESC")
        self.assertEqual(set(df.columns) >= {"id", "stock"}, True)

    def test_third_upload_comparison_does_not_mark_all_as_new(self):
        base_bytes = _make_excel_bytes([
            {"id": "A1", "stock": 1, "name": "Prod A"},
            {"id": "B2", "stock": 1, "name": "Prod B"},
        ])
        second_bytes = _make_excel_bytes([
            {"id": "A1", "stock": 0, "name": "Prod A"},  # changed
            {"id": "B2", "stock": 1, "name": "Prod B"},
        ])
        third_bytes = _make_excel_bytes([
            {"id": "A1", "stock": 0, "name": "Prod A"},
            {"id": "B2", "stock": 0, "name": "Prod B"},  # changed
        ])

        def load(buf):
            df_raw = read_excel_dynamic(buf, "COD. INTERNO")
            return normalize_columns(df_raw, product_id="COD. INTERNO", stock_col="STOCK", price_col=None, name_col="DESC")

        df1 = load(base_bytes)
        df2 = load(second_bytes)
        df3 = load(third_bytes)

        # baseline compare 1->2
        comp12 = compare_stock(df1, df2)
        self.assertEqual(len(comp12["new_products"]), 0)
        self.assertTrue(len(comp12["stock_changes"]) >= 1)

        # compare 2->3 should also have 0 new products
        comp23 = compare_stock(df2, df3)
        self.assertEqual(len(comp23["new_products"]), 0)
        # and at least one stock change
        self.assertTrue(len(comp23["stock_changes"]) >= 1)
