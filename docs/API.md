# OKF Bundle Agent — API Reference

Complete REST API specification for OKF Bundle Agent Service.

## Base URL

```
http://localhost:8002  (local)
http://okf-bundle-agent:8002  (docker)
```

## Authentication

Currently no authentication required. Add JWT/API key middleware in production.

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Purpose:** Verify service health and readiness

**Response:** `200 OK`

```json
{
  "service": "okf-bundle-agent",
  "version": "1.0.0",
  "status": "healthy"
}
```

**Example:**
```bash
curl -X GET http://localhost:8002/health
```

---

### 2. Section Selection

**Endpoint:** `POST /section-selection`

**Purpose:** Classify user query into OKF section

**Request:**
```json
{
  "query": "Show me all delinquent loans"
}
```

**Response:** `200 OK`
```json
{
  "section": "Tables",
  "confidence": 0.95
}
```

**Possible Sections:**
- `Tables` — SQL queries on customer, account, transaction, loan, payment, or flag data
- `Metrics` — KPI queries (delinquency rate, NPA ratio, etc.)
- `Runbooks` — Operational procedures (AML investigation, KYC renewal, etc.)
- `Datasets` — Database/storage metadata

**Example:**
```bash
curl -X POST http://localhost:8002/section-selection \
  -H "Content-Type: application/json" \
  -d '{"query": "Show delinquent loans"}'
```

**Errors:**
- `500 Internal Server Error` — LLM call failed or other service error

---

### 3. Section Retrieval

**Endpoint:** `POST /section-retrieval`

**Purpose:** Retrieve OKF bundle content for a section

**Request:**
```json
{
  "section_type": "Tables"
}
```

**Response:** `200 OK`
```json
{
  "section_type": "Tables",
  "concept_count": 6,
  "concepts": [
    {
      "concept_id": "tables/customers",
      "title": "Customers",
      "concept_type": "table",
      "description": "Customer master data for ClearBank retail banking",
      "resource": null,
      "tags": ["core", "schema"],
      "timestamp": "2025-01-20T10:30:00Z"
    },
    {
      "concept_id": "tables/accounts",
      "title": "Accounts",
      "concept_type": "table",
      "description": "Deposit and savings accounts",
      "tags": ["core", "schema"],
      "timestamp": "2025-01-20T10:30:00Z"
    }
  ],
  "content": "## Customers (type: table)\n\n---type: table\ntitle: Customers\n...\n\n---\n\n## Accounts (type: table)\n\n..."
}
```

**Parameters:**
| Name | Type | Required | Options |
|------|------|----------|---------|
| `section_type` | string | Yes | Tables, Metrics, Runbooks, Datasets |

**Response Fields:**
- `section_type` — Requested section
- `concept_count` — Number of concepts loaded
- `concepts` — Array of concept metadata
- `content` — Full markdown concatenated content

**Example:**
```bash
curl -X POST http://localhost:8002/section-retrieval \
  -H "Content-Type: application/json" \
  -d '{"section_type": "Tables"}'
```

**Errors:**
- `500 Internal Server Error` — Failed to load section files

---

### 4. Context Building

**Endpoint:** `POST /context-building`

**Purpose:** Build structured context from raw OKF content

**Request:**
```json
{
  "query": "Show me all delinquent loans",
  "okf_content": "## Customers (type: table)\n\n..."
}
```

**Response:** `200 OK`
```json
{
  "system_context": "# Schema Context\n\nTable: loans\n\nColumns:\n- loan_id (INTEGER, PK)\n- customer_id (INTEGER, FK)\n- status (TEXT): enum(active, delinquent, written_off, closed)\n- outstanding_balance (DECIMAL)\n\nJOINs:\n- loans.customer_id → customers.customer_id\n\nBusiness Rules:\n- delinquent loans have status='delinquent'\n- query only active and delinquent loans\n\n..."
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | User query for context |
| `okf_content` | string | Yes | Raw OKF markdown from retrieval |

**Response Fields:**
- `system_context` — Structured prompt for downstream agents (SQL generation, etc.)

**Example:**
```bash
curl -X POST http://localhost:8002/context-building \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show delinquent loans",
    "okf_content": "## Tables\n\n### Loans..."
  }'
```

**Errors:**
- `500 Internal Server Error` — LLM call failed

---

### 5. Knowledge Base Query

**Endpoint:** `POST /knowledge-base-query`

**Purpose:** Answer questions from runbooks and datasets

**Request:**
```json
{
  "query": "What are the steps for AML investigation?",
  "okf_content": "## AML Alert Investigation\n\n1. Initial review...\n\n"
}
```

**Response:** `200 OK`
```json
{
  "answer": "The AML investigation process includes:\n\n1. **Initial Alert Review**\n   - Review the automated alert\n   - Assess risk severity\n   - Determine if investigation needed\n\n2. **Customer Verification**\n   - Cross-reference KYC information\n   - Check transaction patterns\n   - Review account history\n\n3. **Decision**\n   - If suspicious: escalate to compliance\n   - If benign: close investigation\n   - Document findings",
  "source": "knowledge_base"
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | Question/query |
| `okf_content` | string | Yes | Raw OKF markdown (runbooks/datasets) |

**Response Fields:**
- `answer` — Answer text from knowledge base
- `source` — Always "knowledge_base"

**Example:**
```bash
curl -X POST http://localhost:8002/knowledge-base-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to handle AML alerts?",
    "okf_content": "## AML Alert Investigation..."
  }'
```

**Errors:**
- `500 Internal Server Error` — LLM call failed

---

### 6. Unified Pipeline

**Endpoint:** `POST /pipeline/run`

**Purpose:** Execute complete OKF processing pipeline

**Request:**
```json
{
  "query": "Show me all delinquent loans",
  "conversation_history": []
}
```

**Response:** `200 OK`
```json
{
  "section": "Tables",
  "context": "# Schema Context\n\nTable: loans\nColumns: ...",
  "answer": "Query guidance: Use SELECT ... FROM loans WHERE status='delinquent'",
  "raw_content": "## Loans (type: table)\n\n..."
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | User query |
| `conversation_history` | array | No | Prior turns for context |

**Response Fields:**
- `section` — Classified OKF section
- `context` — Structured schema/business context
- `answer` — Final answer/guidance
- `raw_content` — Raw OKF markdown

**Pipeline Sequence:**
1. `SectionSelectionAgent` → classify into section
2. `SectionRetrievalAgent` → load OKF markdown
3. `ContextBuilderAgent` → structure context
4. `KnowledgeBaseAgent` (if Runbooks/Datasets) → answer from KB
5. Return context (if Tables/Metrics) → for SQL generation

**Example:**
```bash
curl -X POST http://localhost:8002/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me delinquent loans",
    "conversation_history": []
  }'
```

**Errors:**
- `500 Internal Server Error` — Pipeline execution failed (check logs)

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `400` | Bad request (invalid JSON, missing fields) |
| `500` | Server error (LLM API failed, bundle not found, etc.) |

---

## Response Headers

```
Content-Type: application/json
Date: Mon, 20 Jan 2025 14:35:12 GMT
Server: uvicorn
```

---

## Error Response Format

```json
{
  "detail": "Section selection failed: Connection error to OpenAI API"
}
```

---

## Rate Limiting

None currently. Add in production if needed.

---

## Timeouts

- **Default:** 30 seconds (configurable via `OPENAI_TIMEOUT`)
- **LLM API:** Individual LLM calls may timeout

---

## Pagination

Not applicable (no list endpoints).

---

## Request/Response Examples

### Full Example: Complete Workflow

```bash
#!/bin/bash

BASE_URL="http://localhost:8002"
QUERY="Show me all delinquent loans"

# 1. Classify
echo "Step 1: Classifying query..."
SECTION=$(curl -s -X POST $BASE_URL/section-selection \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\"}" | jq -r '.section')
echo "Section: $SECTION"

# 2. Retrieve content
echo "Step 2: Retrieving section content..."
RESPONSE=$(curl -s -X POST $BASE_URL/section-retrieval \
  -H "Content-Type: application/json" \
  -d "{\"section_type\": \"$SECTION\"}")
CONTENT=$(echo $RESPONSE | jq -r '.content')
echo "Loaded $(echo $CONTENT | wc -c) bytes"

# 3. Build context
echo "Step 3: Building context..."
CONTEXT=$(curl -s -X POST $BASE_URL/context-building \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\", \"okf_content\": $(echo $CONTENT | jq -Rs .)}" | jq -r '.system_context')
echo "Context: $(echo $CONTEXT | head -c 100)..."

# Or use unified pipeline
echo "Using unified pipeline..."
curl -s -X POST $BASE_URL/pipeline/run \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\"}" | jq '.'
```

---

## Swagger/OpenAPI

Interactive API documentation available at:

```
http://localhost:8002/docs
```

Browse endpoints, try requests, and view schemas.

---

## SDK Examples

### Python (httpx)

```python
import httpx

async with httpx.AsyncClient(base_url="http://localhost:8002") as client:
    response = await client.post(
        "/pipeline/run",
        json={"query": "Show delinquent loans"}
    )
    result = response.json()
    print(result["answer"])
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8002/pipeline/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'Show delinquent loans' })
});
const result = await response.json();
console.log(result.answer);
```

### Go

```go
import "net/http"
import "encoding/json"

resp, err := http.Post(
  "http://localhost:8002/pipeline/run",
  "application/json",
  strings.NewReader(`{"query":"Show delinquent loans"}`),
)
var result map[string]interface{}
json.NewDecoder(resp.Body).Decode(&result)
```

---

**Last Updated:** 2025-01-20
