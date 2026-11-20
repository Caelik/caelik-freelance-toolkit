"""Caelik Freelance Toolkit v0.2.0 — reusable mechanics, not client business rules."""

from .analysis import aggregate_metrics, rank_metric, reconcile_rollups
from .audit import DataAudit, audit_dataframe
from .cleaning import apply_id_corrections, convert_date_column, remove_exact_duplicates, standardize_values
from .inventory import flag_reorder_points
from .io_utils import export_tables, load_table
from .joins import join_lookup
from .privacy import pseudonymize_column
from .reporting import add_column_chart, format_table_sheet, style_workbook
from .validation import ValidationError, check_total, require_columns, require_unique_ids

__all__ = [
    "DataAudit", "ValidationError", "add_column_chart", "aggregate_metrics",
    "apply_id_corrections", "audit_dataframe", "check_total",
    "convert_date_column", "export_tables", "flag_reorder_points",
    "format_table_sheet", "join_lookup", "load_table",
    "pseudonymize_column", "rank_metric", "reconcile_rollups",
    "remove_exact_duplicates", "require_columns", "require_unique_ids",
    "standardize_values", "style_workbook",
]
