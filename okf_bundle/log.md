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

## 2026-07-20

- Drafted dataset description for retail_bank database.
- Defined table schemas with business rules and foreign key relationships.
