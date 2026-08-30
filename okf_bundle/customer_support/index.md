# Aurora Electronics Customer Support Bundle

This OKF bundle is the canonical source of truth for AI agents operating over
**Aurora Electronics** e-commerce customer support: product catalog, order
fulfillment, inventory, shipments, and returns/refunds.

## Datasets

* [Customer Products Database](./datasets/customer_products_db.md) - Structured PostgreSQL store for products, orders, and returns
* [Product Information Catalog](./datasets/product_information_catalog.md) - Unstructured product specs & descriptions (PDF, RAG-indexed)
* [Returns & Refunds Policy](./datasets/returns_refunds_policy.md) - Unstructured returns/refunds policy document (PDF, RAG-indexed)
* [Technical Support Guide](./datasets/technical_support_guide.md) - Unstructured troubleshooting guide (PDF, RAG-indexed)

## Tables

* [Products](./tables/products.md) - Master product catalog entries
* [Product Variants](./tables/product_variants.md) - Purchasable SKUs (color/switch-type/size) per product
* [Product Pricing](./tables/product_pricing.md) - Live, promo-aware price per SKU
* [Warehouses](./tables/warehouses.md) - Fulfillment warehouse locations
* [Inventory](./tables/inventory.md) - Per-SKU, per-warehouse stock levels
* [Customers](./tables/customers.md) - Customers who have placed orders
* [Orders](./tables/orders.md) - Order headers and current status
* [Order Items](./tables/order_items.md) - SKU line items within an order
* [Shipments](./tables/shipments.md) - Shipment/parcel tracking
* [Order Status History](./tables/order_status_history.md) - Append-only order status audit trail
* [Return Requests](./tables/return_requests.md) - Customer return/refund requests
* [Return Window Policy](./tables/return_window_policy.md) - Return window & condition rules per category
* [Refunds](./tables/refunds.md) - Refunds issued against return requests
* [Item Condition Flags](./tables/item_condition_flags.md) - Per-item return-eligibility exclusion flags

## Metrics

* [On-Time Delivery Rate](./metrics/on_time_delivery_rate.md) - % of delivered orders that arrived on or before the estimated date
* [Return Rate](./metrics/return_rate.md) - % of delivered order items returned
* [Refund Turnaround Time](./metrics/refund_turnaround_time.md) - Average days from return request to refund completion
* [Stock Availability Rate](./metrics/stock_availability_rate.md) - % of active SKUs currently in stock

## Runbooks

* [Return Eligibility Review](./runbooks/return_eligibility_review.md) - Deciding ELIGIBLE/INELIGIBLE/ESCALATED on a return request
* [Shipment Exception Handling](./runbooks/shipment_exception_handling.md) - Resolving carrier exceptions and delivery delays
* [Low Stock Restock Escalation](./runbooks/low_stock_restock_escalation.md) - Escalating SKUs at or below reorder threshold
