"""Simple file I/O for Excel and CSV; never changes the source workbook."""

from collections.abc import Mapping
from pathlib import Path

import pandas as pd


def export_tables(
    tables: Mapping[str, pd.DataFrame],
    target: str | Path,
    *,
    overwrite: bool = False,
    index: bool = False,
) -> Path:
    """Export DataFrames to named Excel sheets (without styling them)."""
    target = Path(target)
    if target.suffix.lower() != ".xlsx":
        raise ValueError("Output must be an .xlsx file.")
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite: {target}")
    if not tables:
        raise ValueError("At least one table is required.")
    for name in tables:
        if not name or len(name) > 31 or any(c in name for c in "[]:*?/\\"):
            raise ValueError(f"Invalid Excel sheet name: {name!r}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(
        target, engine="openpyxl", date_format="mm/dd/yyyy",
        datetime_format="mm/dd/yyyy",
    ) as writer:
        for sheet_name, table in tables.items():
            table.to_excel(writer, sheet_name=sheet_name, index=index)
    return target


def load_table(source: str | Path, *, sheet_name: int | str = 0) -> pd.DataFrame:
    """Read the first/specified Excel sheet or a CSV; don't modify original."""
    source = Path(source)
    if source.suffix.lower() in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(source, sheet_name=sheet_name)
    if source.suffix.lower() == ".csv":
        return pd.read_csv(source, encoding="utf-8-sig")
    raise ValueError(f"Unsupported input file type: {source.suffix}")
