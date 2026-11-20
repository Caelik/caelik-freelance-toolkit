"""v0.2 checks use invented transactions only — no private client data."""

import unittest

import pandas as pd

from caelik_toolkit import (
    ValidationError, aggregate_metrics, flag_reorder_points, join_lookup,
    pseudonymize_column, rank_metric, reconcile_rollups,
)


class ToolkitV02Tests(unittest.TestCase):
    def setUp(self):
        self.sales = pd.DataFrame({
            "SKU": ["P01", "P01", "P02", "P02"],
            "Month": ["Sep", "Oct", "Sep", "Oct"],
            "Amount": [12.0, -3.0, 9.0, 4.0],
            "Units": [2, -1, 3, 1],
        })
        self.product_lookup = pd.DataFrame({
            "SKU": ["P01", "P02"],
            "Category": ["Notebooks", "Pens"],
        })

    def test_aggregate_metrics_reconciles(self):
        grouped = aggregate_metrics(self.sales, "Month", {
            "Net Sales": ("Amount", "sum"), "Net Units": ("Units", "sum")
        })
        self.assertEqual(grouped.loc[grouped.Month.eq("Sep"), "Net Sales"].iloc[0], 21.0)
        self.assertEqual(grouped["Net Units"].sum(), 5)
        self.assertNotIn("Net Sales", self.sales.columns)

    def test_aggregate_missing_group_fails_closed(self):
        data = self.sales.copy()
        data.loc[0, "Month"] = None
        with self.assertRaises(ValidationError):
            aggregate_metrics(data, "Month", {"Net Sales": ("Amount", "sum")})
        result = aggregate_metrics(data, "Month", {"Net Sales": ("Amount", "sum")}, allow_missing_groups=True)
        self.assertEqual(len(result), 3)

    def test_join_lookup_many_to_one(self):
        result = join_lookup(self.sales, self.product_lookup, key="SKU")
        self.assertEqual(len(result), 4)
        self.assertEqual(result.loc[0, "Category"], "Notebooks")
        self.assertNotIn("Category", self.sales.columns)

    def test_join_lookup_unmatched_or_duplicate_fails(self):
        unmatched = self.sales.copy()
        unmatched.loc[0, "SKU"] = "MISSING"
        with self.assertRaises(ValidationError):
            join_lookup(unmatched, self.product_lookup, key="SKU")
        kept = join_lookup(unmatched, self.product_lookup, key="SKU", require_match=False)
        self.assertTrue(pd.isna(kept.loc[0, "Category"]))
        duplicated = pd.concat([self.product_lookup, self.product_lookup.iloc[[0]]], ignore_index=True)
        with self.assertRaises(ValidationError):
            join_lookup(self.sales, duplicated, key="SKU")

    def test_join_lookup_overlapping_field_fails(self):
        with self.assertRaises(ValidationError):
            join_lookup(self.sales.assign(Category="old"), self.product_lookup, key="SKU")

    def test_flag_reorder_points_unknown_and_discontinued(self):
        data = pd.DataFrame({
            "SKU": ["A", "B", "C", "D"],
            "On Hand": [0, 9, None, 1],
            "Reorder Point": [2, 2, 3, 2],
            "Active": ["Yes", "Yes", "Yes", "No"],
        })
        result = flag_reorder_points(data, active_column="Active")
        self.assertEqual(result["Stock Decision"].tolist(), [
            "Review for reorder", "Above reorder point", "Stock check required",
            "Discontinued — do not reorder",
        ])
        self.assertTrue(pd.isna(result.loc[2, "On Hand"]))
        self.assertNotIn("Stock Decision", data.columns)

    def test_discontinued_item_with_unknown_stock_is_not_flagged_for_recount(self):
        data = pd.DataFrame({
            "On Hand": [None], "Reorder Point": [2], "Active": ["No"],
        })
        result = flag_reorder_points(data, active_column="Active")
        self.assertEqual(result.loc[0, "Stock Decision"], "Discontinued — do not reorder")

    def test_flag_reorder_points_rejects_ambiguous_stock(self):
        data = pd.DataFrame({"On Hand": [-1], "Reorder Point": [2]})
        with self.assertRaises(ValidationError):
            flag_reorder_points(data)
        data.loc[0, "On Hand"] = None
        data.loc[0, "Reorder Point"] = None
        with self.assertRaises(ValidationError):
            flag_reorder_points(data)

    def test_pseudonymize_column_has_stable_labels(self):
        data = pd.DataFrame({"Customer": ["Ada", "Nia", "Ada", None, " "]})
        result = pseudonymize_column(data, "Customer")
        self.assertEqual(result["Customer"].iloc[:3].tolist(), [
            "Customer 001", "Customer 002", "Customer 001"
        ])
        self.assertTrue(pd.isna(result["Customer"].iloc[3]))
        self.assertEqual(result["Customer"].iloc[4], " ")
        self.assertEqual(data["Customer"].iloc[0], "Ada")

    def test_pseudonymize_mapping_requires_all_values(self):
        data = pd.DataFrame({"Customer": ["Ada", "Nia"]})
        with self.assertRaises(ValidationError):
            pseudonymize_column(data, "Customer", mapping={"Ada": "Customer 001"})
        result = pseudonymize_column(data, "Customer", mapping={
            "Ada": "Customer 032", "Nia": "Customer 010"
        })
        self.assertEqual(result["Customer"].tolist(), ["Customer 032", "Customer 010"])

    def test_rank_metric_competition_ties(self):
        data = pd.DataFrame({"Product": ["A", "B", "C"], "Revenue": [50, 50, 10]})
        result = rank_metric(data, "Revenue")
        self.assertEqual(result["Revenue Rank"].tolist(), [1, 1, 3])
        self.assertNotIn("Revenue Rank", data.columns)

    def test_reconcile_rollups_three_views(self):
        by_month = aggregate_metrics(self.sales, "Month", {
            "Net Sales": ("Amount", "sum"), "Net Units": ("Units", "sum")
        })
        by_sku = aggregate_metrics(self.sales, "SKU", {
            "Net Sales": ("Amount", "sum"), "Net Units": ("Units", "sum")
        })
        result = reconcile_rollups(self.sales, {"Month": by_month, "SKU": by_sku}, {
            "Amount": "Net Sales", "Units": "Net Units"
        })
        self.assertEqual(result, {"Amount": 22.0, "Units": 5.0})

    def test_reconcile_rollups_mismatch_rejected(self):
        bad = pd.DataFrame({"Net Sales": [23.0]})
        with self.assertRaises(ValidationError):
            reconcile_rollups(self.sales, {"Month": bad}, {"Amount": "Net Sales"})


if __name__ == "__main__":
    unittest.main()
