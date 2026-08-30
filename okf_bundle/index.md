# OKF Knowledge Bundles

This directory hosts **two independent, domain-scoped OKF bundles**. Each is a
fully self-contained bundle with its own `index.md`, `tables/`, `metrics/`,
`runbooks/`, and `datasets/` sections, loaded by its own `BundleNavigator`
instance. There is no cross-bundle folder sharing or naming coupling.

- [retail_bank_database/](./retail_bank_database/index.md) — **ClearBank**
  retail banking (customer accounts, loans, transactions, compliance)
- [customer_support/](./customer_support/index.md) — **Aurora Electronics**
  customer support (product catalog, order fulfillment, returns/refunds)

`src/config.py` maps the `retail_banking` and `customer_support` domain
identifiers to these two directories (`Settings.BUNDLE_ROOTS`), and
`src/okf_parser.MultiDomainBundleNavigator` fans requests out to the correct
bundle(s) so callers can still request a single domain or, when a query is
ambiguous, both at once — with no change to the public REST API.

This file itself is a human-navigation landing page only; it is **not**
parsed by `BundleNavigator` (which always loads a single bundle's own root
`index.md`).
