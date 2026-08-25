---
type: Table
title: Return Requests
description: One row per return request a customer initiates against an order_item. Header record for the returns/refunds workflow.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.return_requests
domain: customer_support
tags: [returns, refunds, eligibility, compliance]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `return_id` | VARCHAR(20) PK | e.g. `RET-2026-00312`. |
| `order_id` | VARCHAR(20) | FK to [orders](./orders.md). |
| `order_item_id` | BIGINT | FK to [order_items](./order_items.md). |
| `customer_id` | BIGINT | FK to [customers](./customers.md). |
| `return_reason` | VARCHAR(50) | e.g. `CHANGED_MIND`, `DEFECTIVE`. Matches the policy PDF's Section 3 reasons. |
| `return_reason_detail` | TEXT | Free-text customer explanation. |
| `requested_resolution` | VARCHAR(20) | One of: `REFUND`, `REPLACEMENT`. Default `REFUND`. |
| `return_status` | VARCHAR(30) | One of: `REQUESTED`, `APPROVED`, `REJECTED`, `ESCALATED_TO_HUMAN`, `ITEM_IN_TRANSIT`, `ITEM_RECEIVED`, `REFUND_PROCESSED`, `REPLACEMENT_SHIPPED`. Default `REQUESTED`. |
| `requested_at` | TIMESTAMP | |
| `eligibility_decision` | VARCHAR(20) | One of: `ELIGIBLE`, `INELIGIBLE`, `ESCALATED`. Set by the agent/analyst. |
| `eligibility_reason` | VARCHAR(200) | Which policy rule drove the decision. |
| `quality_check_status` | VARCHAR(20) | One of: `PENDING`, `PASSED`, `FAILED`. Set after warehouse receives item. |
| `resolved_at` | TIMESTAMP | |

# Business Rules

- Agent pattern: retrieve the applicable rule from the
  [Returns & Refunds Policy](../datasets/returns_refunds_policy.md) PDF (RAG),
  then check facts via [return_window_policy](./return_window_policy.md) and
  [item_condition_flags](./item_condition_flags.md) (SQL), then apply the
  rule and set `eligibility_decision`. See
  [Return Eligibility Review](../runbooks/return_eligibility_review.md).
- A second return request against an `order_item_id` that already has
  `already_returned = TRUE` set (see [item_condition_flags](./item_condition_flags.md))
  must be rejected or escalated, not auto-approved.
- `REFUND_PROCESSED` should always have a corresponding
  [refunds](./refunds.md) row.

# Common Queries

**Open return requests awaiting review:**
```sql
SELECT return_id, order_id, order_item_id, return_reason, requested_at
FROM return_requests
WHERE return_status = 'REQUESTED'
ORDER BY requested_at ASC;
```

**Return requests for a given order:**
```sql
SELECT return_id, return_reason, requested_resolution, return_status, eligibility_decision
FROM return_requests
WHERE order_id = 'ORD-2026-00841';
```

# Related Concepts

- [Orders](./orders.md)
- [Order Items](./order_items.md)
- [Return Window Policy](./return_window_policy.md)
- [Item Condition Flags](./item_condition_flags.md)
- [Refunds](./refunds.md)
- [Returns & Refunds Policy](../datasets/returns_refunds_policy.md)
- [Return Eligibility Review](../runbooks/return_eligibility_review.md)
- [Return Rate](../metrics/return_rate.md)
