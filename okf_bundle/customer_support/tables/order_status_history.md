---
type: Table
title: Order Status History
description: Append-only audit trail of every order status transition. Use this for "why is my order delayed" timeline queries, not the orders table.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.order_status_history
domain: customer_support
tags: [orders, audit, timeline]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `history_id` | BIGSERIAL PK | |
| `order_id` | VARCHAR(20) | FK to [orders](./orders.md). |
| `status` | VARCHAR(30) | Same enum as `orders.order_status`. |
| `status_timestamp` | TIMESTAMP | |
| `notes` | VARCHAR(200) | e.g. cancellation reason. |

# Business Rules

- Rows are append-only; never updated or deleted.
- The most recent row per `order_id` (by `status_timestamp`) should always
  match `orders.order_status` for that order.

# Common Queries

**Full status timeline for an order:**
```sql
SELECT status, status_timestamp, notes
FROM order_status_history
WHERE order_id = 'ORD-2026-00843'
ORDER BY status_timestamp ASC;
```

# Related Concepts

- [Orders](./orders.md)
- [Shipment Exception Handling](../runbooks/shipment_exception_handling.md)
