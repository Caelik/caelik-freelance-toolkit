# Changelog

## 0.2.0 — Seabright lessons and portfolio templates

- Added strict `join_lookup` for many-to-one reference merges and unmatched-ID checks.
- Added `aggregate_metrics`, `rank_metric`, and `reconcile_rollups` for month/product/category analysis.
- Added `flag_reorder_points`, preserving unknown stock and distinguishing discontinued products.
- Clarified reorder-status precedence for discontinued items with unknown stock; added regression test.
- Added `pseudonymize_column` for limited portfolio sample-label substitution, with explicit privacy caveats.
- Added private/public separation guidance, a reusable case-study template, and a Seabright simulated example.
- Added an end-to-end *toy retail* example and 12 new tests (20 total).
- Preserved v0.1 imports and behavior; client-specific revenue/discount/refund corrections remain client code.

## 0.1.0 — First standalone reusable toolkit

- Data audit with missing values, column types and duplicate flags.
- Explicit category mapping, date conversions, ID corrections and exact deduplication.
- Basic integrity and subtotal validation.
- Excel/CSV import, XLSX export, standardized table formatting and column charts.
- Client-folder template, quickstart and automated tests.
