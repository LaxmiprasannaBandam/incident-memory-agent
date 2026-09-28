from fastapi import APIRouter, HTTPException
from models.schemas import (
    IncidentRequest,
    ResolveRequest,
    AnalyzeResponse,
    ResolveResponse,
    IncidentRecord,
)
from services.agent import AgentService

router = APIRouter(prefix="/incidents", tags=["Incidents"])


def get_agent() -> AgentService:
    return AgentService()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_incident(incident: IncidentRequest):
    """
    Submit a new incident for analysis.

    The agent will:
    1. Search Hindsight for similar historical incidents.
    2. Use any recalled memories to inform the LLM analysis.
    3. Return structured investigation guidance and the recalled memories.
    """
    agent = get_agent()
    try:
        return agent.analyze(incident)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/{incident_id}/resolve", response_model=ResolveResponse)
def resolve_incident(incident_id: str, resolution: ResolveRequest):
    """
    Record the actual root cause, fix, and outcome for a resolved incident.
    Stores the experience as a persistent memory in Hindsight.
    """
    agent = get_agent()
    try:
        return agent.resolve(incident_id, resolution)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resolution failed: {str(e)}")


@router.get("/{incident_id}", response_model=IncidentRecord)
def get_incident(incident_id: str):
    """Retrieve a previously analyzed incident by its ID."""
    agent = get_agent()
    try:
        return agent.get_incident(incident_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
