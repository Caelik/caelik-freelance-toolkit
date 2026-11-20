"""Reusable Excel presentation helpers; they do not change source files."""

from collections.abc import Iterable
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


CURRENCY_FORMAT = '"$"#,##0.00'
DATE_FORMAT = "mm/dd/yyyy"


def add_column_chart(
    ws: Worksheet,
    *,
    header_row: int,
    last_row: int,
    category_col: int,
    value_col: int,
    title: str,
    position: str = "F2",
    bar_color: str = "244C43",
) -> None:
    """Build a chart from table cells; labels must already be display-ready."""
    if last_row <= header_row:
        raise ValueError("A chart needs at least one data row.")
    chart = BarChart()
    chart.type = "col"
    chart.title = title
    chart.style = 10
    chart.legend = None
    chart.width, chart.height = 18, 10
    chart.y_axis.scaling.min = 0
    chart.y_axis.numFmt = '"$"#,##0'
    chart.x_axis.tickLblPos = "nextTo"
    values = Reference(ws, min_col=value_col, min_row=header_row, max_row=last_row)
    categories = Reference(
        ws, min_col=category_col, min_row=header_row + 1, max_row=last_row
    )
    chart.add_data(values, titles_from_data=True)
    chart.set_categories(categories)
    chart.series[0].graphicalProperties.solidFill = bar_color
    ws.add_chart(chart, position)


def format_table_sheet(
    ws: Worksheet,
    *,
    currency_columns: Iterable[str] = (),
    date_columns: Iterable[str] = (),
    header_row: int = 1,
    freeze_columns: int = 0,
    header_color: str = "244C43",
    alternating_color: str = "F2F7F4",
    max_width: int = 45,
) -> None:
    """Style ordinary Excel tables with headers, filters, frozen panes and formats.

    Column selectors are header *names*, not Excel letters. Only presentation
    changes are made. Dates must be actual Excel date values to display as dates.
    """
    if ws.max_row < header_row or header_row < 1:
        raise ValueError("Header row does not exist.")
    currency_columns = set(currency_columns)
    date_columns = set(date_columns)
    ws.sheet_view.showGridLines = False
    fill_header = PatternFill("solid", fgColor=header_color)
    fill_alt = PatternFill("solid", fgColor=alternating_color)
    for cell in ws[header_row]:
        cell.fill = fill_header
        cell.font = Font(name="Aptos", color="FFFFFF", bold=True)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[header_row].height = 30

    for col in range(1, ws.max_column + 1):
        header = ws.cell(header_row, col).value
        if header is None:
            continue
        texts = [str(ws.cell(r, col).value) for r in range(header_row, min(ws.max_row, header_row + 100) + 1)
                 if ws.cell(r, col).value is not None]
        width = min(max(max(map(len, texts), default=10) + 4, 14), max_width)
        ws.column_dimensions[get_column_letter(col)].width = width
        for row in range(header_row + 1, ws.max_row + 1):
            cell = ws.cell(row, col)
            if row % 2 == 0:
                cell.fill = fill_alt
            cell.font = Font(name="Aptos", size=10)
            if header in currency_columns:
                cell.number_format = CURRENCY_FORMAT
            elif header in date_columns:
                cell.number_format = DATE_FORMAT
    last_col = get_column_letter(ws.max_column)
    ws.auto_filter.ref = f"A{header_row}:{last_col}{ws.max_row}"
    ws.freeze_panes = f"{get_column_letter(freeze_columns + 1)}{header_row + 1}"


def style_workbook(
    source: str | Path,
    target: str | Path,
    *,
    formats: dict[str, dict] | None = None,
) -> Path:
    """Apply general table formatting to selected sheets of an existing workbook."""
    source, target = Path(source), Path(target)
    if source.resolve() == target.resolve():
        raise ValueError("Use a separate target file to preserve the unstylized export.")
    wb = load_workbook(source)
    for sheet_name, options in (formats or {}).items():
        if sheet_name not in wb.sheetnames:
            raise KeyError(f"Worksheet does not exist: {sheet_name}")
        format_table_sheet(wb[sheet_name], **options)
    target.parent.mkdir(parents=True, exist_ok=True)
    wb.save(target)
    return target
