"""Assertions for data quality and reconciliation."""

from collections.abc import Iterable
from math import isclose

import pandas as pd


class ValidationError(ValueError):
    """Raised when data does not meet a stated requirement."""


def require_columns(data: pd.DataFrame, required: Iterable[str]) -> None:
    missing = set(required).difference(data.columns)
    if missing:
        raise ValidationError(f"Required columns missing: {sorted(missing)}")


def require_unique_ids(
    data: pd.DataFrame, id_column: str, *, allow_null: bool = False
) -> None:
    require_columns(data, [id_column])
    ids = data[id_column]
    if not allow_null and ids.isna().any():
        raise ValidationError(f"{id_column} contains blank IDs.")
    if ids.dropna().duplicated().any():
        raise ValidationError(f"{id_column} contains repeated IDs.")


def check_total(
    data: pd.DataFrame,
    value_column: str,
    expected: float,
    *,
    allow_missing: bool = False,
    absolute_tolerance: float = 0.005,
) -> float:
    """Compare a numeric column total with an expected checkpoint.

    Fails on missing values by default. `allow_missing=True` explicitly
    validates a *known subtotal*, not necessarily a complete amount.
    """
    require_columns(data, [value_column])
    series = pd.to_numeric(data[value_column], errors="raise")
    if not allow_missing and series.isna().any():
        raise ValidationError(
            f"{value_column} contains unknown amounts; "
            "use allow_missing=True only for a labeled known subtotal."
        )
    actual = float(series.sum())
    if not isclose(actual, expected, rel_tol=0, abs_tol=absolute_tolerance):
        raise ValidationError(
            f"{value_column} total mismatch: expected {expected:.2f}, got {actual:.2f}."
        )
    return actual
