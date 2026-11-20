"""Neutral stock alerts; no automatic ordering or demand forecasting."""

import pandas as pd

from .validation import ValidationError, require_columns


def flag_reorder_points(
    data: pd.DataFrame,
    *,
    on_hand_column: str = "On Hand",
    reorder_column: str = "Reorder Point",
    active_column: str | None = None,
    status_column: str = "Stock Decision",
) -> pd.DataFrame:
    """Flag observed stock at/below reorder points; never turn unknown into zero.

    Active values may be booleans or standard yes/no, true/false, active/inactive
    strings. If active_column is omitted, all products are treated as active.
    This flags an *inventory snapshot*, not an order quantity or current balance.
    """
    required = [on_hand_column, reorder_column]
    if active_column:
        required.append(active_column)
    require_columns(data, required)
    if status_column in data.columns:
        raise ValueError(f"Status column already exists: {status_column}")
    result = data.copy()
    on_hand = pd.to_numeric(result[on_hand_column], errors="raise")
    reorder = pd.to_numeric(result[reorder_column], errors="raise")
    if (on_hand.dropna() < 0).any() or (reorder.dropna() < 0).any():
        raise ValidationError("Negative stock or reorder point requires investigation.")
    if reorder.isna().any():
        raise ValidationError("Unknown reorder point; cannot determine stock status.")
    active = pd.Series(True, index=result.index)
    if active_column:
        codes = result[active_column].map(
            lambda x: str(x).strip().lower() if pd.notna(x) else ""
        )
        yes, no = {"yes", "true", "1", "active"}, {"no", "false", "0", "inactive"}
        unknown = ~codes.isin(yes | no)
        if unknown.any():
            raise ValidationError(f"Unknown active-status values: {codes[unknown].unique().tolist()!r}")
        active = codes.isin(yes)
    result[status_column] = "Above reorder point"
    result.loc[on_hand.le(reorder) & active, status_column] = "Review for reorder"
    result.loc[~active, status_column] = "Discontinued — do not reorder"
    result.loc[on_hand.isna() & active, status_column] = "Stock check required"
    return result
