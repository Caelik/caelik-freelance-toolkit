"""Run after installation: python examples/quickstart.py"""

import pandas as pd
from caelik_toolkit import audit_dataframe, standardize_values, require_unique_ids

sample = pd.DataFrame({
    "Ticket": ["T-001", "T-002", "T-003"],
    "Service": ["Lawn maint.", "Lawn Maintenance", "Pressure wash"],
    "Invoice": [110.0, 125.0, 240.0],
})

audit = audit_dataframe(sample, id_column="Ticket")
print(audit.overview())
print("\nColumn audit:")
print(audit.columns.to_string(index=False))

cleaned = standardize_values(sample, "Service", {
    "Lawn maint.": "Lawn Maintenance",
    "Pressure wash": "Pressure Washing",
})
require_unique_ids(cleaned, "Ticket")
print("\nStandardized categories:")
print(cleaned[["Ticket", "Service Standardized"]].to_string(index=False))
