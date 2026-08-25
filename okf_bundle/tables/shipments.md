---
type: Table
title: Shipments
description: Shipment/parcel tracking. Separate from orders because a single order can ship in multiple parcels (split shipment).
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.shipments
domain: customer_support
tags: [shipments, logistics, tracking]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `shipment_id` | VARCHAR(20) PK | e.g. `SHP-2026-01552`. |
| `order_id` | VARCHAR(20) | FK to [orders](./orders.md). |
| `carrier_name` | VARCHAR(50) | e.g. `BlueDart`, `Delhivery`. |
| `tracking_number` | VARCHAR(50) | |
| `shipment_status` | VARCHAR(30) | One of: `LABEL_CREATED`, `IN_TRANSIT`, `OUT_FOR_DELIVERY`, `DELIVERED`, `EXCEPTION`. |
| `shipped_date` / `delivered_date` | TIMESTAMP | |
| `current_location` | VARCHAR(100) | |
| `exception_reason` | VARCHAR(200) | Populated only when `shipment_status = EXCEPTION`. |

# Business Rules

- `shipment_status = EXCEPTION` with a populated `exception_reason` is the
  trigger for [Shipment Exception Handling](../runbooks/shipment_exception_handling.md).
- An order can have a shipment with no tracking number yet
  (`LABEL_CREATED`, see seed row `SHP-2026-01505`).

# Common Queries

**Shipments currently in an exception state:**
```sql
SELECT shipment_id, order_id, carrier_name, exception_reason, current_location
FROM shipments
WHERE shipment_status = 'EXCEPTION';
```

# Related Concepts

- [Orders](./orders.md)
- [Shipment Exception Handling](../runbooks/shipment_exception_handling.md)
- [On-Time Delivery Rate](../metrics/on_time_delivery_rate.md)
