---
type: Metric
title: Refund Turnaround Time
description: Average number of days between a return request being submitted and its refund being completed. Target is <= 5 days.
domain: customer_support
tags: [refunds, returns, kpi, sla]
timestamp: 2026-08-21T09:00:00Z
---

# Definition

Refund Turnaround Time = average of (`refunds.completed_at` -
`return_requests.requested_at`) in days, for refunds with
`refund_status = 'COMPLETED'`.

# SQL

```sql
SELECT
    ROUND(
        AVG(julianday(rf.completed_at) - julianday(rr.requested_at)),
        2
    ) AS avg_turnaround_days
FROM refunds rf
JOIN return_requests rr ON rr.return_id = rf.return_id
WHERE rf.refund_status = 'COMPLETED';
```

**Refunds still in flight (not yet completed):**
```sql
SELECT rf.refund_id, rf.return_id, rf.refund_status,
       ROUND(julianday('now') - julianday(rf.initiated_at), 1) AS days_open
FROM refunds rf
WHERE rf.refund_status IN ('INITIATED', 'PROCESSING')
ORDER BY days_open DESC;
```

# Source Tables

- [Refunds](../tables/refunds.md)
- [Return Requests](../tables/return_requests.md)

# Thresholds

| Level    | Value        |
|----------|--------------|
| Healthy  | <= 5 days    |
| Warning  | 5 - 10 days  |
| Critical | > 10 days    |
