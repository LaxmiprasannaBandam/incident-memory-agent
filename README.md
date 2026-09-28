# Incident Memory & Response Agent

An AI-powered incident response agent for software engineering and DevOps teams. The agent uses **Hindsight persistent memory** to remember previous production incidents, their symptoms, root causes, fixes, and outcomes. When a similar incident occurs later, the agent recalls that experience and provides context-aware investigation guidance.

Built for the **"AI Agents That Learn Using Hindsight"** challenge.

---

## How it works

```
Engineer submits incident
        │
        ▼
1. Build recall query from incident fields
        │
        ▼
2. Search Hindsight for similar past incidents  ◄── PERSISTENT MEMORY
        │
        ▼
3. Inject recalled memories into LLM prompt
        │
        ▼
4. Groq LLM analyzes current incident + historical context
        │
        ▼
5. Return analysis + visible memory recall to engineer
        │
   Engineer investigates and resolves
        │
        ▼
6. Record root cause, fix, outcome
        │
        ▼
7. Store experience in Hindsight  ◄── LEARNS FOR NEXT TIME
```

**Hindsight is the core differentiator.** Without it, the agent gives generic advice. With it, the agent explicitly surfaces what happened last time and why it's relevant — reducing mean time to resolution on repeat patterns.

---

## Architecture

```
┌─────────────────────────────────────────┐
│           React Frontend                │
│   (Vite · Tailwind · React Router)      │
└──────────────────┬──────────────────────┘
                   │ HTTP (proxied)
┌──────────────────▼──────────────────────┐
│         FastAPI Backend (Python)        │
│                                         │
│  AgentService                           │
│    → HindsightService (recall/retain)   │
│    → GroqService (LLM analysis)         │
└──────────────────┬──────────────────────┘
          ┌────────┴──────────┐
          ▼                   ▼
  Hindsight Server        Groq API
  (Docker :8888)          (llama-3.3-70b)
```

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Node.js](https://nodejs.org/) 18+ (for frontend development)
- [Python](https://www.python.org/) 3.11+ (for backend development)
- A [Groq API key](https://console.groq.com/)

---

## Setup

### 1. Clone and configure environment

```bash
git clone <repo-url>
cd incident-memory-agent
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

HINDSIGHT_API_LLM_PROVIDER=groq
HINDSIGHT_API_LLM_API_KEY=your_groq_api_key_here

HINDSIGHT_BASE_URL=http://localhost:8888
HINDSIGHT_BANK_ID=incident-memory
```

> **Note:** Hindsight needs an LLM internally to extract facts from memories. We use Groq for both roles.

### 2. Start Hindsight

```bash
docker compose up hindsight -d
```

Wait until Hindsight is healthy (check: `curl http://localhost:8888/health`).

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

### 5. Verify health

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok", "hindsight": "connected"}
```

---

## Running the full demo

This is the canonical proof that Hindsight memory works.

### Step 1 — Incident 1 (no memory yet)

Submit in the UI:
- **Title:** Payment API returns 503 errors after deployment
- **Service:** payment-api
- **Environment:** production
- **Severity:** high
- **Description:** Error rate jumped to 87% after deploying v2.3.1. Customers cannot complete payments.
- **Logs:** `ERROR: connection pool exhausted (pool size: 10, wait timeout: 30s)`
- **Recent changes:** Deployed payment-service v2.3.1 with updated database configuration

**Expected:** Memory Recall panel shows "No similar historical incidents found."

### Step 2 — Resolve Incident 1

Click "Record Resolution & Store Memory", then enter:
- **Root cause:** Database connection pool exhaustion. v2.3.1 changed pool size from 50 to 10.
- **Fix:** Restored pool size to 50. Rolled back to v2.3.0.
- **Outcome:** Service recovered. Error rate returned to 0%.
- **Resolution time:** 35

**Expected:** "✅ Experience stored in Hindsight memory."

### Step 3 — Incident 2 (memory recalled)

Submit a new incident:
- **Title:** Payment API 503s spiking after tonight's release
- **Service:** payment-api
- **Environment:** production
- **Severity:** critical
- **Description:** After releasing v2.4.0, we're seeing 503 errors. Customers are being declined at checkout.
- **Logs:** `WARN: connection pool near limit (47/50), ERROR: pool exhausted`
- **Recent changes:** Deployed payment-service v2.4.0

**Expected:**
- 🧠 Memory Recall banner appears (amber highlight)
- The recalled memory shows the previous root cause (connection pool exhaustion) and fix
- The AI analysis explicitly references the historical incident and recommends checking connection pool configuration first

### Demo shortcut: seed the memory first

To skip Step 1 and 2 in a live demo (pre-load the memory):

```bash
cd backend
python seed_demo.py --payment-only
```

Then go directly to Step 3.

---

## Running tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### What the tests cover

| Test file | What it tests |
|---|---|
| `tests/test_hindsight_service.py` | `build_recall_query`, `build_memory_text`, `HindsightService.recall/retain` (mocked) |
| `tests/test_groq_service.py` | `build_prompt` with/without memories, `parse_llm_response` JSON parsing |
| `tests/test_incidents_router.py` | API endpoints via FastAPI `TestClient` (mocked services) |

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ | Groq API key from console.groq.com |
| `GROQ_MODEL` | Optional | Model to use (default: `llama-3.3-70b-versatile`) |
| `HINDSIGHT_API_LLM_PROVIDER` | ✅ | LLM provider for Hindsight (`groq`) |
| `HINDSIGHT_API_LLM_API_KEY` | ✅ | API key for Hindsight's internal LLM |
| `HINDSIGHT_BASE_URL` | Optional | Hindsight server URL (default: `http://localhost:8888`) |
| `HINDSIGHT_BANK_ID` | Optional | Memory bank name (default: `incident-memory`) |

---

## Project structure

```
incident-memory-agent/
├── backend/
│   ├── main.py               # FastAPI entry point
│   ├── config.py             # Environment variable management
│   ├── requirements.txt
│   ├── seed_demo.py          # Pre-seed Hindsight with demo incidents
│   ├── data/
│   │   └── demo_incidents.json
│   ├── models/
│   │   └── schemas.py        # Pydantic request/response models
│   ├── routers/
│   │   ├── health.py         # GET /health
│   │   └── incidents.py      # POST /incidents/analyze, POST /{id}/resolve, GET /{id}
│   ├── services/
│   │   ├── agent.py          # Core orchestration: recall → LLM → retain
│   │   ├── hindsight.py      # Hindsight SDK wrapper + memory format builders
│   │   └── groq_client.py    # Groq LLM wrapper + prompt builder
│   └── tests/
│       ├── test_hindsight_service.py
│       ├── test_groq_service.py
│       └── test_incidents_router.py
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       ├── components/
│       │   ├── AnalysisPanel.jsx
│       │   ├── IncidentForm.jsx
│       │   ├── MemoryRecall.jsx
│       │   ├── ResolutionForm.jsx
│       │   └── StatusBadge.jsx
│       └── pages/
│           ├── NewIncident.jsx
│           └── ResolveIncident.jsx
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS |
| Backend | Python 3.11, FastAPI, Uvicorn |
| LLM | Groq (llama-3.3-70b-versatile) |
| Persistent memory | Hindsight by Vectorize (`hindsight-client`) |
| Memory server | Docker (`ghcr.io/vectorize-io/hindsight`) |

---

## Hindsight memory design

Each resolved incident is stored as a structured plain-text document:

```
INCIDENT RESOLVED

Title: <title>
Service: <service>
Environment: <env>
...
ROOT CAUSE: <root cause>
FIX APPLIED: <fix>
OUTCOME: <outcome>
RESOLUTION TIME: <minutes>
```

Plain text lets Hindsight's internal extraction automatically identify entities (service names, error types), facts (root cause), and relationships (service → deployment → failure pattern). No manual tagging or schema design required.

Recall queries are built by concatenating the most discriminating signal from the new incident: title + service + environment + log snippet. Hindsight's multi-strategy retrieval (semantic + keyword + graph) matches on all of these dimensions simultaneously.
