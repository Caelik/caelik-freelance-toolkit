"""Put client-specific corrections, categorization and business decisions here.

Do NOT put real client names, account details, and proprietary data inside the
shared toolkit itself or publish them in a public repository.
"""

import pandas as pd


def apply_project_rules(raw: pd.DataFrame) -> pd.DataFrame:
    """Start with a copy; add client-approved transformations here."""
    return raw.copy()
