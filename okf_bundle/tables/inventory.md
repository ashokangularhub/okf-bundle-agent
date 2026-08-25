---
type: Table
title: Inventory
description: Per-SKU, per-warehouse stock levels. The table the "is it in stock" queries actually hit.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.inventory
domain: customer_support
tags: [inventory, stock, warehouses, availability]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `inventory_id` | BIGSERIAL PK | |
| `sku` | VARCHAR(30) | FK to [product_variants](./product_variants.md). |
| `warehouse_id` | VARCHAR(10) | FK to [warehouses](./warehouses.md). |
| `quantity_on_hand` | INT | Default 0. |
| `quantity_reserved` | INT | Allocated to unshipped orders. Default 0. |
| `reorder_threshold` | INT | Default 10. |
| `restock_eta_date` | DATE | Populated when `quantity_on_hand = 0`. |
| `last_updated` | TIMESTAMP | |

Unique constraint on `(sku, warehouse_id)`.

# Business Rules

- Available quantity for a SKU = `SUM(quantity_on_hand - quantity_reserved)`
  across all warehouses (the availability logic used by `product-service`).
- Availability status: `IN_STOCK` if available qty > 0; `OUT_OF_STOCK_RESTOCKING`
  if <= 0 but `restock_eta_date` is set; otherwise `OUT_OF_STOCK`.
- When `quantity_on_hand - quantity_reserved <= reorder_threshold`, the SKU
  should be escalated to procurement — see
  [Low Stock Restock Escalation](../runbooks/low_stock_restock_escalation.md).

# Common Queries

**SKUs at or below reorder threshold:**
```sql
SELECT sku, warehouse_id, quantity_on_hand, quantity_reserved, reorder_threshold
FROM inventory
WHERE (quantity_on_hand - quantity_reserved) <= reorder_threshold;
```

**Out-of-stock SKUs with no restock ETA:**
```sql
SELECT sku, warehouse_id
FROM inventory
WHERE quantity_on_hand = 0 AND restock_eta_date IS NULL;
```

# Related Concepts

- [Product Variants](./product_variants.md)
- [Warehouses](./warehouses.md)
- [Stock Availability Rate](../metrics/stock_availability_rate.md)
- [Low Stock Restock Escalation](../runbooks/low_stock_restock_escalation.md)
