"""Reusable patterns only, using fictional toy records.

This example DOES NOT define how real clients record discounts, returns,
stock movement, or taxes. Always clarify those rules before production use.
"""

import pandas as pd

from caelik_toolkit import (
    aggregate_metrics, flag_reorder_points, join_lookup, rank_metric,
    reconcile_rollups,
)


def main() -> None:
    sales = pd.DataFrame({
        "SKU": ["P-01", "P-02", "P-01", "P-03"],
        "Month": ["Sep", "Sep", "Oct", "Oct"],
        "Net Revenue": [12.0, 7.0, -6.0, 20.0],
        "Net Units": [2, 1, -1, 2],
    })
    products = pd.DataFrame({
        "SKU": ["P-01", "P-02", "P-03"],
        "Category": ["Paper", "Pens", "Paper"],
    })
    stock = pd.DataFrame({
        "SKU": ["P-01", "P-02", "P-03"],
        "On Hand": [1, None, 11],
        "Reorder Point": [3, 2, 6],
        "Active": ["Yes", "Yes", "Yes"],
    })

    linked = join_lookup(sales, products, key="SKU", lookup_columns=["Category"])
    measures = {"Net Sales": ("Net Revenue", "sum"), "Net Units": ("Net Units", "sum")}
    monthly = aggregate_metrics(linked, "Month", measures)
    categories = aggregate_metrics(linked, "Category", measures)
    by_product = aggregate_metrics(linked, "SKU", measures)
    by_product = rank_metric(by_product, "Net Sales", rank_column="Revenue Rank")
    inventory = flag_reorder_points(stock, active_column="Active")

    reconcile_rollups(linked, {"monthly": monthly, "category": categories, "product": by_product},
                      {"Net Revenue": "Net Sales", "Net Units": "Net Units"})

    print("MONTHLY\n", monthly.to_string(index=False))
    print("\nPRODUCT RANKINGS\n", by_product.to_string(index=False))
    print("\nSTOCK FLAGS\n", inventory.to_string(index=False))


if __name__ == "__main__":
    main()
