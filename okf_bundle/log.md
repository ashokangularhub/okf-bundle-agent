# Change Log

## 2026-07-21

- Initial bundle creation for ClearBank retail banking platform.
- Added six core tables: bank_customers, bank_accounts, transactions, loans, loan_payments, flags.
- Added four KPI metrics: delinquency rate, NPA ratio, transaction success rate, KYC completion rate.
- Added three operational runbooks: AML investigation, loan restructuring, KYC renewal.

## 2026-08-25

- Renamed `customers` table to `bank_customers` and `accounts` table to
  `bank_accounts` so the bundle can be reused as a knowledge base across
  multiple projects without naming collisions.
- Integrated the Aurora Electronics customer/product knowledge domain
  (from the `customer-product-okf-bundle` project) into this bundle:
  14 tables, 4 datasets, 4 metrics, 3 runbooks. Added as new entries
  alongside the existing ClearBank retail banking content — no existing
  files were modified or removed, and no naming collisions were found.

## 2026-07-20

- Drafted dataset description for retail_bank database.
- Defined table schemas with business rules and foreign key relationships.
