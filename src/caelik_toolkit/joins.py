"""Safe joins to product masters, customer lookups, and other reference tables."""

from collections.abc import Sequence

import pandas as pd

from .validation import ValidationError, require_columns, require_unique_ids


def join_lookup(
    data: pd.DataFrame,
    lookup: pd.DataFrame,
    *,
    key: str,
    lookup_columns: Sequence[str] | None = None,
    require_match: bool = True,
) -> pd.DataFrame:
    """Many-to-one left join with duplicate and unmatched-key safeguards.

    All original rows remain in their input order. The lookup must have unique,
    nonblank keys. Overlapping non-key names cause an error rather than silent
    ``_x``/``_y`` columns. With ``require_match=False`` unmatched lookups stay
    missing for explicit exception handling by the client project.
    """
    require_columns(data, [key])
    require_columns(lookup, [key])
    columns = list(lookup.columns) if lookup_columns is None else [key, *lookup_columns]
    columns = list(dict.fromkeys(columns))
    require_columns(lookup, columns)
    require_unique_ids(lookup, key)
    overlap = (set(data.columns) & set(columns)) - {key}
    if overlap:
        raise ValidationError(f"Join would overwrite or suffix columns: {sorted(overlap)}")
    marker = "_caelik_lookup_match"
    if marker in data.columns or marker in lookup.columns:
        raise ValueError(f"Reserved join marker already exists: {marker}")
    joined = data.merge(
        lookup[columns], how="left", on=key, validate="many_to_one",
        indicator=marker, sort=False,
    )
    if require_match and not joined[marker].eq("both").all():
        unknown = joined.loc[~joined[marker].eq("both"), key].drop_duplicates().head(10).tolist()
        raise ValidationError(f"Unmatched {key} values (up to 10 shown): {unknown!r}")
    return joined.drop(columns=[marker])
