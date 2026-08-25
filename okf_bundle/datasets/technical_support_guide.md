---
type: Dataset
title: Technical Support & Troubleshooting Guide
description: Unstructured troubleshooting guide for Aurora products, ingested for RAG-based technical support answers.
resource: weaviate://localhost:8080/AURORA_TECHNICAL_SUPPORT
domain: customer_support
tags: [support, troubleshooting, unstructured, rag, pdf]
timestamp: 2026-08-21T09:00:00Z
---

# Technical Support & Troubleshooting Guide

Source document: `files/aurora_technical_support_guide.pdf`. Contains
troubleshooting steps, FAQs, and diagnostic guidance for the Aurora product
line. Not tied to a structured table — pure narrative content, answered
directly from retrieved passages.

## Access

Ingested by `rag-pipeline` into the Weaviate collection
`AURORA_TECHNICAL_SUPPORT` (doc_type `technical_support_guide`).

## Related Concepts

- [Products](../tables/products.md)
