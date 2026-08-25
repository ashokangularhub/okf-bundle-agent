---
type: Dataset
title: Returns & Refunds Policy
description: Unstructured policy document defining return windows, eligibility conditions, and refund rules by product category, ingested for RAG.
resource: weaviate://localhost:8080/AURORA_RETURNS_REFUNDS
domain: customer_support
tags: [returns, refunds, policy, unstructured, rag, pdf]
timestamp: 2026-08-21T09:00:00Z
---

# Returns & Refunds Policy

Source document: `files/aurora_returns_refunds_policy.pdf`. Defines the
policy rules (return windows, condition requirements, refund methods,
exclusions) that the structured [return_requests](../tables/return_requests.md) /
[return_window_policy](../tables/return_window_policy.md) /
[item_condition_flags](../tables/item_condition_flags.md) tables enforce as
queryable facts. Agent pattern: retrieve the policy rule from this PDF
(RAG), then check the structured facts (SQL), then apply the rule.

## Access

Ingested by `rag-pipeline` into the Weaviate collection
`AURORA_RETURNS_REFUNDS` (doc_type `returns_refunds_policy`).

## Related Concepts

- [Return Requests](../tables/return_requests.md)
- [Return Window Policy](../tables/return_window_policy.md)
- [Item Condition Flags](../tables/item_condition_flags.md)
- [Return Eligibility Review](../runbooks/return_eligibility_review.md)
- [Return Rate](../metrics/return_rate.md)
