---
type: Table
title: Return Window Policy
description: Queryable mirror of the Returns & Refunds Policy PDF's return-window rules, keyed by product category — avoids re-parsing the PDF for every eligibility check.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.return_window_policy
domain: customer_support
tags: [returns, policy, eligibility]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `category` | VARCHAR(50) PK | Matches [products](./products.md).`category`. |
| `window_days` | INT | Return window length in days from delivery. |
| `condition_requirement` | VARCHAR(200) | Free-text condition needed to qualify. |

Seed values: `Earbuds`=10 days, `Smartwatch`=15 days, `Speaker`=10 days,
`Accessory`=7 days, `Keyboard`=15 days.

# Business Rules

- Kept in sync with the PDF policy **manually** on policy review — this is
  a cache of the policy text for SQL joins, not an independent source of
  truth. If the two disagree, the PDF is authoritative and this table must
  be corrected.
- `days_remaining_in_window = window_days - (CURRENT_DATE - actual_delivery_date)`;
  a value <= 0 means the window has closed.

# Common Queries

**Return window for a category:**
```sql
SELECT window_days, condition_requirement
FROM return_window_policy
WHERE category = 'Keyboard';
```

# Related Concepts

- [Products](./products.md)
- [Return Requests](./return_requests.md)
- [Returns & Refunds Policy](../datasets/returns_refunds_policy.md)
- [Return Eligibility Review](../runbooks/return_eligibility_review.md)
