# Change Log

## 2026-08-30

- Segregated the single flat `okf_bundle/` into two standalone bundles:
  `okf_bundle/retail_bank_database/` (ClearBank) and
  `okf_bundle/customer_support/` (Aurora Electronics). Each is a complete
  bundle with its own `index.md` and `tables/`/`metrics/`/`runbooks/`/`datasets/`
  subfolders. Files were moved with no content changes (`domain:` frontmatter
  retained for backward compatibility). `BundleNavigator` now targets one
  bundle root at a time; `MultiDomainBundleNavigator` (new, in `okf_parser.py`)
  fans a request out across both bundles when no domain is specified, so the
  public REST API and `state.domain` filtering behavior are unchanged.

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
