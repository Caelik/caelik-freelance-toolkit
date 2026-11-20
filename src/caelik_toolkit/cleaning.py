"""Small, explicit cleaning operations that return copies of input data."""

from collections.abc import Mapping

import pandas as pd


def apply_id_corrections(
    data: pd.DataFrame,
    id_column: str,
    corrections: Mapping[object, Mapping[str, object]],
) -> pd.DataFrame:
    """Apply approved `{id: {column: new_value}}` edits to unique IDs.

    Fails if an ID is missing or repeated. Keep approved business corrections
    in client-specific project_rules.py, not the shared toolkit.
    """
    if id_column not in data.columns:
        raise KeyError(f"Missing ID column: {id_column}")
    result = data.copy()
    for record_id, changes in corrections.items():
        matches = result[id_column].eq(record_id)
        if int(matches.sum()) != 1:
            raise ValueError(
                f"Expected exactly one {id_column}={record_id!r}; "
                f"found {int(matches.sum())}."
            )
        for column, value in changes.items():
            if column not in result.columns:
                raise KeyError(f"Unknown correction column: {column}")
            result.loc[matches, column] = value
    return result


def convert_date_column(
    data: pd.DataFrame,
    column: str,
    *,
    date_format: str = "mixed",
    dayfirst: bool = False,
) -> pd.DataFrame:
    """Convert parseable dates; throw on unexpected values instead of hiding them.

    Inspect ambiguous dates before using `format='mixed'`.
    """
    if column not in data.columns:
        raise KeyError(f"Missing date column: {column}")
    result = data.copy()
    result[column] = pd.to_datetime(
        result[column], format=date_format, dayfirst=dayfirst, errors="raise"
    )
    return result


def remove_exact_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    """Remove perfectly identical records only; never guess which ID update wins."""
    return data.drop_duplicates().copy()


def standardize_values(
    data: pd.DataFrame,
    column: str,
    replacements: Mapping[str, str],
    *,
    output_column: str | None = None,
    strip_whitespace: bool = True,
) -> pd.DataFrame:
    """Normalize explicit category aliases, preserving the input DataFrame.

    Defaults to a new '<column> Standardized' field, retaining source values.
    """
    if column not in data.columns:
        raise KeyError(f"Missing category column: {column}")
    result = data.copy()
    target = output_column if output_column is not None else f"{column} Standardized"
    values = result[column].astype("string")
    if strip_whitespace:
        values = values.str.strip()
    result[target] = values.replace(dict(replacements))
    return result
