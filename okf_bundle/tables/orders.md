---
type: Table
title: Orders
description: One row per order header. order_status is the field most order-management queries resolve to.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.orders
domain: customer_support
tags: [orders, fulfillment, payments]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `order_id` | VARCHAR(20) PK | e.g. `ORD-2026-00841`. |
| `customer_id` | BIGINT | FK to [customers](./customers.md). |
| `order_status` | VARCHAR(30) | One of: `PLACED`, `CONFIRMED`, `PACKED`, `SHIPPED`, `OUT_FOR_DELIVERY`, `DELIVERED`, `CANCELLED`, `RETURN_INITIATED`, `RETURNED`. |
| `order_date` | TIMESTAMP | |
| `payment_status` | VARCHAR(20) | One of: `Paid`, `Pending`, `Failed`, `Refunded`. Default `Paid`. |
| `shipping_address` / `shipping_city` | TEXT / VARCHAR(50) | |
| `warehouse_id` | VARCHAR(10) | FK to [warehouses](./warehouses.md) — the fulfilling warehouse. |
| `subtotal_amount` / `shipping_amount` / `total_amount` | DECIMAL(10,2) | |
| `currency` | CHAR(3) | Default `INR`. |
| `estimated_delivery_date` / `actual_delivery_date` | DATE | |
| `last_updated` | TIMESTAMP | |

# Business Rules

- `order_status` is a closed enum enforced by a `CHECK` constraint — no
  other values are valid.
- Every status transition is also recorded as its own row in
  [order_status_history](./order_status_history.md) — use that table for
  timeline/audit queries; this table only holds the *current* status.
- `payment_status = Refunded` corresponds to a `CANCELLED` order whose
  payment was reversed (see seed data example `ORD-2026-00844`).
- On-time delivery is measured as `actual_delivery_date <= estimated_delivery_date`
  — see [On-Time Delivery Rate](../metrics/on_time_delivery_rate.md).

# Common Queries

**Where is order X? (order + customer + shipment in one shot):**
```sql
SELECT o.order_id, c.full_name, c.email, o.order_status, o.order_date,
       o.payment_status, o.estimated_delivery_date, o.actual_delivery_date,
       s.carrier_name, s.tracking_number, s.shipment_status, s.current_location,
       o.total_amount, o.currency
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
LEFT JOIN shipments s ON s.order_id = o.order_id
WHERE o.order_id = 'ORD-2026-00842';
```

**Orders cancelled but not yet refunded:**
```sql
SELECT order_id, customer_id, total_amount
FROM orders
WHERE order_status = 'CANCELLED' AND payment_status != 'Refunded';
```

# Related Concepts

- [Customers](./customers.md)
- [Order Items](./order_items.md)
- [Shipments](./shipments.md)
- [Order Status History](./order_status_history.md)
- [On-Time Delivery Rate](../metrics/on_time_delivery_rate.md)
- [Shipment Exception Handling](../runbooks/shipment_exception_handling.md)
