---
type: Dataset
title: Product Information Catalog
description: Unstructured product specifications, descriptions, and compatibility notes for the Aurora product line, ingested for retrieval-augmented generation (RAG).
resource: weaviate://localhost:8080/AURORA_PRODUCT
domain: customer_support
tags: [products, catalog, unstructured, rag, pdf]
timestamp: 2026-08-21T09:00:00Z
---

# Product Information Catalog

Source document: `files/aurora_product_information_catalog.pdf`. Contains
narrative product descriptions, specifications, and device-compatibility
tables for the 5 Aurora product lines (AuroraBuds Pro 2, AuroraWatch Fit 3,
AuroraSound Go, AuroraDesk Rise, AuroraType K5) that complement the
structured [products](../tables/products.md) /
[product_variants](../tables/product_variants.md) lookup tables — live
price/SKU/stock data stays in the database; descriptive spec content stays
in this PDF.

## Access

Ingested by `rag-pipeline` into the Weaviate collection `AURORA_PRODUCT`
(doc_type `product_catalog`). Query via `rag-pipeline`'s `POST /retrieve`
(collection=`AURORA_PRODUCT`) or `rag-retrieval`'s `POST /query` for an
LLM-synthesized answer.

## Related Concepts

- [Products](../tables/products.md)
- [Product Variants](../tables/product_variants.md)
- [Stock Availability Rate](../metrics/stock_availability_rate.md)
