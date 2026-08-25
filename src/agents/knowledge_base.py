"""
agents/knowledge_base.py — Agent: KnowledgeBaseAgent

Handles queries over Runbooks and Datasets. Answers using OKF content
as the authoritative source.
"""

from __future__ import annotations

import logging

from .base import AgentState, BaseAgent
from .llm import call_llm

logger = logging.getLogger("okf_bundle.agents.knowledge_base")


class KnowledgeBaseAgent(BaseAgent):
    """
    LLM agent that handles non-SQL queries (Runbooks / Datasets branch).
    Answers using OKF content as the authoritative source and writes
    state.final_answer.
    """

    name = "KnowledgeBaseAgent"

    _SYSTEM = (
        "You are a knowledge base agent covering ClearBank retail banking "
        "and Aurora Electronics customer/product support.\n\n"
        "Answer the user's question using ONLY the provided OKF bundle content. "
        "Cite specific runbook steps, rules, or procedures where applicable. "
        "Format procedures as numbered steps. "
        "If the information is not in the provided content, say so explicitly."
    )

    def run(self, state: AgentState) -> AgentState:
        logger.info("[%s] Answering from OKF knowledge base.", self.name)
        user_msg = (
            f"User question: {state.user_query}\n\n"
            f"OKF Bundle Content:\n\n{state.okf_content}"
        )
        state.final_answer = call_llm(self._SYSTEM, user_msg)
        logger.info("[%s] Answer generated (%d chars).",
                    self.name, len(state.final_answer))
        return state
