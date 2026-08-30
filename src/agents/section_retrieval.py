"""
agents/section_retrieval.py — Agent: SectionRetrievalAgent

Reads OKF bundle markdown files using BundleNavigator and
concatenates all concept files for the selected section into state.okf_content.
"""

from __future__ import annotations

import logging

from .base import AgentState, BaseAgent
from ..config import settings
from ..okf_parser import MultiDomainBundleNavigator

logger = logging.getLogger("okf_bundle.agents.section_retrieval")

# Fallback file mappings if BundleNavigator fails. Paths are relative to
# settings.BUNDLE_ROOT and rooted under each domain's standalone bundle
# directory (okf_bundle/retail_bank_database/, okf_bundle/customer_support/).
SECTION_FILES: dict[str, dict[str, list[str]]] = {
    "Tables": {
        "retail_banking": [
            "retail_bank_database/tables/bank_customers.md",
            "retail_bank_database/tables/bank_accounts.md",
            "retail_bank_database/tables/transactions.md",
            "retail_bank_database/tables/loans.md",
            "retail_bank_database/tables/loan_payments.md",
            "retail_bank_database/tables/flags.md",
        ],
        "customer_support": [
            "customer_support/tables/products.md",
            "customer_support/tables/product_variants.md",
            "customer_support/tables/product_pricing.md",
            "customer_support/tables/warehouses.md",
            "customer_support/tables/inventory.md",
            "customer_support/tables/customers.md",
            "customer_support/tables/orders.md",
            "customer_support/tables/order_items.md",
            "customer_support/tables/shipments.md",
            "customer_support/tables/order_status_history.md",
            "customer_support/tables/return_requests.md",
            "customer_support/tables/return_window_policy.md",
            "customer_support/tables/refunds.md",
            "customer_support/tables/item_condition_flags.md",
        ],
    },
    "Metrics": {
        "retail_banking": [
            "retail_bank_database/metrics/loan_delinquency_rate.md",
            "retail_bank_database/metrics/npa_ratio.md",
            "retail_bank_database/metrics/transaction_success_rate.md",
            "retail_bank_database/metrics/kyc_completion_rate.md",
        ],
        "customer_support": [
            "customer_support/metrics/on_time_delivery_rate.md",
            "customer_support/metrics/return_rate.md",
            "customer_support/metrics/refund_turnaround_time.md",
            "customer_support/metrics/stock_availability_rate.md",
        ],
    },
    "Runbooks": {
        "retail_banking": [
            "retail_bank_database/runbooks/aml_alert_investigation.md",
            "retail_bank_database/runbooks/loan_restructuring.md",
            "retail_bank_database/runbooks/kyc_renewal.md",
        ],
        "customer_support": [
            "customer_support/runbooks/return_eligibility_review.md",
            "customer_support/runbooks/shipment_exception_handling.md",
            "customer_support/runbooks/low_stock_restock_escalation.md",
        ],
    },
    "Datasets": {
        "retail_banking": [
            "retail_bank_database/datasets/retail_bank.db.md",
        ],
        "customer_support": [
            "customer_support/datasets/customer_products_db.md",
            "customer_support/datasets/product_information_catalog.md",
            "customer_support/datasets/returns_refunds_policy.md",
            "customer_support/datasets/technical_support_guide.md",
        ],
    },
}


class SectionRetrievalAgent(BaseAgent):
    """
    Tool agent that reads OKF bundle markdown files from disk using BundleNavigator.
    Concatenates all concept files for the identified section into state.okf_content.
    """

    name = "SectionRetrievalAgent"

    def run(self, state: AgentState) -> AgentState:
        logger.info(
            "[%s] ════════════════════════════════════════\n"
            "[%s] SECTION RETRIEVAL STARTED\n"
            "[%s] Section Type: %s\n"
            "[%s] Domain: %s\n"
            "[%s] ════════════════════════════════════════",
            self.name, self.name, self.name, state.section_type, self.name, state.domain or "all", self.name
        )

        try:
            nav = MultiDomainBundleNavigator(settings.BUNDLE_ROOTS)
            logger.debug(
                "[%s] MultiDomainBundleNavigator created, loading section...", self.name)

            concepts = nav.load_section(
                state.section_type, domain=state.domain or None)
            logger.info(
                "[%s] BundleNavigator loaded %d concepts from %s section",
                self.name, len(concepts), state.section_type
            )

            # Log what concepts were loaded
            if concepts:
                concept_titles = [c.title for c in concepts]
                logger.info(
                    "[%s] Loaded concepts: %s",
                    self.name, ", ".join(concept_titles)
                )

                # Show specific for Tables section
                if state.section_type == "Tables":
                    has_loans = any("loan" in c.title.lower()
                                    for c in concepts)
                    has_customers = any("customer" in c.title.lower()
                                        for c in concepts)
                    has_payments = any("payment" in c.title.lower()
                                       for c in concepts)
                    logger.info(
                        "[%s] Tables loaded - Loans: %s, Customers: %s, Loan Payments: %s",
                        self.name, "✓" if has_loans else "✗",
                        "✓" if has_customers else "✗",
                        "✓" if has_payments else "✗"
                    )

            if concepts:
                parts = [
                    f"## {c.title} (type: {c.concept_type})\n\n{c.body}"
                    for c in concepts
                ]
                state.okf_content = "\n\n---\n\n".join(parts)
                logger.info(
                    "[%s] ✅ SECTION LOADED:\n"
                    "[%s] Concepts: %d\n"
                    "[%s] Content size: %d chars",
                    self.name, self.name, len(
                        concepts), self.name, len(state.okf_content)
                )
            else:
                logger.warning(
                    "[%s] BundleNavigator returned 0 concepts; falling back to direct file read.",
                    self.name,
                )
                self._fallback_file_read(state)
        except Exception as exc:
            logger.error(
                "[%s] BundleNavigator failed: %s. Using fallback.", self.name, exc)
            self._fallback_file_read(state)

        if not state.okf_content:
            state.okf_content = "(No OKF content found.)"
            logger.warning("[%s] No content found for section %s",
                           self.name, state.section_type)

        return state

    def _fallback_file_read(self, state: AgentState) -> None:
        """Fallback: read section files directly from disk, filtered by domain."""
        by_domain = SECTION_FILES.get(state.section_type, {})
        domains = [state.domain] if state.domain else list(by_domain.keys())
        rel_paths = [p for d in domains for p in by_domain.get(d, [])]

        parts = []
        for rel_path in rel_paths:
            full_path = settings.BUNDLE_ROOT / rel_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    parts.append(f"## {full_path.name}\n\n{content}")
                except Exception as exc:
                    logger.warning("[%s] Failed to read %s: %s",
                                   self.name, full_path, exc)
        state.okf_content = "\n\n---\n\n".join(parts) if parts else ""
