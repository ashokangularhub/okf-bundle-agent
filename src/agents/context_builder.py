"""
agents/context_builder.py — Agent: ContextBuilderAgent

Transforms raw OKF section content into a structured system prompt
for use by SQL generation or other downstream agents.
"""

from __future__ import annotations

import logging
import re

from .base import AgentState, BaseAgent
from .llm import call_llm

logger = logging.getLogger("okf_bundle.agents.context_builder")


def extract_all_column_names(content: str) -> list[str]:
    """Extract all column names from a table's schema section."""
    schema_match = re.search(
        r"^#\s+Schema\s*\n(.*?)(?=\n#|\Z)",
        content,
        re.MULTILINE | re.DOTALL
    )
    if not schema_match:
        return []

    schema_section = schema_match.group(1)
    table_match = re.search(
        r"\|\s*Column\s*\|.*?\n.*?\n((?:\|.*?\n)*)",
        schema_section,
        re.MULTILINE
    )
    if not table_match:
        return []

    columns = []
    for line in table_match.group(1).split('\n'):
        line = line.strip()
        if line.startswith('|') and line.endswith('|') and '---' not in line:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) >= 1:
                col_name = cells[0]
                columns.append(col_name)

    return columns


def extract_table_name_from_markdown(content: str) -> str:
    """Extract the table name from markdown OKF content."""
    title_match = re.search(r"^title:\s*(.+?)$", content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        return "".join(word.capitalize() for word in title.split())

    resource_match = re.search(r"public\.(\w+)", content)
    if resource_match:
        table_name = resource_match.group(1)
        return "".join(word.capitalize() for word in table_name.split('_'))

    return ""


def extract_table_titles(content: str) -> list[str]:
    """
    Extract human-readable table titles from the '## <Title> (type: ...)'
    headers that SectionRetrievalAgent inserts for every concept in a
    section. A section (e.g. "Tables") concatenates MULTIPLE table files,
    so this always finds every table, unlike title/resource regexes that
    only match the first occurrence.
    """
    return list(dict.fromkeys(
        re.findall(r"^##\s+(.+?)\s+\(type:\s*\w+\)", content, re.MULTILINE)
    ))


def title_to_snake_case(title: str) -> str:
    """Convert a human-readable OKF title (e.g. 'Loan Payments') to the
    snake_case table name PostgreSQL actually uses (e.g. 'loan_payments')."""
    return re.sub(r"[\s\-]+", "_", title.strip().lower())


class ContextBuilderAgent(BaseAgent):
    """
    LLM agent that distills raw OKF content into a structured system prompt:
    tables, columns, ENUM values, JOIN paths, business rules, and metric formulas.
    """

    name = "ContextBuilderAgent"

    _SYSTEM = (
        "You are a context builder for a banking knowledge system.\n\n"
        "Given raw OKF knowledge bundle content, distill a concise but complete "
        "system context that includes:\n"
        "  1. **Table schemas**: EXACT column names (with types, ENUM values)\n"
        "  2. **Explicit JOIN paths**: e.g., 'Loans.customer_id → Customers.customer_id'\n"
        "  3. **Business rules and constraints** (status enums, thresholds, date ranges)\n"
        "  4. **Metric SQL formulas** if the section is Metrics\n"
        "  5. **Common queries** people ask (e.g., 'loan details with customer info')\n\n"
        "CRITICAL RULES:\n"
        "  - List EVERY column name EXACTLY as it appears in the schema\n"
        "  - NEVER invent, abbreviate, or derive column names\n"
        "  - Use full names like 'first_name', not 'fullName' or 'full name'\n"
        "  - Include column types and any constraints\n"
        "  - Explicitly list JOIN relationships for common queries\n"
        "  - If a column is defined, it MUST be spelled exactly as in schema\n"
        "  - NEVER refer to a table by its human-readable title (e.g. 'Loan Payments').\n"
        "    ALWAYS use the exact snake_case PostgreSQL table name (e.g. 'loan_payments').\n\n"
        "Keep it factual, structured, and actionable. Omit prose.\n"
        "This context feeds downstream SQL generation and knowledge base agents."
    )

    def run(self, state: AgentState) -> AgentState:
        logger.info("[%s] Building structured context.", self.name)

        # Extract table name and columns for reference
        table_name = extract_table_name_from_markdown(state.okf_content)
        all_columns = extract_all_column_names(state.okf_content)

        # A section (e.g. "Tables") concatenates MULTIPLE table files, each
        # under its own '## Title (type: ...)' header — collect every real
        # table name so we never imply that only one table exists.
        titles = extract_table_titles(state.okf_content)
        title_to_actual = {t: title_to_snake_case(t) for t in titles}

        # Build context with column reference
        user_msg = f"User query: {state.user_query}\n\n"

        if table_name and all_columns:
            user_msg += f"Table: {table_name}\n"
            user_msg += "Exact available columns:\n"
            for col in all_columns:
                user_msg += f"  • `{col}`\n"
            user_msg += "\nOKF Bundle Content:\n\n"

        user_msg += state.okf_content

        state.system_context = call_llm(self._SYSTEM, user_msg)

        # Prepend an authoritative snake_case table name reference so the
        # SQL generator/validator always know the real table names, even if
        # the LLM-generated context above echoes a human-readable title.
        if title_to_actual:
            table_list = "\n".join(
                f"  • `{snake}`" for snake in title_to_actual.values())
            table_name_reference = (
                f"# Database Table Names (PostgreSQL, snake_case)\n\n"
                f"These are the ONLY valid tables available. Use these EXACT names "
                f"(not CamelCase, not titles with spaces) in SQL FROM and JOIN clauses:\n"
                f"{table_list}\n\n"
            )
            state.system_context = table_name_reference + state.system_context

        # Normalize any leaked human-readable titles (e.g. "Loan Payments")
        # to their real snake_case table name so nothing downstream sees
        # contradicting table names in the same context.
        for title, snake in sorted(title_to_actual.items(), key=lambda kv: -len(kv[0])):
            if title.lower() == snake:
                continue
            state.system_context = re.sub(
                rf'"{re.escape(title)}"', f"`{snake}`", state.system_context)
            state.system_context = re.sub(
                rf"\b{re.escape(title)}\b", snake, state.system_context)

        logger.info(
            "[%s] Context built (%d chars).", self.name, len(
                state.system_context)
        )
        return state
