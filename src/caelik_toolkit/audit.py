"""Read-only dataset audits. These tools flag issues; they do not clean data."""

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class DataAudit:
    """A snapshot of findings from an input DataFrame."""

    summary: dict[str, int]
    columns: pd.DataFrame
    exact_duplicate_rows: pd.DataFrame
    duplicate_id_rows: pd.DataFrame

    def overview(self) -> str:
        """Short human-readable summary for a terminal or notebook."""
        lines = [f"{key}: {value}" for key, value in self.summary.items()]
        return "\n".join(lines)


def audit_dataframe(data: pd.DataFrame, id_column: str | None = None) -> DataAudit:
    """Inspect dimensions, missing values and duplicates without modifying data.

    `exact_duplicate_rows` includes *all copies* of each exact duplicate;
    `duplicate_id_rows` includes all repeated nonblank IDs, even if their
    remaining fields differ. Neither result is a recommendation to delete.
    """
    if id_column is not None and id_column not in data.columns:
        raise KeyError(f"ID column {id_column!r} is not present.")

    columns = pd.DataFrame({
        "column": [str(column) for column in data.columns],
        "dtype": [str(dtype) for dtype in data.dtypes],
        "missing_count": [int(data[column].isna().sum()) for column in data.columns],
        "missing_percent": [round(float(data[column].isna().mean() * 100), 2)
                            for column in data.columns],
        "distinct_nonmissing": [int(data[column].nunique(dropna=True))
                                for column in data.columns],
    })
    exact = data.loc[data.duplicated(keep=False)].copy()
    if id_column is None:
        repeated = data.iloc[0:0].copy()
    else:
        ids = data[id_column]
        repeated = data.loc[ids.notna() & ids.duplicated(keep=False)].copy()

    summary = {
        "rows": len(data),
        "columns": len(data.columns),
        "exact_duplicate_extra_rows": int(data.duplicated().sum()),
        "rows_in_exact_duplicate_groups": len(exact),
        "rows_with_repeated_ids": len(repeated),
        "missing_cells": int(data.isna().sum().sum()),
    }
    return DataAudit(summary, columns, exact, repeated)
