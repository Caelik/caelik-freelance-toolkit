"""Toy example only. Publishing real row-level records requires wider review."""

import pandas as pd

from caelik_toolkit import pseudonymize_column

sample = pd.DataFrame({
    "Customer": ["Invented Name A", "Invented Name B", "Invented Name A"],
    "Category": ["Notebooks", "Greeting Cards", "Notebooks"],
})

preview = pseudonymize_column(sample, "Customer")
print(preview.to_string(index=False))
