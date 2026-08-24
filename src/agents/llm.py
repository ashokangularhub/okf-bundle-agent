"""
agents/llm.py — LLM helper: call_llm() for OKF Bundle Agent Service

Call call_llm() for any LLM inference needed by agents.
Falls back to intelligent mock when OPENAI_API_KEY is not set.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

import httpx

from ..config import settings

logger = logging.getLogger("okf_bundle.llm")

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def call_llm(
    system: str,
    user: str,
    *,
    json_mode: bool = False,
    history: list[dict] | None = None,
) -> str | dict[str, Any]:
    """
    Call OpenAI Chat Completions via httpx.
    Returns a parsed dict when json_mode=True, otherwise a plain string.
    Falls back to an intelligent mock stub when OPENAI_API_KEY is absent.

    Parameters
    ----------
    history : list of {"role": "user"|"assistant", "content": "..."} dicts
        Prior conversation turns inserted between system and current user message.
    """
    api_key = settings.OPENAI_API_KEY.strip() if settings.OPENAI_API_KEY else ""
    if not api_key:
        logger.debug("No OPENAI_API_KEY — mock LLM stub active.")
        return _mock_llm(system, user, json_mode=json_mode)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    messages: list[dict] = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user})

    payload: dict[str, Any] = {
        "model": settings.OPENAI_MODEL,
        "max_tokens": 2048,
        "messages": messages,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        response = httpx.post(
            OPENAI_URL,
            headers=headers,
            json=payload,
            timeout=settings.OPENAI_TIMEOUT
        )
        response.raise_for_status()
        text: str = response.json()["choices"][0]["message"]["content"].strip()
        logger.debug("LLM response received (%d chars).", len(text))
    except httpx.HTTPStatusError as exc:
        logger.error(
            "LLM API HTTP %s: %s", exc.response.status_code, exc.response.text[:300]
        )
        raise
    except Exception as exc:
        logger.error("LLM call failed: %s", exc)
        raise

    if json_mode:
        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE
        ).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(
                "JSON parse failed on LLM output; wrapping in 'raw' key.")
            return {"raw": text}

    return text


# ── Mock LLM (offline / demo mode) ───────────────────────────────────────────


def _mock_llm(system: str, user: str, *, json_mode: bool) -> str | dict[str, Any]:
    """Keyword-driven stubs that produce realistic responses without an API key."""
    sl = system.lower()
    ul = user.lower()

    # ── Intent classification ─────────────────────────────────────────
    if "intent" in sl or ("classify" in sl and "domain" in sl):
        domain_kws = [
            "loan", "customer", "account", "transaction", "kyc", "aml",
            "flag", "balance", "payment", "delinquent", "npa", "runbook",
            "clearbank", "banking", "fraud", "risk", "metric",
        ]
        intent = "domain" if any(kw in ul for kw in domain_kws) else "general"
        return {"intent": intent} if json_mode else intent

    # ── Section selection ─────────────────────────────────────────────
    if "section" in sl and any(s in sl for s in ("tables", "metrics", "runbooks", "datasets")):
        if any(w in ul for w in [
            "runbook", "steps for", "procedure", "aml investigation",
            "kyc renewal", "loan restructuring", "how to", "workflow",
        ]):
            sec = "Runbooks"
        elif any(w in ul for w in [
            "metric", "kpi", "delinquency rate", "npa ratio",
            "success rate", "kyc completion", "ratio", "percentage",
        ]):
            sec = "Metrics"
        elif any(w in ul for w in ["dataset", "database", "retention", "storage"]):
            sec = "Datasets"
        else:
            sec = "Tables"
        return {"section": sec} if json_mode else sec

    # ── Context building ──────────────────────────────────────────────
    if "context builder" in sl or ("context" in sl and "schema context" in sl):
        return (
            "# Schema Context (Mock)\n\n"
            "**Tables:** bank_customers, bank_accounts, transactions, loans, loan_payments, flags\n\n"
            "**Key columns:**\n"
            "- bank_customers: customer_id, full_name, email, kyc_status ∈ {verified,pending,expired,rejected}, "
            "status ∈ {active,inactive,blacklisted}, created_at\n"
            "- bank_accounts: account_id, customer_id (FK), account_type ∈ {savings,checking,fixed_deposit}, "
            "balance, status ∈ {active,frozen,blocked,closed}\n"
            "- transactions: txn_id, customer_id (FK), account_id (FK), amount, type, "
            "status ∈ {completed,pending,failed,reversed}, txn_at\n"
            "- loans: loan_id, customer_id (FK), principal, outstanding_balance, interest_rate, "
            "status ∈ {active,delinquent,written_off,closed}, disbursed_at\n"
            "- loan_payments: payment_id, loan_id (FK), emi_amount, due_date, paid_date, "
            "status ∈ {paid,overdue,pending}\n"
            "- flags: flag_id, customer_id (FK), flag_type ∈ {aml,fraud,kyc,risk}, "
            "severity ∈ {low,medium,high,critical}, status ∈ {open,resolved,escalated}\n"
        )

    # ── Knowledge base ────────────────────────────────────────────────
    if "knowledge base agent" in sl or any(w in sl for w in ["runbook", "compliance workflow"]):
        return (
            "**ClearBank Knowledge Base Answer** *(Mock)*\n\n"
            "Based on the OKF bundle content, here is the relevant guidance "
            f"for your query:\n\n> {ul[:200]}\n\n"
            "Please refer to the full runbook in `okf_bundle/runbooks/` for complete steps."
        )

    # ── Response synthesis ────────────────────────────────────────────
    if "response synthesizer" in sl or "synthesiz" in sl:
        return f"**Answer** *(Mock)*\n\n{ul[:400]}"

    # ── General fallback ──────────────────────────────────────────────
    return f"I can help with that. *(Mock)* You asked: {user[:200]}"
