---
type: Table
title: Warehouses
description: One row per fulfillment warehouse used for inventory and order shipping.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.warehouses
domain: customer_support
tags: [warehouses, fulfillment, logistics]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `warehouse_id` | VARCHAR(10) PK | e.g. `WH-BLR-01`. |
| `warehouse_name` | VARCHAR(100) | |
| `city` / `region` | VARCHAR(50) | |
| `is_active` | BOOLEAN | Default `TRUE`. |

# Business Rules

- Referenced by both [inventory](./inventory.md) (`warehouse_id`, stock per
  SKU) and [orders](./orders.md) (`warehouse_id`, the fulfilling warehouse
  for that order).
- Seed data has two warehouses: `WH-BLR-01` (Bangalore) and `WH-DEL-01` (Delhi).

# Common Queries

**Active warehouses by region:**
```sql
SELECT warehouse_id, warehouse_name, city
FROM warehouses
WHERE region = 'South' AND is_active = TRUE;
```

# Related Concepts

- [Inventory](./inventory.md)
- [Orders](./orders.md)
