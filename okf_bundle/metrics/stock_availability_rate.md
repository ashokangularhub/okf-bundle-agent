---
type: Metric
title: Stock Availability Rate
description: Percentage of active SKUs currently in stock across all warehouses. Target is >= 95%.
domain: customer_support
tags: [inventory, products, kpi, availability]
timestamp: 2026-08-21T09:00:00Z
---

# Definition

Stock Availability Rate = (count of active [product_variants](../tables/product_variants.md)
with total available quantity > 0 across all [warehouses](../tables/warehouses.md)) /
(total count of active product_variants) × 100

Available quantity per SKU = `SUM(quantity_on_hand - quantity_reserved)` from
[inventory](../tables/inventory.md).

# SQL

```sql
SELECT
    ROUND(
        100.0 * SUM(CASE WHEN available_qty > 0 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS stock_availability_rate_pct
FROM (
    SELECT pv.sku, COALESCE(SUM(inv.quantity_on_hand - inv.quantity_reserved), 0) AS available_qty
    FROM product_variants pv
    LEFT JOIN inventory inv ON inv.sku = pv.sku
    WHERE pv.is_active = TRUE
    GROUP BY pv.sku
) sku_stock;
```

# Source Tables

- [Product Variants](../tables/product_variants.md)
- [Inventory](../tables/inventory.md)

# Thresholds

| Level    | Value      |
|----------|------------|
| Healthy  | >= 95%     |
| Warning  | 85% - 95%  |
| Critical | < 85%      |
