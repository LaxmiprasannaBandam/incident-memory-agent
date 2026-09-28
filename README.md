# Incident Memory & Response Agent

An AI-powered incident response agent for software engineering and DevOps teams.

The agent uses **Hindsight persistent memory by Vectorize** to remember previous production incidents, including their symptoms, root causes, fixes, and outcomes. When a similar incident occurs later, the agent recalls relevant past experiences and provides context-aware investigation guidance.

## Why this matters

Production incidents often repeat familiar patterns. Engineers may have solved a similar problem months earlier, but that knowledge can be difficult to find quickly.

This project gives an AI incident-response agent persistent memory:

```text
New incident
     ↓
Recall relevant past incidents from Hindsight
     ↓
Combine current incident + historical context
     ↓
AI generates investigation guidance
     ↓
Engineer resolves the incident
     ↓
Resolution is stored in Hindsight
     ↓
Future incidents can recall this experience

The key idea is that the agent does not only answer the current incident. It learns from resolved incidents and uses those experiences in future investigations.

How Hindsight is used

Hindsight is the persistent memory layer of the application.

During incident analysis

The agent builds a recall query using important incident signals:

Incident title
Service
Environment
Logs
Recent changes

It sends this query to the Hindsight memory bank:

incident-memory

Relevant historical memories are returned and passed to the Groq-powered analysis agent.

After incident resolution

The engineer provides:

Root cause
Fix applied
Outcome
Resolution time

The complete incident experience is then retained in Hindsight.

This creates a continuous learning loop:

RECALL
  ↓
Analyze current incident using past experience
  ↓
RESOLVE
  ↓
RETAIN
  ↓
Future incidents can recall the experience
Demonstrated memory behavior

The application was tested using multiple related payment-service incidents.

Incident 1

The first payment API incident had no previous matching incident in memory.

The agent analyzed the incident and the engineer resolved it.

The resolution was then stored in Hindsight.

Incident 2

A second payment API incident occurred after another deployment.

Hindsight recalled historical incidents containing:

Payment API 503 errors
Database connection pool exhaustion
Previous deployment information
Root causes
Fixes
Outcomes

The agent used those memories to recommend checking the database connection pool configuration.

Incident 3

A third incident used different wording:

Checkout payments failing with database timeout errors

The system still recalled previous related incidents and recognized the same underlying pattern:

Payment API 503 errors
        +
Database connection timeouts
        +
Connection pool at maximum capacity
        +
Recent deployment
        ↓
Previous incident pattern
        ↓
Connection pool configuration should be investigated

This demonstrates the main purpose of persistent memory: the agent can reuse experience from previous incidents rather than starting from zero each time.

Architecture
┌──────────────────────────────────────────────┐
│              React Frontend                  │
│        Vite + Tailwind + React               │
│                                              │
│  Incident Form → Analysis → Resolution      │
└──────────────────────┬───────────────────────┘
                       │ HTTP
                       ▼
┌──────────────────────────────────────────────┐
│              FastAPI Backend                 │
│                                              │
│  Incident Router                             │
│        │                                     │
│        ▼                                     │
│  Agent Service                               │
│     ├── Hindsight Service                    │
│     │      ├── Recall                        │
│     │      └── Retain                        │
│     │                                        │
│     └── Groq Service                         │
│            └── LLM Analysis                  │
└───────────────┬─────────────────┬────────────┘
                │                 │
                ▼                 ▼
       ┌────────────────┐   ┌────────────────┐
       │ Hindsight      │   │ Groq API       │
       │ Docker :8888   │   │ LLM            │
       │ Persistent     │   │                │
       │ Memory         │   │                │
       └────────────────┘   └────────────────┘
Tech stack
Layer	Technology
Frontend	React 18, Vite, Tailwind CSS
Backend	Python 3.11, FastAPI, Uvicorn
LLM	Groq
Agent model	openai/gpt-oss-120b
Persistent memory	Hindsight by Vectorize
Hindsight SDK	hindsight-client
Memory server	Docker
API communication	HTTP / REST
Testing	Pytest
Project structure
incident-memory-agent/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── seed_demo.py
│   │
│   ├── data/
│   │   └── demo_incidents.json
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── routers/
│   │   ├── health.py
│   │   └── incidents.py
│   │
│   ├── services/
│   │   ├── agent.py
│   │   ├── hindsight.py
│   │   └── groq_client.py
│   │
│   └── tests/
│       ├── test_hindsight_service.py
│       ├── test_groq_service.py
│       └── test_incidents_router.py
│
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
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
Prerequisites

Install the following:

Docker Desktop
Node.js 18+
Python 3.11+
Groq API key
Setup
1. Clone the repository
git clone https://github.com/LaxmiprasannaBandam/incident-memory-agent.git
cd incident-memory-agent
2. Configure environment variables

Create a .env file from .env.example.

cp .env.example .env

Then configure:

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b

HINDSIGHT_BASE_URL=http://localhost:8888
HINDSIGHT_BANK_ID=incident-memory

HINDSIGHT_API_LLM_PROVIDER=groq
HINDSIGHT_API_LLM_API_KEY=your_groq_api_key_here
HINDSIGHT_API_LLM_GROQ_SERVICE_TIER=on_demand

Never commit .env to GitHub.

The repository includes .env.example as a safe configuration template.

3. Start Hindsight

From the project root:

docker compose up hindsight -d

Hindsight runs locally on:

http://localhost:8888

The application uses the Hindsight memory bank:

incident-memory
4. Start the backend

Open a terminal:

cd backend
pip install -r requirements.txt
uvicorn main:app --reload

The backend runs at:

http://localhost:8000

FastAPI documentation:

http://localhost:8000/docs
5. Start the frontend

Open another terminal:

cd frontend
npm install
npm run dev

The frontend runs at:

http://localhost:5173
Health check

The backend provides:

GET /health

Expected response:

{
  "status": "ok",
  "hindsight": "connected"
}
Demo workflow

The strongest demonstration is a simple before-and-after memory flow.

1. Submit the first incident

Example:

Title:
Payment API returns 503 errors after deployment

Service:
payment-api

Environment:
production

Severity:
high

Description:
Error rate increased after deployment and customers cannot complete payments.

Logs:
Database connections are timing out and the connection pool is exhausted.

Recent changes:
A new payment service version was deployed shortly before the incident.

Because there is no previous matching experience yet, the UI shows:

No similar historical incidents found.
2. Resolve the incident

Enter the actual resolution:

Root cause:
Database connection pool was exhausted after deployment due to incorrect connection pool configuration.

Fix:
Increased the database connection pool size, corrected the configuration, restarted the payment service, and verified database connectivity.

Outcome:
Payment API recovered and 503 errors stopped.

The application stores this experience in Hindsight.

3. Submit a similar incident

Use different wording:

Title:
Checkout payments failing with database timeout errors

Service:
payment-api

Environment:
production

Severity:
high

Now Hindsight recalls related historical experiences.

The UI displays the recalled memories and the AI analysis uses them when generating investigation guidance.

4. Observe the learning effect

The important visual change is:

FIRST INCIDENT

No historical memory
        ↓
Generic investigation
        ↓
Resolution stored


FUTURE INCIDENT

Historical memories recalled
        ↓
Previous root causes and fixes visible
        ↓
Context-aware investigation

This is the core behavior demonstrated by the application.

API endpoints
Method	Endpoint	Purpose
GET	/health	Backend and Hindsight health
POST	/incidents/analyze	Analyze a new incident
POST	/incidents/{incident_id}/resolve	Store incident resolution
GET	/incidents/{incident_id}	Retrieve incident information
Running tests

From the backend directory:

pytest tests/ -v

The test suite covers:

Test	Coverage
test_hindsight_service.py	Recall/retain logic and memory formatting
test_groq_service.py	Prompt construction and LLM response parsing
test_incidents_router.py	Incident API endpoints
Hindsight memory design

Each resolved incident is converted into a structured memory containing information such as:

INCIDENT RESOLVED

Title: ...
Service: ...
Environment: ...
Severity: ...
Description: ...
Logs: ...
Recent Changes: ...

ROOT CAUSE: ...
FIX APPLIED: ...
OUTCOME: ...
RESOLUTION TIME: ...

The incident ID is used as the document identifier when retaining the experience.

The application then uses Hindsight recall when analyzing future incidents.

This allows the system to preserve operational experience across separate incident interactions.

Key implementation idea

The central agent flow is:

Current Incident
      │
      ▼
Build Recall Query
      │
      ▼
Hindsight Recall
      │
      ▼
Historical Incident Memories
      │
      ▼
Groq Analysis
      │
      ▼
Investigation Guidance
      │
      ▼
Engineer Resolves Incident
      │
      ▼
Hindsight Retain

The memory layer is therefore part of the agent's decision-making workflow rather than being only a storage layer.

Limitations

This project is a prototype for demonstrating persistent-memory incident response.

Current limitations include:

Incident information is entered manually.
Production logs and monitoring systems are not directly connected.
Resolution quality depends on the information recorded by the engineer.
The prototype does not automatically execute remediation actions.
Memory relevance depends on the quality and similarity of recalled incidents.
Future improvements

Potential extensions include:

Integration with monitoring and alerting platforms
Automatic ingestion of production logs
Slack/Teams incident-response integration
Automated incident timeline generation
Post-incident review generation
More detailed incident similarity evaluation
Safe automated remediation suggestions
Team-level operational knowledge sharing
License

This project is provided for demonstration and educational purposes.