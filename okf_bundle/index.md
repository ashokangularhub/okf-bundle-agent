# Multi-Domain Knowledge Bundle

This OKF bundle contains curated knowledge reused across multiple projects.
It is the canonical source of truth for AI agents operating over:

- **ClearBank** retail banking (customer accounts, loans, transactions, compliance)
- **Aurora Electronics** customer support (product catalog, order fulfillment, returns/refunds)

Table, metric, and runbook names are kept unique across domains so this
single bundle can be safely queried by any consuming project.

## Datasets

* [Retail Bank Database](./datasets/retail_bank.db.md) - Core banking data store
* [Customer Products Database](./datasets/customer_products_db.md) - Structured PostgreSQL store for products, orders, and returns
* [Product Information Catalog](./datasets/product_information_catalog.md) - Unstructured product specs & descriptions (PDF, RAG-indexed)
* [Returns & Refunds Policy](./datasets/returns_refunds_policy.md) - Unstructured returns/refunds policy document (PDF, RAG-indexed)
* [Technical Support Guide](./datasets/technical_support_guide.md) - Unstructured troubleshooting guide (PDF, RAG-indexed)

## Tables

* [Bank Customers](./tables/bank_customers.md) - KYC-verified customer profiles
* [Bank Accounts](./tables/bank_accounts.md) - Savings, checking, and fixed-deposit accounts
* [Transactions](./tables/transactions.md) - All debit/credit/transfer events
* [Loans](./tables/loans.md) - Loan applications and lifecycle
* [Loan Payments](./tables/loan_payments.md) - EMI schedule and payment history
* [Flags](./tables/flags.md) - Fraud, AML, and compliance alerts
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

* [Loan Delinquency Rate](./metrics/loan_delinquency_rate.md) - % of active loans overdue
* [NPA Ratio](./metrics/npa_ratio.md) - Non-performing asset ratio
* [Transaction Success Rate](./metrics/transaction_success_rate.md) - % of transactions completed
* [KYC Completion Rate](./metrics/kyc_completion_rate.md) - % of customers with verified KYC
* [On-Time Delivery Rate](./metrics/on_time_delivery_rate.md) - % of delivered orders that arrived on or before the estimated date
* [Return Rate](./metrics/return_rate.md) - % of delivered order items returned
* [Refund Turnaround Time](./metrics/refund_turnaround_time.md) - Average days from return request to refund completion
* [Stock Availability Rate](./metrics/stock_availability_rate.md) - % of active SKUs currently in stock

## Runbooks

* [AML Alert Investigation](./runbooks/aml_alert_investigation.md) - Anti-money laundering review steps
* [Loan Restructuring](./runbooks/loan_restructuring.md) - Workflow for restructuring delinquent loans
* [KYC Renewal](./runbooks/kyc_renewal.md) - Steps for expired KYC re-verification
* [Return Eligibility Review](./runbooks/return_eligibility_review.md) - Deciding ELIGIBLE/INELIGIBLE/ESCALATED on a return request
* [Shipment Exception Handling](./runbooks/shipment_exception_handling.md) - Resolving carrier exceptions and delivery delays
* [Low Stock Restock Escalation](./runbooks/low_stock_restock_escalation.md) - Escalating SKUs at or below reorder threshold
