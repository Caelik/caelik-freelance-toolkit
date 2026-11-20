"""Client-agnostic grouping, ranking, and reconciliation helpers.

Business meanings (e.g., which returns count or how revenue is defined) belong
in the client's project_rules.py, not here.
"""

from collections.abc import Mapping, Sequence
from math import isclose

import pandas as pd

from .validation import ValidationError, require_columns


def aggregate_metrics(
    data: pd.DataFrame,
    group_columns: str | Sequence[str],
    measures: Mapping[str, tuple[str, str]],
    *,
    allow_missing_groups: bool = False,
) -> pd.DataFrame:
    """Group by named columns using explicit ``{output: (column, agg)}`` rules.

    Do not assume that sum, count, net revenue, etc. is correct for a specific
    client: define those business rules in the project and pass them here.
    Missing group keys are rejected by default (not silently dropped).
    """
    groups = [group_columns] if isinstance(group_columns, str) else list(group_columns)
    if not groups or not measures:
        raise ValueError("Specify at least one grouping column and measure.")
    require_columns(data, [*groups, *(field for field, _ in measures.values())])
    if not allow_missing_groups and data[groups].isna().any().any():
        raise ValidationError("Missing group keys would make this summary ambiguous.")
    valid_aggs = {"sum", "count", "size", "min", "max", "mean", "nunique"}
    for output, (_, agg) in measures.items():
        if agg not in valid_aggs:
            raise ValueError(f"Unsupported aggregation for {output!r}: {agg!r}")
    result = data.groupby(groups, dropna=False, as_index=False).agg(**dict(measures))
    return result.reset_index(drop=True)


def rank_metric(
    data: pd.DataFrame,
    metric_column: str,
    *,
    rank_column: str | None = None,
    descending: bool = True,
    tie_method: str = "min",
) -> pd.DataFrame:
    """Add a competition rank while preserving the original dataset."""
    require_columns(data, [metric_column])
    if tie_method not in {"min", "dense", "max", "first", "average"}:
        raise ValueError("Invalid ranking tie method.")
    values = pd.to_numeric(data[metric_column], errors="raise")
    if values.isna().any():
        raise ValidationError(f"{metric_column} has missing ranking values.")
    result = data.copy()
    name = rank_column or f"{metric_column} Rank"
    if name in result.columns:
        raise ValueError(f"Rank column already exists: {name}")
    ranks = values.rank(method=tie_method, ascending=not descending)
    result[name] = ranks.astype(int) if tie_method != "average" else ranks
    return result


def reconcile_rollups(
    detail: pd.DataFrame,
    rollups: Mapping[str, pd.DataFrame],
    measures: Mapping[str, str],
    *,
    allow_missing: bool = False,
    absolute_tolerance: float = 0.005,
) -> dict[str, float]:
    """Check detail sums equal each independent rollup (e.g. month/product/category).

    ``measures`` maps each detail column to its corresponding rollup column.
    Missing amounts fail unless explicitly permitted for known subtotals.
    Does not correct data or round away unexplained differences.
    """
    if not rollups or not measures:
        raise ValueError("Provide rollups and measures to reconcile.")
    require_columns(detail, measures.keys())
    expected = {}
    for detail_col in measures:
        values = pd.to_numeric(detail[detail_col], errors="raise")
        if not allow_missing and values.isna().any():
            raise ValidationError(f"Detail {detail_col} contains missing values.")
        expected[detail_col] = float(values.sum())
    for label, rollup in rollups.items():
        require_columns(rollup, measures.values())
        for detail_col, summary_col in measures.items():
            values = pd.to_numeric(rollup[summary_col], errors="raise")
            if not allow_missing and values.isna().any():
                raise ValidationError(f"{label}: {summary_col} contains missing values.")
            actual = float(values.sum())
            if not isclose(actual, expected[detail_col], rel_tol=0, abs_tol=absolute_tolerance):
                raise ValidationError(
                    f"{label}: {summary_col} sums to {actual:.4f}; "
                    f"detail {detail_col} sums to {expected[detail_col]:.4f}."
                )
    return expected
