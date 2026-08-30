---
type: Metric
title: Return Rate
description: Percentage of delivered order line items that are subsequently returned. Target is <= 8%.
domain: customer_support
tags: [returns, orders, kpi, quality]
timestamp: 2026-08-21T09:00:00Z
---

# Definition

Return Rate = (count of [order_items](../tables/order_items.md) with
`item_status = 'RETURNED'`) / (count of order_items belonging to orders
with `order_status IN ('DELIVERED', 'RETURN_INITIATED', 'RETURNED')`) × 100

# SQL

```sql
SELECT
    ROUND(
        100.0 * SUM(CASE WHEN oi.item_status = 'RETURNED' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS return_rate_pct
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_status IN ('DELIVERED', 'RETURN_INITIATED', 'RETURNED');
```

**By product category:**
```sql
SELECT p.category,
       ROUND(100.0 * SUM(CASE WHEN oi.item_status = 'RETURNED' THEN 1 ELSE 0 END)
             / NULLIF(COUNT(*), 0), 2) AS return_rate_pct
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN product_variants pv ON pv.sku = oi.sku
JOIN products p ON p.product_id = pv.product_id
WHERE o.order_status IN ('DELIVERED', 'RETURN_INITIATED', 'RETURNED')
GROUP BY p.category
ORDER BY return_rate_pct DESC;
```

# Source Tables

- [Order Items](../tables/order_items.md)
- [Orders](../tables/orders.md)
- [Return Requests](../tables/return_requests.md)

# Thresholds

| Level    | Value    |
|----------|----------|
| Healthy  | <= 8%    |
| Warning  | 8% - 15% |
| Critical | > 15%    |
