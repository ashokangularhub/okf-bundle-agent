---
type: Runbook
title: Shipment Exception Handling
description: Workflow for investigating and resolving carrier shipment exceptions and orders at risk of missing their estimated delivery date.
domain: customer_support
tags: [shipments, logistics, delivery, workflow]
timestamp: 2026-08-21T09:00:00Z
---

# Shipment Exception Handling Workflow

## When Is This Runbook Triggered?

1. A [shipments](../tables/shipments.md) row transitions to
   `shipment_status = 'EXCEPTION'` with an `exception_reason` populated.
2. An order's `estimated_delivery_date` has passed but
   [orders](../tables/orders.md).`order_status` is not yet `DELIVERED`.
3. A customer contacts support asking "where is my order?" for a delayed
   shipment.

## Steps

### Step 1: Pull the Shipment & Order Timeline
```sql
SELECT o.order_id, o.order_status, o.estimated_delivery_date,
       s.shipment_id, s.carrier_name, s.tracking_number, s.shipment_status,
       s.current_location, s.exception_reason
FROM orders o
LEFT JOIN shipments s ON s.order_id = o.order_id
WHERE o.order_id = :order_id;
```
Cross-check against [order_status_history](../tables/order_status_history.md)
for the full status timeline.

### Step 2: Classify the Exception
- **Address/access issue** (e.g. "recipient unavailable", "incorrect
  address"): contact customer to confirm/update `orders.shipping_address`.
- **Carrier delay** (e.g. "weather", "hub congestion"): monitor, no
  customer action needed; update customer proactively if delay exceeds 2 days.
- **Lost/damaged in transit**: treat as a service failure — offer
  reshipment or refund without requiring a formal
  [return_requests](../tables/return_requests.md) (item was never received).

### Step 3: Resolution
- **Reship**: create a new [shipments](../tables/shipments.md) row for the
  same order; do not modify the exception row (append-only history).
- **Refund**: process directly (this is a delivery failure, not a return —
  skip [Return Eligibility Review](./return_eligibility_review.md)).
- **Escalate to carrier**: open a carrier claim for lost/damaged parcels
  above a value threshold (tracked outside this schema).

### Step 4: Update Records
Append a row to [order_status_history](../tables/order_status_history.md)
documenting the resolution and reason. Update `orders.order_status` if the
resolution changes it (e.g. back to `PACKED` for a reship).

## SLA

Shipment exceptions must be triaged within **24 hours** of the status
change. Customers must be proactively notified within **48 hours** if the
estimated delivery date will be missed.

## Related

- [Orders](../tables/orders.md)
- [Shipments](../tables/shipments.md)
- [Order Status History](../tables/order_status_history.md)
- [On-Time Delivery Rate](../metrics/on_time_delivery_rate.md)
