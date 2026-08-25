---
type: Table
title: Item Condition Flags
description: Per-order-item condition flags that make an item ineligible for return regardless of window — e.g. already returned, customer-modified, part of a bundle.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.item_condition_flags
domain: customer_support
tags: [returns, eligibility, exclusions]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `order_item_id` | BIGINT PK | FK to [order_items](./order_items.md). |
| `already_returned` | BOOLEAN | Default `FALSE`. |
| `modified_by_customer` | BOOLEAN | e.g. hot-swapped keyboard switches. Default `FALSE`. |
| `is_bundle_component` | BOOLEAN | Part of a promo bundle. Default `FALSE`. |
| `damage_reported_at` | TIMESTAMP | For the 48-hour transit-damage window check. |
| `notes` | VARCHAR(200) | |

# Business Rules

- Any of `already_returned = TRUE` or `modified_by_customer = TRUE` should
  short-circuit an eligibility check to `INELIGIBLE` regardless of
  `return_window_policy.window_days` remaining.
- `damage_reported_at` populated means the customer reported transit
  damage; the policy PDF's 48-hour damage-claim window applies instead of
  the standard category return window.

# Common Queries

**Items ineligible due to prior modification or return:**
```sql
SELECT order_item_id, already_returned, modified_by_customer, notes
FROM item_condition_flags
WHERE already_returned = TRUE OR modified_by_customer = TRUE;
```

# Related Concepts

- [Order Items](./order_items.md)
- [Return Requests](./return_requests.md)
- [Return Eligibility Review](../runbooks/return_eligibility_review.md)
