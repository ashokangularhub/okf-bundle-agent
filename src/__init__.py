"""
OKF Bundle Agent Service

A standalone FastAPI service for OKF (Open Knowledge Format) bundle operations.
Provides REST endpoints for section routing, content retrieval, and knowledge base queries.

Version: 1.0.0
"""

from .config import settings
from .models import (
    AgentState,
    SectionSelectionRequest,
    SectionSelectionResponse,
    SectionRetrievalRequest,
    SectionRetrievalResponse,
    ContextBuilderRequest,
    ContextBuilderResponse,
    KnowledgeBaseQueryRequest,
    KnowledgeBaseQueryResponse,
)

__version__ = "1.0.0"
__all__ = [
    "settings",
    "AgentState",
    "SectionSelectionRequest",
    "SectionSelectionResponse",
    "SectionRetrievalRequest",
    "SectionRetrievalResponse",
    "ContextBuilderRequest",
    "ContextBuilderResponse",
    "KnowledgeBaseQueryRequest",
    "KnowledgeBaseQueryResponse",
]
