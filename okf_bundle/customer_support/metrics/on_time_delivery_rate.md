---
type: Metric
title: On-Time Delivery Rate
description: Percentage of delivered orders that arrived on or before their estimated delivery date. Target is >= 90%.
domain: customer_support
tags: [orders, delivery, logistics, kpi]
timestamp: 2026-08-21T09:00:00Z
---

# Definition

On-Time Delivery Rate = (count of orders with `order_status = 'DELIVERED'`
AND `actual_delivery_date <= estimated_delivery_date`) /
(total count of orders with `order_status = 'DELIVERED'`) × 100

Orders without an `estimated_delivery_date` (e.g. cancelled before
dispatch) are excluded.

# SQL

```sql
SELECT
    ROUND(
        100.0 * SUM(CASE WHEN actual_delivery_date <= estimated_delivery_date THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS on_time_delivery_rate_pct
FROM orders
WHERE order_status = 'DELIVERED'
  AND estimated_delivery_date IS NOT NULL;
```

# Source Tables

- [Orders](../tables/orders.md)
- [Shipments](../tables/shipments.md)

# Thresholds

| Level    | Value    |
|----------|----------|
| Healthy  | >= 90%   |
| Warning  | 75% - 90% |
| Critical | < 75%    |
