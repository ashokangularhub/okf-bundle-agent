---
type: Table
title: Product Variants
description: One row per purchasable SKU (color/switch-type/size option) within a product line.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.product_variants
domain: customer_support
tags: [products, sku, variants, catalog]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `sku` | VARCHAR(30) PK | e.g. `AUR-EB-PRO2-BLK`. The sellable unit. |
| `product_id` | VARCHAR(20) | FK to [products](./products.md). |
| `variant_label` | VARCHAR(100) | e.g. "Obsidian Black", "Aurora Tactile Brown". |
| `variant_type` | VARCHAR(30) | One of: `color`, `switch_type`, `size`. |
| `price_delta` | DECIMAL(10,2) | +/- vs `products.base_price` (e.g. premium colorway). Default 0. |
| `is_active` | BOOLEAN | Default `TRUE`. |

# Business Rules

- `sku` (Stock Keeping Unit) uniquely identifies one specific sellable
  version of a product — `product_id` identifies the general line.
- A single `product_id` can have multiple SKUs; `order_items.sku` and
  `inventory.sku` always reference this table, never `products.product_id`
  directly.
- Effective sell price for a SKU is **not** `products.base_price + price_delta`
  — it is `product_pricing.current_price`, which is independently maintained
  (promo-aware). `price_delta` is descriptive/reference only.

# Common Queries

**All active SKUs for a product:**
```sql
SELECT sku, variant_label, variant_type
FROM product_variants
WHERE product_id = 'AUR-WT-FIT3' AND is_active = TRUE;
```

# Related Concepts

- [Products](./products.md)
- [Product Pricing](./product_pricing.md)
- [Inventory](./inventory.md)
- [Order Items](./order_items.md)
