from __future__ import annotations

from io import BytesIO
from typing import Iterable, Mapping, Any

import pandas as pd


def make_excel_bytes(
    rows: Iterable[Mapping[str, Any]],
    *,
    header_row_index: int = 4,
    columns=("COD. INTERNO", "STOCK", "DESC", "PRECIO"),
) -> bytes:
    """Create an .xlsx in memory with header at a given row.

    This matches the real-world supplier files where the header isn't on row 0.

    `rows` items are expected to include keys: id, stock, name(optional), price(optional).
    """
    pre = [[None for _ in range(len(columns))] for _ in range(header_row_index)]
    header = list(columns)

    data = []
    for r in rows:
        data.append([
            r.get("id"),
            r.get("stock"),
            r.get("name", ""),
            r.get("price", ""),
        ])

    raw = pre + [header] + data
    df = pd.DataFrame(raw)

    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, header=False)
    out.seek(0)
    return out.getvalue()


class DummyFile:
    """A minimal non-seekable file-like object for testing."""

    def __init__(self, data: bytes):
        self._data = data
        self._pos = 0

    def read(self, n: int | None = None) -> bytes:
        if n is None:
            n = len(self._data) - self._pos
        chunk = self._data[self._pos : self._pos + n]
        self._pos += len(chunk)
        return chunk
