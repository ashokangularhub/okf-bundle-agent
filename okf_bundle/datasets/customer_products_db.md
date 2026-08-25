---
type: Dataset
title: Customer Products Database
description: Core PostgreSQL database for Aurora Electronics customer support — product catalog, pricing, inventory, order lifecycle, and returns/refunds facts.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support
domain: customer_support
tags: [ecommerce, retail, products, orders, returns, production]
timestamp: 2026-08-21T09:00:00Z
---

# Customer Products Database

The `customer_support` schema inside the shared `common_knowledgebase_db`
PostgreSQL database is the system of record for Aurora Electronics'
product catalog, live pricing/inventory, order fulfillment, and
returns/refunds eligibility facts. It lives alongside the retail banking
tables (`public` schema, see [Retail Bank Database](./retail_bank.db.md))
in the same physical database so this bundle can be reused across
multiple projects without needing a separate database instance.

## Tables

- [products](../tables/products.md) — one row per product line
- [product_variants](../tables/product_variants.md) — one row per purchasable SKU
- [product_pricing](../tables/product_pricing.md) — one row per SKU, current effective price
- [warehouses](../tables/warehouses.md) — one row per fulfillment warehouse
- [inventory](../tables/inventory.md) — one row per SKU/warehouse stock record
- [customers](../tables/customers.md) — one row per customer
- [orders](../tables/orders.md) — one row per order
- [order_items](../tables/order_items.md) — one row per SKU line within an order
- [shipments](../tables/shipments.md) — one row per shipped parcel
- [order_status_history](../tables/order_status_history.md) — append-only order status audit trail
- [return_requests](../tables/return_requests.md) — one row per return request
- [return_window_policy](../tables/return_window_policy.md) — return window/condition rules per category
- [refunds](../tables/refunds.md) — one row per refund issued
- [item_condition_flags](../tables/item_condition_flags.md) — per-order-item return-exclusion flags

## Access

Read/write access is via the `ak-db-service` / `sql-service` FastAPI
applications that front `common_knowledgebase_db`. All tables in this
dataset live under the `customer_support` schema, so SQL must qualify
table names accordingly, e.g. `SELECT * FROM customer_support.orders`.
Direct database access is for reporting/analytics only.

## Source Schema Files

Table structure and seed data are defined in:
- `sql-service/scripts/seed_customer_support_data.sql`

## Retention

- Order and shipment history (orders, order_items, shipments) retained indefinitely
  for customer support history.
- Return/refund records retained for 5 years for compliance/audit purposes.
