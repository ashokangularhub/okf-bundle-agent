---
type: Table
title: Product Pricing
description: Current effective (promo-aware) price per SKU, kept separate from the reference base_price on products.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.product_pricing
domain: customer_support
tags: [products, pricing, promotions]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `sku` | VARCHAR(30) PK | FK to [product_variants](./product_variants.md). |
| `current_price` | DECIMAL(10,2) | Live sell price. |
| `discount_pct` | DECIMAL(5,2) | Default 0. |
| `promo_label` | VARCHAR(100) | e.g. "Festive Sale". NULL if no active promo. |
| `promo_start_date` / `promo_end_date` | DATE | |
| `last_price_update` | TIMESTAMP | |

# Business Rules

- This table — not `products.base_price` — is the source of truth for what
  a customer is actually charged.
- Every active [product_variants](./product_variants.md) row must have a
  corresponding `product_pricing` row; the product-service availability
  query inner-joins on it.

# Common Queries

**SKUs currently on promotion:**
```sql
SELECT sku, current_price, discount_pct, promo_label
FROM product_pricing
WHERE promo_label IS NOT NULL;
```

# Related Concepts

- [Product Variants](./product_variants.md)
- [Products](./products.md)
- [Stock Availability Rate](../metrics/stock_availability_rate.md)
