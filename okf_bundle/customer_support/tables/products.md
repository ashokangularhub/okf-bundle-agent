---
type: Table
title: Products
description: One row per product line (master catalog entry). Live active-status/pricing anchor fields; descriptive spec content lives in the Product Information Catalog PDF.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.products
domain: customer_support
tags: [products, catalog, pricing]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `product_id` | VARCHAR(20) PK | e.g. `AUR-EB-PRO2`. Matches the PDF catalog's "Product ID" field. |
| `product_name` | VARCHAR(150) | e.g. "AuroraBuds Pro 2". |
| `category` | VARCHAR(50) | One of: `Earbuds`, `Smartwatch`, `Speaker`, `Accessory`, `Keyboard`. |
| `base_price` | DECIMAL(10,2) | MRP before discounts/tax. |
| `currency` | CHAR(3) | Default `INR`. |
| `is_active` | BOOLEAN | `FALSE` = discontinued, still supported for post-sale. |
| `launch_date` | DATE | |
| `discontinued_date` | DATE | NULL while active. |
| `created_at` / `updated_at` | TIMESTAMP | |

# Business Rules

- Only fields that change frequently or must be looked up exactly live here;
  narrative specs/compatibility content lives in the
  [Product Information Catalog](../datasets/product_information_catalog.md) PDF.
- `is_active = FALSE` products are discontinued but remain visible for
  post-sale support (returns, warranty) — see [return_window_policy](./return_window_policy.md).
- Return window / condition requirements are keyed by `category`, not by
  individual product.

# Common Queries

**All active products in a category:**
```sql
SELECT product_id, product_name, base_price, currency
FROM products
WHERE category = 'Keyboard' AND is_active = TRUE;
```

**Cheapest variant of a product (via product_variants/product_pricing):**
```sql
SELECT pv.variant_label, pp.current_price
FROM product_variants pv
JOIN product_pricing pp ON pp.sku = pv.sku
WHERE pv.product_id = 'AUR-KB-K5'
ORDER BY pp.current_price ASC
LIMIT 1;
```

# Related Concepts

- [Product Variants](./product_variants.md)
- [Product Pricing](./product_pricing.md)
- [Inventory](./inventory.md)
- [Product Information Catalog](../datasets/product_information_catalog.md)
- [Stock Availability Rate](../metrics/stock_availability_rate.md)
