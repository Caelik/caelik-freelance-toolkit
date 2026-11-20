"""Pseudonyms for portfolio *samples*, not a confidentiality guarantee.

Prefer aggregates or fully synthetic records for public portfolios. This helper
only replaces ONE field; names, notes, IDs, workbook metadata, etc. can still
identify people. Never use it as a blanket 'anonymize spreadsheet' solution.
"""

from collections.abc import Mapping

import pandas as pd

from .validation import ValidationError, require_columns


def pseudonymize_column(
    data: pd.DataFrame,
    column: str,
    *,
    prefix: str = "Customer",
    mapping: Mapping[object, str] | None = None,
    output_column: str | None = None,
) -> pd.DataFrame:
    """Replace labels with stable Customer 001-style identifiers in a COPY.

    Without a mapping, first appearance defines numbering *within this call*.
    For consistency across sheets, supply a private mapping created separately.
    Missing/blank strings stay missing/blank. An output_column keeps raw names;
    do NOT publish that extra column. Never publish the name mapping itself.
    """
    require_columns(data, [column])
    if not prefix.strip():
        raise ValueError("Pseudonym prefix cannot be blank.")
    target = output_column or column
    if output_column is not None and output_column in data.columns:
        raise ValueError(f"Output column already exists: {output_column}")
    result = data.copy()
    values = data[column]
    valid = values.notna() & values.astype("string").str.strip().ne("").fillna(False)
    if mapping is None:
        names = list(pd.unique(values.loc[valid]))
        lookup = {name: f"{prefix} {i:03d}" for i, name in enumerate(names, start=1)}
    else:
        lookup = dict(mapping)
        uncovered = [v for v in pd.unique(values.loc[valid]) if v not in lookup]
        if uncovered:
            raise ValidationError(f"Private pseudonym mapping misses {len(uncovered)} labels.")
    result[target] = values.map(lookup).where(valid, values)
    return result
