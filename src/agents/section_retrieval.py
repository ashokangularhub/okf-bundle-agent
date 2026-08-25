"""
agents/section_retrieval.py — Agent: SectionRetrievalAgent

Reads OKF bundle markdown files using BundleNavigator and
concatenates all concept files for the selected section into state.okf_content.
"""

from __future__ import annotations

import logging

from .base import AgentState, BaseAgent
from ..config import settings
from ..okf_parser import BundleNavigator

logger = logging.getLogger("okf_bundle.agents.section_retrieval")

# Fallback file mappings if BundleNavigator fails
SECTION_FILES: dict[str, list[str]] = {
    "Tables": [
        "tables/bank_customers.md",
        "tables/bank_accounts.md",
        "tables/transactions.md",
        "tables/loans.md",
        "tables/loan_payments.md",
        "tables/flags.md",
        "tables/products.md",
        "tables/product_variants.md",
        "tables/product_pricing.md",
        "tables/warehouses.md",
        "tables/inventory.md",
        "tables/customers.md",
        "tables/orders.md",
        "tables/order_items.md",
        "tables/shipments.md",
        "tables/order_status_history.md",
        "tables/return_requests.md",
        "tables/return_window_policy.md",
        "tables/refunds.md",
        "tables/item_condition_flags.md",
    ],
    "Metrics": [
        "metrics/loan_delinquency_rate.md",
        "metrics/npa_ratio.md",
        "metrics/transaction_success_rate.md",
        "metrics/kyc_completion_rate.md",
        "metrics/on_time_delivery_rate.md",
        "metrics/return_rate.md",
        "metrics/refund_turnaround_time.md",
        "metrics/stock_availability_rate.md",
    ],
    "Runbooks": [
        "runbooks/aml_alert_investigation.md",
        "runbooks/loan_restructuring.md",
        "runbooks/kyc_renewal.md",
        "runbooks/return_eligibility_review.md",
        "runbooks/shipment_exception_handling.md",
        "runbooks/low_stock_restock_escalation.md",
    ],
    "Datasets": [
        "datasets/retail_bank.db.md",
        "datasets/customer_products_db.md",
        "datasets/product_information_catalog.md",
        "datasets/returns_refunds_policy.md",
        "datasets/technical_support_guide.md",
    ],
}

# domain each fallback file belongs to, used to filter SECTION_FILES by state.domain
_RETAIL_BANKING_FILES = {
    "tables/bank_customers.md", "tables/bank_accounts.md", "tables/transactions.md",
    "tables/loans.md", "tables/loan_payments.md", "tables/flags.md",
    "metrics/loan_delinquency_rate.md", "metrics/npa_ratio.md",
    "metrics/transaction_success_rate.md", "metrics/kyc_completion_rate.md",
    "runbooks/aml_alert_investigation.md", "runbooks/loan_restructuring.md",
    "runbooks/kyc_renewal.md", "datasets/retail_bank.db.md",
}
FILE_DOMAINS: dict[str, str] = {
    path: ("retail_banking" if path in _RETAIL_BANKING_FILES else "customer_support")
    for paths in SECTION_FILES.values()
    for path in paths
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
            nav = BundleNavigator(str(settings.BUNDLE_ROOT))
            logger.debug(
                "[%s] BundleNavigator created, loading section...", self.name)

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
        parts = []
        for rel_path in SECTION_FILES.get(state.section_type, []):
            if state.domain and FILE_DOMAINS.get(rel_path) != state.domain:
                continue
            full_path = settings.BUNDLE_ROOT / rel_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    parts.append(f"## {full_path.name}\n\n{content}")
                except Exception as exc:
                    logger.warning("[%s] Failed to read %s: %s",
                                   self.name, full_path, exc)
        state.okf_content = "\n\n---\n\n".join(parts) if parts else ""
