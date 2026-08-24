# OKF Bundle Agent Service

A standalone FastAPI microservice for **Open Knowledge Format (OKF)** bundle operations. Provides REST endpoints for semantic routing, knowledge retrieval, and intelligent context building for banking domain queries.

## 🎯 Purpose

**OKF Bundle Agent** is a reusable service that:

- **Routes queries** to the correct knowledge section (Tables | Metrics | Runbooks | Datasets)
- **Retrieves OKF content** from markdown bundles using lazy/progressive disclosure
- **Builds structured contexts** for downstream SQL generation or domain reasoning
- **Answers questions** from operational runbooks and compliance procedures
- **Runs independently** — can be deployed as a containerized microservice
- **Integrates easily** — simple REST API compatible with any client (Python, Node.js, .NET, etc.)

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│      Client (NL2SqlGen-OKF-Agents)      │
│       SQL Service or Any App            │
└────────────┬────────────────────────────┘
             │ HTTP REST
             ▼
┌─────────────────────────────────────────┐
│    OKF Bundle Agent Service (8002)      │
├─────────────────────────────────────────┤
│  1. SectionSelectionAgent               │
│     ↓ (classify query)                  │
│  2. SectionRetrievalAgent               │
│     ↓ (load OKF markdown)               │
│  3. ContextBuilderAgent                 │
│     ↓ (structure context)               │
│  4. KnowledgeBaseAgent (optional)       │
│     ↓ (answer from runbooks)            │
└─────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│   OKF Bundle (Markdown Knowledge Base)  │
│   ├── tables/                           │
│   ├── metrics/                          │
│   ├── runbooks/                         │
│   └── datasets/                         │
└─────────────────────────────────────────┘
```

## ✨ Features

- **4 REST Endpoints** for OKF operations (section routing, retrieval, context building, KB queries)
- **Unified Pipeline Endpoint** that chains all agents in sequence
- **Lazy Bundle Loading** (BundleNavigator) — efficient for large knowledge bases
- **Fallback Mechanisms** — graceful degradation if primary loading strategy fails
- **Mock LLM Mode** — works offline without OpenAI API key (keyword-driven responses)
- **Structured Response Models** using Pydantic
- **Comprehensive Logging** — debug pipeline execution easily
- **Docker Support** — containerized deployment
- **Health Checks** — built-in liveness probe

## 🚀 Quick Start

### 1. **Local Setup**

```bash
# Clone or navigate to project
cd okf-bundle-agent

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy .env template and configure
cp .env.example .env
# Edit .env to add OPENAI_API_KEY (optional for mock mode)

# Run service
python -m uvicorn src.service:app --host 0.0.0.0 --port 8002 --reload
```

**Service will be available at:** `http://localhost:8002`

**Interactive API docs:** `http://localhost:8002/docs`

### 2. **Docker Setup**

```bash
# Build image
docker build -t okf-bundle-agent:latest .

# Run container
docker run -p 8002:8002 \
  -e OPENAI_API_KEY=sk-... \
  -e DEBUG=False \
  okf-bundle-agent:latest
```

### 3. **Docker Compose** (with other services)

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
      timeout: 10s
      retries: 3

  # Your other services (NL2SqlGen-OKF-Agents, sql-service, etc.)
  nl2sql-agents:
    # ... config
    depends_on:
      okf-bundle-agent:
        condition: service_healthy
```

## 📡 API Endpoints

### Health Check

```bash
GET /health

Response:
{
  "service": "okf-bundle-agent",
  "version": "1.0.0",
  "status": "healthy"
}
```

### Section Selection (Classification)

```bash
POST /section-selection

Request:
{
  "query": "Show me all delinquent loans"
}

Response:
{
  "section": "Tables",
  "confidence": 0.95
}
```

### Section Retrieval

```bash
POST /section-retrieval

Request:
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
      "tags": ["schema", "core"],
      "resource": null,
      "timestamp": "2025-01-20"
    }
  ],
  "content": "## Bank Customers (type: table)\n\n..."
}
```

### Context Building

```bash
POST /context-building

Request:
{
  "query": "Show delinquent loans",
  "okf_content": "## Tables\n\n..."
}

Response:
{
  "system_context": "Table: loans\nColumns: loan_id, status, outstanding_balance\n..."
}
```

### Knowledge Base Query

```bash
POST /knowledge-base-query

Request:
{
  "query": "What are the steps for AML investigation?",
  "okf_content": "## AML Alert Investigation\n\n..."
}

Response:
{
  "answer": "1. Initial alert review...\n2. Customer verification...",
  "source": "knowledge_base"
}
```

### Unified Pipeline

```bash
POST /pipeline/run

Request:
{
  "query": "Show me all delinquent loans",
  "conversation_history": []
}

Response:
{
  "section": "Tables",
  "context": "Table: loans\nColumns: loan_id...",
  "answer": "...",
  "raw_content": "## Tables\n\n..."
}
```

## 🔧 Configuration

All configuration via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_NAME` | `okf-bundle-agent` | Service identifier |
| `SERVICE_HOST` | `0.0.0.0` | Bind address |
| `SERVICE_PORT` | `8002` | HTTP port |
| `DEBUG` | `False` | Debug logging |
| `OPENAI_API_KEY` | `` | OpenAI API key (optional) |
| `OPENAI_MODEL` | `gpt-4o` | LLM model |
| `OPENAI_TIMEOUT` | `30` | API timeout (seconds) |
| `BUNDLE_ROOT` | `okf_bundle/` | Path to OKF bundle |

## 📚 Integration Guide

See [INTEGRATION.md](./docs/INTEGRATION.md) for detailed instructions on:
- Integrating with NL2SqlGen-OKF-Agents
- Using as a library vs. microservice
- Example client code (Python, JavaScript, cURL)
- Error handling and retry strategies

## 🧪 Testing

```bash
# Run pytest
pytest tests/

# Run specific test
pytest tests/test_okf_bundle.py::test_section_selection

# With coverage
pytest --cov=src tests/
```

## 📖 Documentation

- **[API.md](./docs/API.md)** — Detailed endpoint reference
- **[USAGE.md](./docs/USAGE.md)** — Usage examples and patterns
- **[INTEGRATION.md](./docs/INTEGRATION.md)** — Integration guide
- **Interactive Docs** — `http://localhost:8002/docs` (Swagger UI)

## 🏦 OKF Bundle Structure

The included `okf_bundle/` contains:

```
okf_bundle/
├── index.md                    # Bundle index
├── tables/                     # 6 table definitions
│   ├── bank_customers.md
│   ├── bank_accounts.md
│   ├── transactions.md
│   ├── loans.md
│   ├── loan_payments.md
│   └── flags.md
├── metrics/                    # 4 KPI definitions
│   ├── loan_delinquency_rate.md
│   ├── npa_ratio.md
│   ├── transaction_success_rate.md
│   └── kyc_completion_rate.md
├── runbooks/                   # 3 operational procedures
│   ├── aml_alert_investigation.md
│   ├── loan_restructuring.md
│   └── kyc_renewal.md
└── datasets/
    └── retail_bank.db.md       # Database metadata
```

Each markdown file has YAML frontmatter (type, title, description, etc.) and business rules/schemas in the body.

## 🔐 Security

- **CORS enabled** — configure origins as needed
- **No authentication** — add auth middleware as needed
- **Request validation** — Pydantic models validate all inputs
- **API Key for OpenAI** — store securely in environment

## 📊 Logging

Service logs to stdout with structured format:
```
2025-01-20 14:35:12 - okf_bundle.service - INFO - Starting okf-bundle-agent v1.0.0
2025-01-20 14:35:15 - okf_bundle.agents.section_selection - INFO - [SectionSelectionAgent] Selecting OKF section.
2025-01-20 14:35:16 - okf_bundle.agents.section_selection - INFO - [SectionSelectionAgent] → section_type=Tables
```

Set `DEBUG=True` in `.env` for verbose logging.

## 🚦 Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `OPENAI_API_KEY`
- [ ] Set proper `CORS` origins
- [ ] Use health checks in orchestration
- [ ] Add request rate limiting
- [ ] Set up centralized logging (ELK, CloudWatch, etc.)
- [ ] Configure alerts for errors
- [ ] Use secrets manager for API keys
- [ ] Test with expected data volumes

## 📞 Support & Contributing

For issues, questions, or contributions:
1. Check existing documentation (see `/docs`)
2. Review integration guide
3. Test with curl/Postman against `/docs` endpoint
4. Check logs with `DEBUG=True`

## 📄 License

Part of the ClearBank AI initiative. See parent project for license details.

## 🔗 Related Projects

- **NL2SqlGen-OKF-Agents** — Main SQL generation pipeline (uses this service)
- **sql-service** — SQL execution microservice
- **ak-db-service** — Database abstraction layer

---

**Version:** 1.0.0 | **Last Updated:** 2025-01-20
