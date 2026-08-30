---
type: Table
title: Order Items
description: One row per SKU line item within an order. Unit price is a point-in-time snapshot, not the live price.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.order_items
domain: customer_support
tags: [orders, line-items, returns]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `order_item_id` | BIGSERIAL PK | |
| `order_id` | VARCHAR(20) | FK to [orders](./orders.md). |
| `sku` | VARCHAR(30) | FK to [product_variants](./product_variants.md). |
| `quantity` | INT | Must be > 0. |
| `unit_price` | DECIMAL(10,2) | Price **at time of purchase** — never re-derive from live [product_pricing](./product_pricing.md). |
| `line_total` | DECIMAL(10,2) | |
| `item_status` | VARCHAR(30) | One of: `ACTIVE`, `CANCELLED`, `RETURNED`. Default `ACTIVE`. |

# Business Rules

- `unit_price`/`line_total` are historical snapshots — do not join to
  `product_pricing` to compute what a customer paid.
- `item_status = CANCELLED` is set when the parent order is cancelled before
  dispatch; `RETURNED` is set once a linked [return_requests](./return_requests.md)
  row completes.
- Every returnable item has a 1:1 [item_condition_flags](./item_condition_flags.md)
  row keyed by `order_item_id`.

# Common Queries

**Line items for an order:**
```sql
SELECT order_item_id, sku, quantity, unit_price, line_total, item_status
FROM order_items
WHERE order_id = 'ORD-2026-00841';
```

# Related Concepts

- [Orders](./orders.md)
- [Product Variants](./product_variants.md)
- [Return Requests](./return_requests.md)
- [Item Condition Flags](./item_condition_flags.md)
- [Return Rate](../metrics/return_rate.md)
