# Caelik Freelance Toolkit

**Reusable Python helpers for data auditing, cleaning, validation, analysis, and Excel reporting.**

This is a portfolio and learning project built around common challenges in small-business data analysis: inconsistent categories, duplicate records, missing values, unreliable lookups, inventory exceptions, and totals that need to reconcile. The library deliberately separates **generic operations** from **project-specific business rules**.

**Current version:** `0.2.0` · **Python:** 3.10 or newer

## What it does

| Area | Main functions | Purpose |
|---|---|---|
| Audit | `audit_dataframe` | Examine data types, blanks, exact duplicates, and repeated IDs without editing the source |
| Cleaning | `standardize_values`, `convert_date_column`, `apply_id_corrections`, `remove_exact_duplicates` | Apply explicit transformations to copies |
| Validation | `require_columns`, `require_unique_ids`, `check_total` | Stop when required data or totals are inconsistent |
| Joins | `join_lookup` | Perform validated many-to-one reference-table joins |
| Analysis | `aggregate_metrics`, `rank_metric`, `reconcile_rollups` | Build summaries, rankings, and cross-check totals |
| Inventory | `flag_reorder_points` | Flag stock needing review while preserving unknown counts |
| Privacy examples | `pseudonymize_column` | Make consistent single-column example labels; **not full anonymization** |
| I/O and Excel | `load_table`, `export_tables`, `format_table_sheet`, `add_column_chart`, `style_workbook` | Read and export data, and format basic Excel reports |

## Installation

Clone this repository or download its source. From the repository folder, use a Python 3.10+ environment:

```bash
python -m pip install -e .
```

The package installs as `caelik_toolkit` and depends on `pandas` and `openpyxl`. An isolated virtual environment is recommended.

## Quick example

```python
import pandas as pd
from caelik_toolkit import (
    aggregate_metrics,
    audit_dataframe,
    check_total,
    standardize_values,
)

raw = pd.DataFrame({
    "Order": ["A-101", "A-102", "A-103"],
    "Service": ["Lawn maint.", "Lawn Maintenance", "Pressure wash"],
    "Amount": [120.0, 180.0, 90.0],
})

print(audit_dataframe(raw, id_column="Order").overview())
cleaned = standardize_values(raw, "Service", {
    "Lawn maint.": "Lawn Maintenance",
    "Pressure wash": "Pressure Washing",
})

summary = aggregate_metrics(
    cleaned, "Service Standardized", {"Revenue": ("Amount", "sum")}
)
check_total(summary, "Revenue", expected=390.0)
print(summary)
```

The example is fictional. For real projects, revenue definitions, refunds, exceptions, dates, and any permitted corrections must be established in that project's own rules.

## Run the tests and examples

After installation:

```bash
python -m unittest discover -s tests -v
python examples/quickstart.py
python examples/retail_workflow.py
python examples/portfolio_labels.py
```

The tests use invented records and cover auditing, transformations, joins, reconciliations, reorder flags, Excel formatting, and error paths. Passing tests do not guarantee a new dataset is correct: source validation and client-specific checks remain essential.

## Repository layout

```text
src/caelik_toolkit/   Reusable Python package
examples/             Small self-contained fictional examples
tests/                Automated unit tests
project_template/     Starting folder for a separate analytics project
docs/                 Privacy and publication guidance
```

For a new project, copy `project_template/` **outside the toolkit repository**, place untouched source files in `data/raw/`, and adapt `project_rules.py` to the approved business logic. Install the shared toolkit into that project's environment with `pip install -e <path-to-toolkit>`.

## Design principles and limitations

- Preserve original records; cleaning functions return copies rather than silently rewriting inputs.
- **Exact duplicate records** and **repeated IDs** are different questions. Don't drop records solely because a key repeats.
- Treat missing financial amounts and missing inventory counts as unknown, not zero.
- Validate joins and reconcile summaries against cleaned detail before issuing a report.
- Reorder flags describe a **stock snapshot**, not automatic purchasing recommendations or a live inventory system.
- `pseudonymize_column()` replaces just one field; it does not anonymize a full dataset. See `docs/PRIVACY_CHECKLIST.md` before sharing any client-derived work.
- Do not commit actual client files, credentials, identifiable records, or proprietary business rules to this repository.

## Development note

This toolkit was developed with AI-assisted coding and documentation, followed by review, testing, and experimentation with fictional analytics scenarios. Its purpose is to demonstrate reusable patterns and careful validation, not to present a production-ready data platform.

## License

Licensed under the [MIT License](LICENSE). Copyright (c) 2026 Brad Kessenich.
