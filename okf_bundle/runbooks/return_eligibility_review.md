---
type: Runbook
title: Return Eligibility Review
description: Step-by-step workflow for deciding whether a customer's return request is eligible, ineligible, or requires human escalation.
domain: customer_support
tags: [returns, refunds, eligibility, compliance, workflow]
timestamp: 2026-08-21T09:00:00Z
---

# Return Eligibility Review Workflow

## When Is This Runbook Triggered?

1. A [return_requests](../tables/return_requests.md) row is created with
   `return_status = 'REQUESTED'`.
2. A customer contacts support asking "can I return this?" before formally
   submitting a request.

## Steps

### Step 1: Retrieve the Policy Rule
Retrieve the applicable rule from the
[Returns & Refunds Policy](../datasets/returns_refunds_policy.md) PDF for
the item's `return_reason` (e.g. `CHANGED_MIND`, `DEFECTIVE`) — RAG lookup,
not SQL.

### Step 2: Gather the Facts
Query the structured facts for the `order_item_id`:

```sql
SELECT oi.order_item_id, o.order_status, o.actual_delivery_date,
       p.category, rwp.window_days, rwp.condition_requirement,
       (CURRENT_DATE - o.actual_delivery_date) AS days_since_delivery,
       icf.already_returned, icf.modified_by_customer,
       icf.is_bundle_component, icf.damage_reported_at
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN product_variants pv ON pv.sku = oi.sku
JOIN products p ON p.product_id = pv.product_id
LEFT JOIN return_window_policy rwp ON rwp.category = p.category
LEFT JOIN item_condition_flags icf ON icf.order_item_id = oi.order_item_id
WHERE oi.order_item_id = :order_item_id;
```

### Step 3: Apply Exclusions First
Before checking the window, reject/escalate immediately if any of:
- [item_condition_flags](../tables/item_condition_flags.md).`already_returned = TRUE`
  → `INELIGIBLE` ("already returned").
- `modified_by_customer = TRUE` → `INELIGIBLE` ("customer-modified item"),
  unless the policy PDF's category-specific exception applies.
- `orders.order_status = 'CANCELLED'` → nothing to return; handled by the
  cancellation flow, not this runbook.

### Step 4: Check the Return Window
- If `damage_reported_at` is set, apply the PDF's transit-damage window
  instead of the standard category window.
- Otherwise: `days_remaining_in_window = window_days - days_since_delivery`.
  - `> 0` and condition requirement met (per PDF) → `ELIGIBLE`.
  - `<= 0` → `INELIGIBLE` ("window closed").
  - Ambiguous condition (e.g. no clear opened/unopened state) → `ESCALATED`.

### Step 5: Record the Decision
Update [return_requests](../tables/return_requests.md):
- `eligibility_decision` (`ELIGIBLE` / `INELIGIBLE` / `ESCALATED`)
- `eligibility_reason` — cite the specific policy section/rule applied.
- If `ELIGIBLE` and `requested_resolution = 'REFUND'`: proceed to quality
  check on item receipt (`quality_check_status`), then create a
  [refunds](../tables/refunds.md) row once `PASSED`.
- If `ESCALATED`: set `return_status = 'ESCALATED_TO_HUMAN'`.

## SLA

Eligibility decisions must be made within **48 hours** of request submission.
Escalated cases must be picked up by a human reviewer within **24 hours**.

## Related

- [Return Requests](../tables/return_requests.md)
- [Return Window Policy](../tables/return_window_policy.md)
- [Item Condition Flags](../tables/item_condition_flags.md)
- [Returns & Refunds Policy](../datasets/returns_refunds_policy.md)
- [Return Rate](../metrics/return_rate.md)
- [Refund Turnaround Time](../metrics/refund_turnaround_time.md)
