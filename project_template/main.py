"""Copy this entire folder for a new client; modify project_rules.py."""

from pathlib import Path

from caelik_toolkit import audit_dataframe, export_tables, load_table
from project_rules import apply_project_rules

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "data" / "raw" / "source.xlsx"
OUTPUT = BASE / "output" / "working_report.xlsx"


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Place a client workbook at {SOURCE} or edit SOURCE in main.py."
        )
    raw = load_table(SOURCE)
    audit = audit_dataframe(raw)  # Supply id_column once you know the schema.
    print(audit.overview())
    cleaned = apply_project_rules(raw)
    export_tables({"Working Data": cleaned}, OUTPUT, overwrite=True)
    print(f"Report written: {OUTPUT}")


if __name__ == "__main__":
    main()
