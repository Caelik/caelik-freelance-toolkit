"""Run: python -m unittest discover -s tests -v"""

import tempfile
import unittest
from pathlib import Path

import pandas as pd
from openpyxl import Workbook, load_workbook

from caelik_toolkit import (
    ValidationError,
    apply_id_corrections, audit_dataframe, check_total, convert_date_column,
    add_column_chart, export_tables, format_table_sheet, remove_exact_duplicates,
    require_unique_ids, standardize_values,
)


class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            "Order ID": ["A1", "A2", "A2", "A3"],
            "Category": ["Lawn care", "Hedge", "Hedge", "Lawn Maintenance"],
            "Date": ["07/23/2026", "2026-08-20", "2026-08-20", "10/21/2026"],
            "Amount": [25.0, 40.0, 40.0, None],
        })

    def test_audit_flags_but_does_not_remove_duplicates(self):
        audit = audit_dataframe(self.data, id_column="Order ID")
        self.assertEqual(audit.summary["rows"], 4)
        self.assertEqual(audit.summary["exact_duplicate_extra_rows"], 1)
        self.assertEqual(len(audit.duplicate_id_rows), 2)
        self.assertEqual(len(self.data), 4)

    def test_remove_exact_duplicates_only(self):
        result = remove_exact_duplicates(self.data)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(self.data), 4)

    def test_standardize_does_not_change_source(self):
        result = standardize_values(self.data, "Category", {"Lawn care": "Lawn Maintenance"})
        self.assertEqual(result.loc[0, "Category Standardized"], "Lawn Maintenance")
        self.assertEqual(self.data.loc[0, "Category"], "Lawn care")

    def test_dates_convert_mixed(self):
        result = convert_date_column(self.data, "Date")
        self.assertEqual(result.loc[0, "Date"].month, 7)
        self.assertEqual(result.loc[3, "Date"].month, 10)
        self.assertEqual(self.data.loc[0, "Date"], "07/23/2026")

    def test_id_corrections_require_unique_match(self):
        with self.assertRaises(ValueError):
            apply_id_corrections(self.data, "Order ID", {"A2": {"Amount": 12.5}})
        result = apply_id_corrections(self.data, "Order ID", {"A1": {"Amount": 12.5}})
        self.assertEqual(result.loc[0, "Amount"], 12.5)
        self.assertEqual(self.data.loc[0, "Amount"], 25.0)

    def test_validation_requires_explicit_partial_totals(self):
        with self.assertRaises(ValidationError):
            check_total(self.data, "Amount", 105.0)
        self.assertEqual(check_total(self.data, "Amount", 105.0, allow_missing=True), 105.0)
        with self.assertRaises(ValidationError):
            require_unique_ids(self.data, "Order ID")

    def test_excel_chart_uses_worksheet_range(self):
        wb = Workbook()
        ws = wb.active
        ws.append(["Month", "Revenue"])
        ws.append(["Jul 2026", 100])
        ws.append(["Aug 2026", 150])
        add_column_chart(
            ws, header_row=1, last_row=3,
            category_col=1, value_col=2,
            title="Monthly revenue", position="D2",
        )
        self.assertEqual(len(ws._charts), 1)

    def test_excel_export_and_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.xlsx"
            export_tables({"Orders": self.data}, path)
            with self.assertRaises(FileExistsError):
                export_tables({"Orders": self.data}, path)
            wb = load_workbook(path)
            format_table_sheet(wb["Orders"], currency_columns=["Amount"])
            self.assertEqual(wb["Orders"].freeze_panes, "A2")
            self.assertEqual(wb["Orders"]["D2"].number_format, '"$"#,##0.00')
            wb.save(path)
            wb.close()


if __name__ == "__main__":
    unittest.main()
