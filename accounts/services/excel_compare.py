import logging
from typing import Optional, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)


def _find_header_row(df_no_header: pd.DataFrame, key_col_name: str) -> Optional[int]:
    """
    Scan the DataFrame (read with header=None) to locate the row index
    that contains the key column name. Matching is case-insensitive and trims spaces.
    Returns the row index or None if not found.
    """
    target = str(key_col_name).strip().lower()
    for i in range(len(df_no_header)):
        row_values = df_no_header.iloc[i].astype(str).str.strip().str.lower().tolist()
        if target in row_values:
            logger.info("Detected header row at index %d for key '%s'", i, key_col_name)
            return i
    logger.warning("Header row not found for key '%s'", key_col_name)
    return None


def read_excel_dynamic(file_obj, key_col_name: str) -> pd.DataFrame:
    """
    Read an Excel file where headers may not be on the first row.
    Detect the header row by searching for the key column name.
    Returns a DataFrame with proper column names and data rows only.
    Raises ValueError if header row cannot be detected.
    """
    # Read entire sheet without headers
    df_raw = pd.read_excel(file_obj, header=None, dtype=str)
    header_row = _find_header_row(df_raw, key_col_name)
    if header_row is None:
        raise ValueError(f"Could not detect header row containing '{key_col_name}'.")

    # Build DataFrame with detected header
    header = df_raw.iloc[header_row].astype(str).str.strip()
    df = df_raw.iloc[header_row + 1:].copy()
    df.columns = header
    # Drop fully empty rows
    df = df.dropna(how='all')
    logger.info("Excel read complete: %d rows, %d columns", len(df), len(df.columns))
    return df


def normalize_columns(
    df: pd.DataFrame,
    product_id: str,
    stock_col: str,
    price_col: Optional[str],
    stock_in_text: Optional[str] = None,
    stock_out_text: Optional[str] = None,
) -> pd.DataFrame:
    """
    Keep only relevant columns and normalize names to 'id', 'stock', 'price'.
    Coerce 'stock' and 'price' to numeric where possible.
    """
    cols = [product_id, stock_col]
    if price_col:
        cols.append(price_col)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns in Excel: {missing}")

    out = df[cols].copy()
    rename_map = {product_id: 'id', stock_col: 'stock'}
    if price_col:
        rename_map[price_col] = 'price'
    out = out.rename(columns=rename_map)

    # Normalize types
    out['id'] = out['id'].astype(str).str.strip()
    # Handle stock values: numeric preferred; if text, map using configured strings
    stock_series = out['stock']
    numeric_stock = pd.to_numeric(stock_series, errors='coerce')
    out['stock'] = numeric_stock

    # Prepare text mapping for non-numeric entries
    if stock_in_text or stock_out_text:
        def map_text_stock(val: Any) -> Optional[float]:
            if pd.isna(val):
                return None
            s = str(val).strip().lower()
            if stock_in_text and s == str(stock_in_text).strip().lower():
                return 1.0
            if stock_out_text and s == str(stock_out_text).strip().lower():
                return 0.0
            return None

        # Fill where numeric is NaN using text mapping
        mask_nan = out['stock'].isna()
        mapped = stock_series[mask_nan].map(map_text_stock)
        out.loc[mask_nan & mapped.notna(), 'stock'] = mapped[mapped.notna()]

    # Default missing stock to 0
    out['stock'] = out['stock'].fillna(0)

    # Deduplicate IDs: aggregate stock and keep last price if present
    if out['id'].duplicated().any():
        logger.info("Duplicate product IDs detected; aggregating by id.")
        agg = {'stock': 'sum'}
        if 'price' in out.columns:
            agg['price'] = 'last'
        out = out.groupby('id', as_index=False).agg(agg)
    if 'price' in out.columns:
        out['price'] = pd.to_numeric(out['price'], errors='coerce')

    # Drop rows with empty id
    out = out[out['id'] != '']
    return out


def compare_stock(old_df: Optional[pd.DataFrame], new_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compare two normalized DataFrames with columns: 'id', 'stock', optional 'price'.
    Returns a dict of DataFrames:
      - removed_or_out_of_stock
      - new_products
      - stock_changes
      - price_changes
    """
    if old_df is None or old_df.empty:
        logger.info("No previous file; treating all rows as new products.")
        return {
            'removed_or_out_of_stock': pd.DataFrame(columns=['id', 'old_stock', 'new_stock']),
            'new_products': new_df.copy(),
            'stock_changes': pd.DataFrame(columns=['id', 'old_stock', 'new_stock']),
            'price_changes': pd.DataFrame(columns=['id', 'old_price', 'new_price']),
        }

    # Index by id for easy comparison
    old_idx = old_df.set_index('id')
    new_idx = new_df.set_index('id')

    # Removed or out of stock: present before but missing now OR stock <= 0
    missing_now = old_idx[~old_idx.index.isin(new_idx.index)].copy()
    missing_now['old_stock'] = missing_now['stock']
    missing_now['new_stock'] = pd.NA

    out_of_stock = new_idx[new_idx['stock'] <= 0].copy()
    out_of_stock = out_of_stock.join(old_idx[['stock']], how='left', rsuffix='_old')
    out_of_stock = out_of_stock.rename(columns={'stock_old': 'old_stock', 'stock': 'new_stock'})
    out_of_stock = out_of_stock.reset_index()[['id', 'old_stock', 'new_stock']]

    removed_or_out = pd.concat([
        missing_now.reset_index()[['id', 'old_stock', 'new_stock']],
        out_of_stock
    ], ignore_index=True)

    # New products: in new but not in old
    new_products = new_idx[~new_idx.index.isin(old_idx.index)].reset_index()

    # Stock changes: id in both and stock changed
    common_ids = old_idx.index.intersection(new_idx.index)
    stock_compare = pd.DataFrame({
        'old_stock': old_idx.loc[common_ids, 'stock'],
        'new_stock': new_idx.loc[common_ids, 'stock'],
    }, index=common_ids).reset_index()
    stock_changes = stock_compare[stock_compare['old_stock'] != stock_compare['new_stock']]

    # Price changes: if both have price
    if 'price' in old_idx.columns and 'price' in new_idx.columns:
        price_compare = pd.DataFrame({
            'old_price': old_idx.loc[common_ids, 'price'],
            'new_price': new_idx.loc[common_ids, 'price'],
        }, index=common_ids).reset_index()
        price_changes = price_compare[price_compare['old_price'] != price_compare['new_price']]
    else:
        price_changes = pd.DataFrame(columns=['id', 'old_price', 'new_price'])

    result = {
        'removed_or_out_of_stock': removed_or_out,
        'new_products': new_products,
        'stock_changes': stock_changes,
        'price_changes': price_changes,
    }
    logger.info(
        "Comparison summary: removed/out=%d, new=%d, stock_changes=%d, price_changes=%d",
        len(result['removed_or_out_of_stock']),
        len(result['new_products']),
        len(result['stock_changes']),
        len(result['price_changes']),
    )
    return result
