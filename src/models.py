"""
models.py — Request/Response models for OKF Bundle Agent API
"""
from dataclasses import dataclass, field
from typing import Optional
from pydantic import BaseModel


# ─── API Request/Response Models ───────────────────────────────────

class SectionSelectionRequest(BaseModel):
    """Request to classify a query into an OKF section."""
    query: str

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me all delinquent loans"
            }
        }


class SectionSelectionResponse(BaseModel):
    """Response with classified section."""
    section: str  # "Tables" | "Metrics" | "Runbooks" | "Datasets"
    domain: Optional[str] = None  # "retail_banking" | "customer_support"
    confidence: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "section": "Tables",
                "domain": "retail_banking",
                "confidence": 0.95
            }
        }


class SectionRetrievalRequest(BaseModel):
    """Request to retrieve OKF content for a section."""
    section_type: str  # "Tables" | "Metrics" | "Runbooks" | "Datasets"
    # "retail_banking" | "customer_support"; None = all domains
    domain: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "section_type": "Tables",
                "domain": "retail_banking"
            }
        }


class ConceptMetadata(BaseModel):
    """Metadata about a single concept."""
    concept_id: str
    title: str
    concept_type: str
    description: Optional[str] = None
    resource: Optional[str] = None
    tags: list[str] = []
    timestamp: Optional[str] = None


class SectionRetrievalResponse(BaseModel):
    """Response with loaded OKF content."""
    section_type: str
    domain: Optional[str] = None
    concept_count: int
    concepts: list[ConceptMetadata]
    content: str  # Full markdown concatenated content

    class Config:
        json_schema_extra = {
            "example": {
                "section_type": "Tables",
                "concept_count": 2,
                "concepts": [
                    {
                        "concept_id": "tables/bank_customers",
                        "title": "Bank Customers",
                        "concept_type": "table",
                        "description": "Customer master data"
                    }
                ],
                "content": "## Bank Customers (type: table)\n\n..."
            }
        }


class ContextBuilderRequest(BaseModel):
    """Request to build structured context from raw OKF content."""
    query: str
    okf_content: str
    domain: Optional[str] = None  # "retail_banking" | "customer_support"

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show delinquent loans",
                "okf_content": "## Tables\n\n..."
            }
        }


class ContextBuilderResponse(BaseModel):
    """Response with structured context."""
    system_context: str

    class Config:
        json_schema_extra = {
            "example": {
                "system_context": "Table: loans\nColumns: loan_id, status, outstanding_balance\n..."
            }
        }


class KnowledgeBaseQueryRequest(BaseModel):
    """Request to answer from knowledge base (runbooks/datasets)."""
    query: str
    okf_content: str

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the steps for AML investigation?",
                "okf_content": "## AML Alert Investigation\n\n..."
            }
        }


class KnowledgeBaseQueryResponse(BaseModel):
    """Response from knowledge base agent."""
    answer: str
    source: str = "knowledge_base"

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "1. Initial review...\n2. ...",
                "source": "knowledge_base"
            }
        }


class HealthResponse(BaseModel):
    """Service health check response."""
    service: str
    version: str
    status: str = "healthy"

    class Config:
        json_schema_extra = {
            "example": {
                "service": "okf-bundle-agent",
                "version": "1.0.0",
                "status": "healthy"
            }
        }


# ─── Internal Agent State (from refactored base.py) ──────────────────

@dataclass
class AgentState:
    """
    Mutable state object threaded through every agent in the pipeline.
    Used internally by the service.
    """
    user_query: str
    conversation_history: list = field(default_factory=list)
    intent: str = ""
    section_type: str = ""  # "Tables" | "Metrics" | "Runbooks" | "Datasets"
    domain: str = ""  # "retail_banking" | "customer_support"; "" = all domains
    okf_content: str = ""
    system_context: str = ""
    final_answer: str = ""
    error: str = ""
