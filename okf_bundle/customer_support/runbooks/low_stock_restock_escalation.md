---
type: Runbook
title: Low Stock Restock Escalation
description: Process for escalating SKUs that have fallen at or below their reorder threshold, or gone out of stock with no restock ETA.
domain: customer_support
tags: [inventory, procurement, stock, workflow]
timestamp: 2026-08-21T09:00:00Z
---

# Low Stock Restock Escalation Workflow

## When Is This Runbook Triggered?

1. An [inventory](../tables/inventory.md) row's available quantity
   (`quantity_on_hand - quantity_reserved`) falls at or below
   `reorder_threshold`.
2. A SKU reaches `quantity_on_hand = 0` with no `restock_eta_date` set.
3. A customer support agent needs an ETA for an out-of-stock SKU a customer
   is asking about.

## Steps

### Step 1: Identify At-Risk SKUs
```sql
SELECT sku, warehouse_id, quantity_on_hand, quantity_reserved,
       reorder_threshold, restock_eta_date
FROM inventory
WHERE (quantity_on_hand - quantity_reserved) <= reorder_threshold
ORDER BY (quantity_on_hand - quantity_reserved) ASC;
```

### Step 2: Check for an Existing Restock Plan
- If `restock_eta_date` is set and in the future: no action needed, monitor.
- If `restock_eta_date` is NULL and `quantity_on_hand = 0`: escalate to
  procurement immediately (Step 3).
- If below threshold but `quantity_on_hand > 0`: flag as "monitor", raise a
  standard (non-urgent) procurement request.

### Step 3: Escalate to Procurement
Raise a purchase/restock request referencing the
[product](../tables/products.md) and [warehouse](../tables/warehouses.md).
Include current sell-through context from
[Stock Availability Rate](../metrics/stock_availability_rate.md) if the
whole category is trending low.

### Step 4: Update the Record
Once procurement confirms a restock date, update `restock_eta_date` on the
[inventory](../tables/inventory.md) row. Customer support can now share
this ETA on `OUT_OF_STOCK_RESTOCKING` inquiries.

### Step 5: Close Out
When new stock is received, update `quantity_on_hand` and clear
`restock_eta_date`.

## SLA

SKUs with `quantity_on_hand = 0` and no restock plan must be escalated to
procurement within **24 hours** of detection.

## Related

- [Inventory](../tables/inventory.md)
- [Warehouses](../tables/warehouses.md)
- [Products](../tables/products.md)
- [Stock Availability Rate](../metrics/stock_availability_rate.md)
