"""
service.py — OKF Bundle Agent FastAPI Service

Main FastAPI application exposing OKF bundle operations as REST endpoints.
"""

from pydantic import BaseModel
import logging
import logging.handlers
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

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
    HealthResponse,
    ConceptMetadata,
)
from .agents import (
    SectionSelectionAgent,
    SectionRetrievalAgent,
    ContextBuilderAgent,
    KnowledgeBaseAgent,
)

# ── Setup logging ──────────────────────────────────────────────────────────


def setup_logging() -> None:
    """Configure logging to display DEBUG/INFO messages in console."""
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Enhanced format with timestamp and logger name
    formatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set specific loggers
    logging.getLogger("okf_bundle.service").setLevel(logging.DEBUG)
    logging.getLogger("okf_bundle").setLevel(logging.DEBUG)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


# Initialize logging on import
setup_logging()

logger = logging.getLogger("okf_bundle.service")

# ── Create FastAPI app ─────────────────────────────────────────────────────

app = FastAPI(
    title=settings.SERVICE_NAME,
    description="REST API for OKF (Open Knowledge Format) bundle operations",
    version=settings.SERVICE_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Endpoints ──────────────────────────────────────────────────────────


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse with service status
    """
    logger.info(
        "[OKF-BUNDLE] ════════════════════════════════════════\n"
        "[OKF-BUNDLE] HEALTH CHECK\n"
        "[OKF-BUNDLE] Service: %s\n"
        "[OKF-BUNDLE] Version: %s\n"
        "[OKF-BUNDLE] ════════════════════════════════════════",
        settings.SERVICE_NAME, settings.SERVICE_VERSION
    )
    return HealthResponse(
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        status="healthy"
    )


@app.post(
    "/section-selection",
    response_model=SectionSelectionResponse,
    tags=["Section Routing"]
)
async def classify_section(req: SectionSelectionRequest) -> SectionSelectionResponse:
    """
    Classify a user query to determine which OKF section it belongs to.

    Routes queries as:
    - **Tables**: SQL data queries (bank_customers, bank_accounts, transactions, loans, payments, flags)
    - **Metrics**: KPI computations (delinquency rate, NPA ratio, transaction success, KYC completion)
    - **Runbooks**: Operational procedures (AML investigation, loan restructuring, KYC renewal)
    - **Datasets**: Database/storage metadata and retention policies

    Args:
        req: SectionSelectionRequest with user query

    Returns:
        SectionSelectionResponse with section classification

    Example:
        ```
        POST /section-selection
        {
            "query": "Show me all delinquent loans"
        }

        Response:
        {
            "section": "Tables",
            "confidence": 0.95
        }
        ```
    """
    logger.info(
        "[OKF-BUNDLE] ════════════════════════════════════════\n"
        "[OKF-BUNDLE] SECTION SELECTION REQUEST\n"
        "[OKF-BUNDLE] Query: %s\n"
        "[OKF-BUNDLE] ════════════════════════════════════════",
        req.query
    )
    try:
        state = AgentState(user_query=req.query)
        agent = SectionSelectionAgent()
        state = agent.run(state)

        logger.info(
            "[OKF-BUNDLE] ✅ SECTION SELECTED:\n"
            "[OKF-BUNDLE] Section: %s\n"
            "[OKF-BUNDLE] Query: %s",
            state.section_type, req.query
        )

        return SectionSelectionResponse(
            section=state.section_type,
            confidence=0.9  # Mock confidence for now
        )
    except Exception as exc:
        logger.error(
            "[OKF-BUNDLE] ❌ SECTION SELECTION FAILED:\n"
            "[OKF-BUNDLE] Query: %s\n"
            "[OKF-BUNDLE] Error: %s",
            req.query, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Section selection failed: {str(exc)}"
        )


@app.post(
    "/section-retrieval",
    response_model=SectionRetrievalResponse,
    tags=["Content Retrieval"]
)
async def retrieve_section(req: SectionRetrievalRequest) -> SectionRetrievalResponse:
    """
    Retrieve OKF bundle content for a specific section.

    Loads all markdown files for the requested section using BundleNavigator
    and returns structured concept metadata along with concatenated content.

    Args:
        req: SectionRetrievalRequest with section_type

    Returns:
        SectionRetrievalResponse with loaded concepts and markdown content

    Example:
        ```
        POST /section-retrieval
        {
            "section_type": "Tables"
        }

        Response:
        {
            "section_type": "Tables",
            "concept_count": 6,
            "concepts": [
                {
                    "concept_id": "tables/bank_customers",
                    "title": "Bank Customers",
                    "concept_type": "table",
                    "description": "Customer master data",
                    "tags": ["schema", "core"]
                }
            ],
            "content": "## Bank Customers...\n\n---\n\n## Bank Accounts..."
        }
        ```
    """
    logger.info(
        "[OKF-BUNDLE] ════════════════════════════════════════\n"
        "[OKF-BUNDLE] SECTION RETRIEVAL REQUEST\n"
        "[OKF-BUNDLE] Section Type: %s\n"
        "[OKF-BUNDLE] ════════════════════════════════════════",
        req.section_type
    )
    try:
        state = AgentState(user_query=f"Get {req.section_type} section")
        state.section_type = req.section_type

        agent = SectionRetrievalAgent()
        state = agent.run(state)

        # Parse concepts for metadata (simplified version)
        concepts = [
            ConceptMetadata(
                concept_id=req.section_type.lower(),
                title=req.section_type,
                concept_type="section",
                description=f"OKF {req.section_type} section"
            )
        ]

        logger.info(
            "[OKF-BUNDLE] ✅ SECTION RETRIEVED:\n"
            "[OKF-BUNDLE] Section: %s\n"
            "[OKF-BUNDLE] Content length: %d chars",
            state.section_type, len(state.okf_content)
        )

        return SectionRetrievalResponse(
            section_type=state.section_type,
            concept_count=1,  # Simplified
            concepts=concepts,
            content=state.okf_content
        )
    except Exception as exc:
        logger.error(
            "[OKF-BUNDLE] ❌ SECTION RETRIEVAL FAILED:\n"
            "[OKF-BUNDLE] Section: %s\n"
            "[OKF-BUNDLE] Error: %s",
            req.section_type, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Section retrieval failed: {str(exc)}"
        )


@app.post(
    "/context-building",
    response_model=ContextBuilderResponse,
    tags=["Context Processing"]
)
async def build_context(req: ContextBuilderRequest) -> ContextBuilderResponse:
    """
    Build structured context from raw OKF content.

    Transforms raw OKF markdown into a structured system prompt containing:
    - Table names and columns (with types/ENUM values)
    - JOIN paths and foreign keys
    - Business rules and constraints
    - Metric formulas (if applicable)

    Args:
        req: ContextBuilderRequest with query and OKF content

    Returns:
        ContextBuilderResponse with structured system_context

    Example:
        ```
        POST /context-building
        {
            "query": "Show delinquent loans",
            "okf_content": "## Tables\n\n**Bank Customers**..."
        }

        Response:
        {
            "system_context": "Table: loans\nColumns: loan_id, status...\n"
        }
        ```
    """
    logger.info(
        "[OKF-BUNDLE] ════════════════════════════════════════\n"
        "[OKF-BUNDLE] CONTEXT BUILDING REQUEST\n"
        "[OKF-BUNDLE] Query: %s\n"
        "[OKF-BUNDLE] Content length: %d chars\n"
        "[OKF-BUNDLE] ════════════════════════════════════════",
        req.query, len(req.okf_content)
    )
    try:
        state = AgentState(
            user_query=req.query,
            okf_content=req.okf_content
        )

        agent = ContextBuilderAgent()
        state = agent.run(state)

        logger.info(
            "[OKF-BUNDLE] ✅ CONTEXT BUILT:\n"
            "[OKF-BUNDLE] Query: %s\n"
            "[OKF-BUNDLE] Context length: %d chars",
            req.query, len(state.system_context)
        )

        return ContextBuilderResponse(system_context=state.system_context)
    except Exception as exc:
        logger.error(
            "[OKF-BUNDLE] ❌ CONTEXT BUILDING FAILED:\n"
            "[OKF-BUNDLE] Query: %s\n"
            "[OKF-BUNDLE] Error: %s",
            req.query, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Context building failed: {str(exc)}"
        )


@app.post(
    "/knowledge-base-query",
    response_model=KnowledgeBaseQueryResponse,
    tags=["Knowledge Base"]
)
async def query_knowledge_base(req: KnowledgeBaseQueryRequest) -> KnowledgeBaseQueryResponse:
    """
    Query the knowledge base using OKF content.

    Answers questions using Runbooks and Datasets content as the authoritative
    source. Returns procedural steps, operational workflows, and compliance guidance.

    Args:
        req: KnowledgeBaseQueryRequest with query and OKF content

    Returns:
        KnowledgeBaseQueryResponse with answer and source attribution

    Example:
        ```
        POST /knowledge-base-query
        {
            "query": "What are the steps for AML investigation?",
            "okf_content": "## AML Alert Investigation\n\n1. Initial review..."
        }

        Response:
        {
            "answer": "1. Initial review of alert...\n2. Customer verification...",
            "source": "knowledge_base"
        }
        ```
    """
    logger.info(
        "[OKF-BUNDLE] ════════════════════════════════════════\n"
        "[OKF-BUNDLE] KNOWLEDGE BASE QUERY REQUEST\n"
        "[OKF-BUNDLE] Query: %s\n"
        "[OKF-BUNDLE] Content length: %d chars\n"
        "[OKF-BUNDLE] ════════════════════════════════════════",
        req.query, len(req.okf_content)
    )
    try:
        state = AgentState(
            user_query=req.query,
            okf_content=req.okf_content
        )

        agent = KnowledgeBaseAgent()
        state = agent.run(state)

        logger.info(
            "[OKF-BUNDLE] ✅ KNOWLEDGE BASE QUERY SUCCESS:\n"
            "[OKF-BUNDLE] Query: %s\n"
            "[OKF-BUNDLE] Answer length: %d chars",
            req.query, len(state.final_answer)
        )

        return KnowledgeBaseQueryResponse(
            answer=state.final_answer,
            source="knowledge_base"
        )
    except Exception as exc:
        logger.error(
            "[OKF-BUNDLE] ❌ KNOWLEDGE BASE QUERY FAILED:\n"
            "[OKF-BUNDLE] Query: %s\n"
            "[OKF-BUNDLE] Error: %s",
            req.query, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Knowledge base query failed: {str(exc)}"
        )


# ── Unified Pipeline Endpoint ──────────────────────────────────────────────


class UnifiedPipelineRequest(BaseModel):
    """Request for the unified OKF pipeline."""
    query: str
    conversation_history: Optional[list] = None


class UnifiedPipelineResponse(BaseModel):
    """Response from unified pipeline."""
    section: str
    context: str
    answer: str
    raw_content: str


@app.post(
    "/pipeline/run",
    response_model=UnifiedPipelineResponse,
    tags=["Pipeline"]
)
async def run_unified_pipeline(req: UnifiedPipelineRequest) -> UnifiedPipelineResponse:
    """
    Execute the complete OKF processing pipeline.

    Chains agents in sequence:
    1. SectionSelectionAgent → classify query into section
    2. SectionRetrievalAgent → load OKF content for section
    3. ContextBuilderAgent → build structured context
    4. KnowledgeBaseAgent (for Runbooks/Datasets) or return context (for Tables/Metrics)

    Args:
        req: UnifiedPipelineRequest with user query

    Returns:
        UnifiedPipelineResponse with section, context, and answer

    Example:
        ```
        POST /pipeline/run
        {
            "query": "What are the AML investigation steps?"
        }

        Response:
        {
            "section": "Runbooks",
            "context": "Operational procedures for compliance...",
            "answer": "1. Initial alert review...",
            "raw_content": "## AML Alert Investigation..."
        }
        ```
    """
    try:
        state = AgentState(user_query=req.query)

        # Step 1: Section Selection
        logger.info("Pipeline: Step 1 - Section Selection")
        state = SectionSelectionAgent().run(state)

        # Step 2: Section Retrieval
        logger.info(
            f"Pipeline: Step 2 - Section Retrieval ({state.section_type})")
        state = SectionRetrievalAgent().run(state)

        # Step 3: Context Building
        logger.info("Pipeline: Step 3 - Context Building")
        state = ContextBuilderAgent().run(state)

        # Step 4: Knowledge Base Query or return context
        if state.section_type in ("Runbooks", "Datasets"):
            logger.info("Pipeline: Step 4 - Knowledge Base Query")
            state = KnowledgeBaseAgent().run(state)
        else:
            # For Tables/Metrics, return the context as the answer
            state.final_answer = state.system_context

        return UnifiedPipelineResponse(
            section=state.section_type,
            context=state.system_context,
            answer=state.final_answer,
            raw_content=state.okf_content
        )
    except Exception as exc:
        logger.error("Unified pipeline failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution failed: {str(exc)}"
        )


if __name__ == "__main__":
    import uvicorn

    logger.info(
        f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    uvicorn.run(
        app,
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        log_level="debug" if settings.DEBUG else "info",
    )
