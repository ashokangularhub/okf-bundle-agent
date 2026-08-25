"""
agents/section_selection.py — Agent: SectionSelectionAgent

Maps user query to exactly one OKF section:
'Tables', 'Metrics', 'Runbooks', or 'Datasets'.
"""

from __future__ import annotations

import logging

from .base import AgentState, BaseAgent
from .llm import call_llm

logger = logging.getLogger("okf_bundle.agents.section_selection")


class SectionSelectionAgent(BaseAgent):
    """
    LLM agent that routes a user query to the most relevant OKF section.
    """

    name = "SectionSelectionAgent"

    _VALID_SECTIONS = {"Tables", "Metrics", "Runbooks", "Datasets"}
    _VALID_DOMAINS = {"retail_banking", "customer_support"}

    _SYSTEM = (
        "You are a query router for a multi-domain knowledge system covering "
        "both retail banking (ClearBank) and e-commerce customer/product support "
        "(Aurora Electronics).\n\n"
        "Choose the SINGLE most relevant OKF section for the user's query:\n\n"
        "**Tables**: SQL data queries about specific entities or records\n"
        "  - 'Show me customers who...', 'List loans with status X', 'Find accounts belonging to Y'\n"
        "  - 'Where is order X?', 'List returns for customer Y', 'Show SKUs out of stock'\n"
        "  - Queries requesting: details, listings, specific records, filtered data\n"
        "  - Examples: 'Show delinquent loans', 'List frozen accounts', 'Where is my order ORD-2026-00841?'\n"
        "  - Key indicators: specific customer/loan/account/order/product details, data lookups\n\n"
        "**Metrics**: Aggregate statistics, KPI computations, rates, and ratios\n"
        "  - 'What is the delinquency rate?', 'Calculate NPA ratio', 'Transaction success rate'\n"
        "  - 'What is the return rate?', 'On-time delivery rate this month', 'Stock availability rate'\n"
        "  - Queries requesting: percentages, averages, counts, aggregates\n"
        "  - Examples: 'Delinquency rate by month', 'Average refund turnaround time'\n"
        "  - Key indicators: rate, ratio, average, count, percentage, aggregate\n\n"
        "**Runbooks**: Operational procedures and workflows\n"
        "  - 'How to investigate an AML alert?', 'Steps for loan restructuring', 'KYC renewal process'\n"
        "  - 'How do I review a return request?', 'Steps for a shipment exception', 'Low stock escalation process'\n"
        "  - Queries requesting: procedures, steps, workflows, processes, instructions\n"
        "  - Examples: 'AML investigation steps', 'Return eligibility review process'\n"
        "  - Key indicators: how to, steps, process, procedure, workflow\n\n"
        "**Datasets**: Database/storage metadata and retention policies\n"
        "  - 'Where is customer data stored?', 'Data retention policy', 'Backup schedule'\n"
        "  - 'Where is the product catalog PDF indexed?', 'What database backs orders?'\n"
        "  - Queries requesting: storage info, retention policies, metadata\n"
        "  - Examples: 'Data retention period', 'Where is customer PII stored', 'Backup frequency'\n"
        "  - Key indicators: metadata, storage, retention, policy, where is\n\n"
        "ALSO identify which domain the query belongs to:\n"
        "  - \"retail_banking\": customers, accounts, transactions, loans, payments, flags, KYC, AML\n"
        "  - \"customer_support\": products, orders, shipments, inventory, returns, refunds, warehouses\n"
        "  - If genuinely ambiguous or spans both, omit the domain field.\n\n"
        "Respond ONLY with valid JSON: "
        "{\"section\": \"<Tables|Metrics|Runbooks|Datasets>\", "
        "\"domain\": \"<retail_banking|customer_support|null>\"}"
    )

    def run(self, state: AgentState) -> AgentState:
        logger.info("[%s] Selecting OKF section.", self.name)
        logger.debug("[%s] Query: %s", self.name, state.user_query[:200])

        result = call_llm(self._SYSTEM, state.user_query, json_mode=True)
        logger.debug("[%s] LLM result: %s", self.name, result)

        sec: str = (
            result.get("section", "Tables") if isinstance(
                result, dict) else str(result)
        ).strip()

        if sec not in self._VALID_SECTIONS:
            for v in self._VALID_SECTIONS:
                if v.lower() == sec.lower():
                    sec = v
                    break
            else:
                logger.warning(
                    "[%s] Unknown section '%s', defaulting to Tables.", self.name, sec
                )
                sec = "Tables"

        state.section_type = sec

        dom = result.get("domain") if isinstance(result, dict) else None
        dom = str(dom).strip() if dom else ""
        if dom and dom.lower() not in self._VALID_DOMAINS:
            for v in self._VALID_DOMAINS:
                if v.lower() == dom.lower():
                    dom = v
                    break
            else:
                logger.warning(
                    "[%s] Unknown domain '%s', leaving unset (all domains).", self.name, dom
                )
                dom = ""
        state.domain = dom

        logger.info(
            "[%s] ✅ SECTION SELECTED: %s (domain=%s)\n"
            "[%s] Query was routed to: %s section\n"
            "[%s] This section will load: %s concepts",
            self.name, state.section_type, state.domain or "all",
            self.name, state.section_type,
            self.name, "20 Tables" if sec == "Tables" else "8 Metrics" if sec == "Metrics" else "6 Runbooks" if sec == "Runbooks" else "5 Datasets"
        )
        return state
