---
type: Table
title: Customers
description: One row per customer who has placed an order. Minimal fields — this is Order Management, not full CRM/Account Management.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.customers
domain: customer_support
tags: [customers, orders, tiering]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_id` | BIGSERIAL PK | |
| `full_name` | VARCHAR(150) | |
| `email` | VARCHAR(150) | Unique, not null. |
| `phone` | VARCHAR(20) | |
| `customer_tier` | VARCHAR(20) | One of: `Standard`, `Gold`, `VIP`. Default `Standard`. |
| `created_at` | TIMESTAMP | |

# Business Rules

- `email` is the natural lookup key used by support agents ("what orders
  has x@example.com placed?").
- `customer_tier` does not currently gate any documented business rule in
  this schema but is available for tier-based support prioritization.

# Common Queries

**Orders placed by a customer email:**
```sql
SELECT o.order_id, o.order_status, o.order_date, o.total_amount
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE c.email = 'ananya.rao@example.com'
ORDER BY o.order_date DESC;
```

# Related Concepts

- [Orders](./orders.md)
- [Return Requests](./return_requests.md)
