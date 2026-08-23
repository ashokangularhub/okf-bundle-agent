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

    _SYSTEM = (
        "You are a query router for a banking knowledge system.\n\n"
        "Choose the SINGLE most relevant OKF section for the user's query:\n\n"
        "**Tables**: SQL data queries about specific entities or records\n"
        "  - 'Show me customers who...', 'List loans with status X', 'Find accounts belonging to Y'\n"
        "  - Queries requesting: details, listings, specific records, filtered data\n"
        "  - Examples: 'Show delinquent loans', 'List frozen accounts', 'Customers with upcoming payments'\n"
        "  - Key indicators: specific customer/loan/account details, data lookups\n\n"
        "**Metrics**: Aggregate statistics, KPI computations, rates, and ratios\n"
        "  - 'What is the delinquency rate?', 'Calculate NPA ratio', 'Transaction success rate'\n"
        "  - Queries requesting: percentages, averages, counts, aggregates\n"
        "  - Examples: 'Delinquency rate by month', 'KYC completion percentage', 'Average loan amount'\n"
        "  - Key indicators: rate, ratio, average, count, percentage, aggregate\n\n"
        "**Runbooks**: Operational procedures and workflows\n"
        "  - 'How to investigate an AML alert?', 'Steps for loan restructuring', 'KYC renewal process'\n"
        "  - Queries requesting: procedures, steps, workflows, processes, instructions\n"
        "  - Examples: 'AML investigation steps', 'Loan restructuring procedure', 'KYC renewal checklist'\n"
        "  - Key indicators: how to, steps, process, procedure, workflow\n\n"
        "**Datasets**: Database/storage metadata and retention policies\n"
        "  - 'Where is customer data stored?', 'Data retention policy', 'Backup schedule'\n"
        "  - Queries requesting: storage info, retention policies, metadata\n"
        "  - Examples: 'Data retention period', 'Where is customer PII stored', 'Backup frequency'\n"
        "  - Key indicators: metadata, storage, retention, policy, where is\n\n"
        "Respond ONLY with valid JSON: {\"section\": \"<Tables|Metrics|Runbooks|Datasets>\"}"
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
        logger.info(
            "[%s] ✅ SECTION SELECTED: %s\n"
            "[%s] Query was routed to: %s section\n"
            "[%s] This section will load: %s concepts",
            self.name, state.section_type,
            self.name, state.section_type,
            self.name, "6 Tables" if sec == "Tables" else "4 Metrics" if sec == "Metrics" else "3 Runbooks" if sec == "Runbooks" else "1 Dataset"
        )
        return state
