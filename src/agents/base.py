"""
agents/base.py — Shared state and base class for all agents

All agents inherit from BaseAgent and operate on AgentState.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger("okf_bundle.agents")


@dataclass
class AgentState:
    """
    Mutable state object threaded through agents in the pipeline.
    Each agent reads from and writes to this shared state.
    """
    user_query: str
    conversation_history: list = field(default_factory=list)
    section_type: str = ""  # "Tables" | "Metrics" | "Runbooks" | "Datasets"
    domain: str = ""  # "retail_banking" | "customer_support"; "" = all domains
    okf_content: str = ""
    system_context: str = ""
    final_answer: str = ""
    error: str = ""


class BaseAgent:
    """Abstract base class for all bundle agents."""

    name: str = "BaseAgent"

    def run(self, state: AgentState) -> AgentState:
        raise NotImplementedError(f"{self.name}.run() not implemented")

    def __repr__(self) -> str:
        return f"<{self.name}>"
