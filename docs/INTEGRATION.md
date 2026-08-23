# OKF Bundle Agent — Integration Guide

This guide explains how to integrate the **OKF Bundle Agent** with other projects, particularly **NL2SqlGen-OKF-Agents**.

## Table of Contents

1. [Integration Modes](#integration-modes)
2. [Setup Steps](#setup-steps)
3. [Python Integration (Library)](#python-integration-library)
4. [REST Integration (Microservice)](#rest-integration-microservice)
5. [Example: NL2SqlGen-OKF-Agents](#example-nl2sqlgen-okf-agents)
6. [Environment Configuration](#environment-configuration)
7. [Error Handling](#error-handling)
8. [Troubleshooting](#troubleshooting)

---

## Integration Modes

### Mode 1: **Microservice (REST API)**

Best for:
- Deploying as a standalone service
- Language-agnostic clients
- Containerized architectures (Docker, Kubernetes)
- Separation of concerns

**Communication:** HTTP REST
**Port:** `8002` (configurable)
**Latency:** ~100-500ms per request (network + LLM)

### Mode 2: **Library (Direct Import)**

Best for:
- Same-process usage
- Minimal latency
- Monolithic architectures
- Python-only consumers

**Communication:** In-process function calls
**Port:** N/A
**Latency:** ~50-200ms per request (LLM only)

---

## Setup Steps

### Step 1: Start OKF Bundle Agent Service

```bash
cd okf-bundle-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add OPENAI_API_KEY

# Start service
python -m uvicorn src.service:app --host 0.0.0.0 --port 8002
```

Verify it's running:
```bash
curl http://localhost:8002/health
# Response: {"service":"okf-bundle-agent","version":"1.0.0","status":"healthy"}
```

### Step 2: Configure Downstream Service (e.g., NL2SqlGen-OKF-Agents)

Choose your integration mode and follow the appropriate section below.

---

## Python Integration (Library)

### Installation

Add to your project's `requirements.txt`:

```
# Add the okf-bundle-agent as a local dependency (development)
# Or when published to PyPI:
# okf-bundle-agent>=1.0.0
```

For local development:

```bash
cd okf-bundle-agent
pip install -e .  # Installs in editable mode
```

### Usage Example

```python
from okf_bundle_agent.agents import (
    AgentState,
    SectionSelectionAgent,
    SectionRetrievalAgent,
    ContextBuilderAgent,
    KnowledgeBaseAgent,
)

# Initialize state
state = AgentState(user_query="Show me all delinquent loans")

# Step 1: Classify query
section_agent = SectionSelectionAgent()
state = section_agent.run(state)
print(f"Section: {state.section_type}")  # Output: "Tables"

# Step 2: Retrieve content
retrieval_agent = SectionRetrievalAgent()
state = retrieval_agent.run(state)
print(f"Loaded {len(state.okf_content)} chars of OKF content")

# Step 3: Build context
context_agent = ContextBuilderAgent()
state = context_agent.run(state)
print(f"Context: {state.system_context[:100]}...")

# Step 4: Query knowledge base (if needed)
if state.section_type in ("Runbooks", "Datasets"):
    kb_agent = KnowledgeBaseAgent()
    state = kb_agent.run(state)
    print(f"Answer: {state.final_answer}")
else:
    # For Tables/Metrics, use context for SQL generation
    print(f"Use context for SQL generation")
```

### Refactoring Existing Code

**Before (monolithic approach):**
```python
from src.agents import SectionSelectionAgent
from src.agents.base import BUNDLE_ROOT

agent = SectionSelectionAgent()
# Imports from local src/agents/
```

**After (using OKF Bundle Agent library):**
```python
from okf_bundle_agent.agents import SectionSelectionAgent

agent = SectionSelectionAgent()
# Imports from okf-bundle-agent package
```

---

## REST Integration (Microservice)

### Client Code Examples

#### Python (using `httpx`)

```python
import httpx
import json

BASE_URL = "http://localhost:8002"
client = httpx.Client(base_url=BASE_URL, timeout=30.0)

# Step 1: Classify query
response = client.post(
    "/section-selection",
    json={"query": "Show me all delinquent loans"}
)
result = response.json()
section = result["section"]  # "Tables"
print(f"Section: {section}")

# Step 2: Retrieve section content
response = client.post(
    "/section-retrieval",
    json={"section_type": section}
)
retrieval = response.json()
okf_content = retrieval["content"]
print(f"Loaded {len(okf_content)} chars")

# Step 3: Build context
response = client.post(
    "/context-building",
    json={
        "query": "Show me all delinquent loans",
        "okf_content": okf_content
    }
)
context = response.json()["system_context"]
print(f"Context built: {context[:100]}...")

# Or use unified pipeline
response = client.post(
    "/pipeline/run",
    json={"query": "Show me all delinquent loans"}
)
pipeline_result = response.json()
print(f"Section: {pipeline_result['section']}")
print(f"Answer: {pipeline_result['answer'][:100]}...")

client.close()
```

#### JavaScript/Node.js

```javascript
const BASE_URL = 'http://localhost:8002';

async function runPipeline(query) {
  const response = await fetch(`${BASE_URL}/pipeline/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return await response.json();
}

// Usage
runPipeline("Show me all delinquent loans")
  .then(result => console.log(result))
  .catch(err => console.error(err));
```

#### cURL

```bash
# Health check
curl -X GET http://localhost:8002/health

# Classification
curl -X POST http://localhost:8002/section-selection \
  -H "Content-Type: application/json" \
  -d '{"query": "Show delinquent loans"}'

# Unified pipeline
curl -X POST http://localhost:8002/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me delinquent loans"}'
```

### Configuration

Set environment variable to point to OKF Bundle Agent:

```bash
# In NL2SqlGen-OKF-Agents .env or config
OKF_BUNDLE_AGENT_URL=http://localhost:8002
OKF_BUNDLE_AGENT_TIMEOUT=30
```

Then use in your code:

```python
import os
import httpx

OKF_AGENT_URL = os.getenv("OKF_BUNDLE_AGENT_URL", "http://localhost:8002")
OKF_AGENT_TIMEOUT = int(os.getenv("OKF_BUNDLE_AGENT_TIMEOUT", "30"))

client = httpx.Client(base_url=OKF_AGENT_URL, timeout=OKF_AGENT_TIMEOUT)
```

---

## Example: NL2SqlGen-OKF-Agents

### Before Refactoring (Monolithic)

**NL2SqlGen-OKF-Agents structure:**
```
src/
├── agents/
│   ├── section_selection.py    ← Local copy
│   ├── section_retrieval.py    ← Local copy
│   ├── context_builder.py      ← Local copy
│   ├── knowledge_base.py       ← Local copy
│   ├── sql_generator.py
│   ├── sql_validator.py
│   ├── sql_executor.py
│   ├── error_response_generator.py
│   ├── response_synthesizer.py
│   ├── orchestration.py        ← Imports local agents
│   └── base.py                 ← Shared state
├── okf_parser.py               ← Local copy
└── okf_validator.py            ← Local copy
```

### After Refactoring (Microservice)

**NL2SqlGen-OKF-Agents structure:**
```
src/
├── agents/
│   ├── sql_generator.py        ← Only SQL-specific agents
│   ├── sql_validator.py
│   ├── sql_executor.py
│   ├── error_response_generator.py
│   ├── response_synthesizer.py
│   ├── orchestration.py        ← Now calls OKF Bundle Agent REST
│   └── base.py                 ← Minimal shared state
├── okf_client.py               ← New: REST client for OKF service
└── ... (no more okf_parser.py or bundle agents)
```

### Implementation Steps

#### Step 1: Create REST Client Wrapper

Create `src/okf_client.py`:

```python
"""
okf_client.py — REST client for OKF Bundle Agent Service
"""

import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger("clearbank.okf_client")


class OKFBundleClient:
    """HTTP client for OKF Bundle Agent service."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url or os.getenv(
            "OKF_BUNDLE_AGENT_URL", "http://localhost:8002"
        )
        self.timeout = timeout
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def select_section(self, query: str) -> str:
        """Classify query into OKF section."""
        response = self.client.post(
            "/section-selection",
            json={"query": query}
        )
        response.raise_for_status()
        return response.json()["section"]

    def retrieve_section(self, section_type: str) -> str:
        """Retrieve OKF content for section."""
        response = self.client.post(
            "/section-retrieval",
            json={"section_type": section_type}
        )
        response.raise_for_status()
        return response.json()["content"]

    def build_context(self, query: str, okf_content: str) -> str:
        """Build structured context from OKF content."""
        response = self.client.post(
            "/context-building",
            json={
                "query": query,
                "okf_content": okf_content
            }
        )
        response.raise_for_status()
        return response.json()["system_context"]

    def query_knowledge_base(self, query: str, okf_content: str) -> str:
        """Query knowledge base (runbooks/datasets)."""
        response = self.client.post(
            "/knowledge-base-query",
            json={
                "query": query,
                "okf_content": okf_content
            }
        )
        response.raise_for_status()
        return response.json()["answer"]

    def run_pipeline(self, query: str) -> dict:
        """Run complete OKF pipeline."""
        response = self.client.post(
            "/pipeline/run",
            json={"query": query}
        )
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# Singleton instance
_client: Optional[OKFBundleClient] = None


def get_okf_client() -> OKFBundleClient:
    """Get or create global OKF client."""
    global _client
    if _client is None:
        _client = OKFBundleClient()
    return _client
```

#### Step 2: Update Orchestration Agent

Update `src/agents/orchestration.py`:

```python
"""
agents/orchestration.py — Updated Orchestration Agent (REST-based)
"""

import logging
from .base import AgentState, BaseAgent
from ..okf_client import get_okf_client
from .knowledge_base import KnowledgeBaseAgent  # Still local
from .sql_generator import SQLGeneratorAgent    # Still local
# ... other imports

logger = logging.getLogger("clearbank.agent.orchestration")


class OrchestrationAgent(BaseAgent):
    """Coordinator that uses OKF Bundle Agent service."""

    name = "OrchestrationAgent"

    def run(self, state: AgentState) -> AgentState:
        logger.info("[%s] Domain pipeline start.", self.name)

        okf_client = get_okf_client()

        try:
            # Step 1: Section Selection (via OKF service)
            logger.info("[%s] → Calling OKF Bundle Agent for section selection", self.name)
            state.section_type = okf_client.select_section(state.user_query)

            # Step 2 & 3: Section Retrieval + Context Building (via OKF service)
            logger.info("[%s] → Calling OKF Bundle Agent for content retrieval", self.name)
            state.okf_content = okf_client.retrieve_section(state.section_type)
            state.system_context = okf_client.build_context(
                state.user_query,
                state.okf_content
            )

            # Step 4: Branch logic (local agents or OKF service)
            if state.section_type in ("Runbooks", "Datasets"):
                logger.info("[%s] → KB branch (%s)", self.name, state.section_type)
                state.final_answer = okf_client.query_knowledge_base(
                    state.user_query,
                    state.okf_content
                )
                # Could also use local KnowledgeBaseAgent if preferred
                return ResponseSynthesizerAgent().run(state)

            # For Tables/Metrics, continue with local SQL pipeline
            logger.info("[%s] → SQL pipeline branch", self.name)
            # ... existing SQL pipeline code ...

        except Exception as exc:
            logger.error("[%s] OKF Bundle Agent error: %s", self.name, exc)
            state.error = f"OKF service error: {str(exc)}"
            return ErrorResponseGeneratorAgent().run(state)
```

#### Step 3: Update Requirements

Update `NL2SqlGen-OKF-Agents/requirements.txt`:

```
# Remove these (now provided by OKF service):
# pyyaml

# Add HTTP client (if not already present):
httpx>=0.25.0

# Keep all other dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
# ... etc
```

#### Step 4: Environment Configuration

Update `.env` for NL2SqlGen-OKF-Agents:

```bash
# Point to OKF Bundle Agent service
OKF_BUNDLE_AGENT_URL=http://okf-bundle-agent:8002
OKF_BUNDLE_AGENT_TIMEOUT=30

# Keep existing settings
OPENAI_API_KEY=sk-...
SQL_SERVICE_URL=http://localhost:8000
```

---

## Environment Configuration

### OKF Bundle Agent

```bash
# .env for okf-bundle-agent/
SERVICE_PORT=8002
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
DEBUG=False
BUNDLE_ROOT=okf_bundle/
```

### NL2SqlGen-OKF-Agents

```bash
# .env for NL2SqlGen-OKF-Agents/
OKF_BUNDLE_AGENT_URL=http://okf-bundle-agent:8002
OKF_BUNDLE_AGENT_TIMEOUT=30

# Other settings
SQL_SERVICE_URL=http://localhost:8000
OPENAI_API_KEY=sk-...
```

### Docker Compose

```yaml
version: '3.8'
services:
  okf-bundle-agent:
    image: okf-bundle-agent:latest
    ports:
      - "8002:8002"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      DEBUG: "False"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s

  nl2sql-agents:
    image: nl2sql-agents:latest
    ports:
      - "8081:8081"
    environment:
      OKF_BUNDLE_AGENT_URL: http://okf-bundle-agent:8002
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      okf-bundle-agent:
        condition: service_healthy
```

---

## Error Handling

### REST Integration

```python
import httpx

try:
    response = client.post("/section-selection", json={"query": query})
    response.raise_for_status()
    section = response.json()["section"]
except httpx.HTTPStatusError as exc:
    if exc.response.status_code == 500:
        logger.error("OKF service error: %s", exc.response.text)
        # Fallback: use default section
        section = "Tables"
    else:
        raise
except httpx.TimeoutException:
    logger.error("OKF service timeout")
    section = "Tables"  # Fallback
```

### Connection Pooling

```python
# Reuse client for multiple requests
client = httpx.Client(base_url="http://localhost:8002", timeout=30)

for query in queries:
    response = client.post("/section-selection", json={"query": query})
    # Process response

client.close()
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
tail -f okf-bundle-agent/debug.log

# Verify port is free
lsof -i :8002  # Unix/Linux/Mac
netstat -ano | findstr :8002  # Windows

# Check Python version
python --version  # Requires 3.10+
```

### Connection Refused

```bash
# Verify service is running
curl http://localhost:8002/health

# Check firewall (if remote)
# Check docker network (if containerized)
docker network ls
docker inspect okf-bundle-agent
```

### LLM Errors

```bash
# Check API key
echo $OPENAI_API_KEY

# Test OpenAI connection
python -c "import openai; openai.api_key='sk-...'; openai.ChatCompletion.create(...)"

# Use mock mode (no API key needed)
# Leave OPENAI_API_KEY empty or unset
```

### Slow Responses

```bash
# Check LLM latency
DEBUG=True python -m uvicorn src.service:app

# Increase timeout
OKF_BUNDLE_AGENT_TIMEOUT=60

# Profile memory
python -m memory_profiler src/service.py
```

---

## Next Steps

1. **Test endpoints** using the [API Reference](./API.md)
2. **Review usage patterns** in [USAGE.md](./USAGE.md)
3. **Deploy to production** using Docker
4. **Monitor** service health and performance

---

**Last Updated:** 2025-01-20
