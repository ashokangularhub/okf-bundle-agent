---
type: Table
title: Refunds
description: One row per refund actually issued, post quality-check approval.
resource: postgresql://postgres:5432/common_knowledgebase_db/customer_support.refunds
domain: customer_support
tags: [refunds, payments, returns]
timestamp: 2026-08-21T09:00:00Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `refund_id` | VARCHAR(20) PK | e.g. `RFD-2026-00298`. |
| `return_id` | VARCHAR(20) | FK to [return_requests](./return_requests.md). |
| `refund_amount` | DECIMAL(10,2) | |
| `refund_method` | VARCHAR(30) | One of: `ORIGINAL_CARD`, `UPI`, `BANK_TRANSFER`, `WALLET_CREDIT`. |
| `refund_status` | VARCHAR(20) | One of: `INITIATED`, `PROCESSING`, `COMPLETED`, `FAILED`. Default `INITIATED`. |
| `bonus_credit_applied` | BOOLEAN | Fast-track wallet bonus. Default `FALSE`. |
| `initiated_at` / `completed_at` | TIMESTAMP | |

# Business Rules

- Only created after a [return_requests](./return_requests.md) row's
  `quality_check_status = PASSED`.
- `completed_at - initiated_at` is the turnaround time tracked by
  [Refund Turnaround Time](../metrics/refund_turnaround_time.md).

# Common Queries

**Was a refund issued for a return?**
```sql
SELECT refund_status, refund_amount, refund_method, completed_at
FROM refunds
WHERE return_id = 'RET-2026-00312';
```

# Related Concepts

- [Return Requests](./return_requests.md)
- [Refund Turnaround Time](../metrics/refund_turnaround_time.md)
