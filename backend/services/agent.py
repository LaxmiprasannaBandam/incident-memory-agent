import logging
import uuid
from datetime import datetime, timezone
from typing import Dict

from models.schemas import (
    IncidentRequest,
    ResolveRequest,
    AnalyzeResponse,
    ResolveResponse,
    IncidentRecord,
    IncidentAnalysis,
    MemoryRecallResult,
    RecalledMemory,
)
from services.hindsight import HindsightService, build_recall_query, build_memory_text
from services.groq_client import GroqService

logger = logging.getLogger(__name__)

# In-memory store for active incidents (sufficient for demo scope)
# Maps incident_id -> IncidentRecord
_incidents: Dict[str, IncidentRecord] = {}


class AgentService:
    """
    Orchestrates the full incident analysis and resolution workflow:

    analyze:
      1. Build recall query from incident
      2. Recall relevant memories from Hindsight
      3. Call Groq LLM with current incident + historical memories
      4. Return analysis + recalled memories

    resolve:
      5. Accept engineer's root cause, fix, outcome
      6. Build structured memory text
      7. Retain in Hindsight
      8. Return confirmation
    """

    def __init__(self):
        self._hindsight = HindsightService()
        self._groq = GroqService()

    def analyze(self, incident: IncidentRequest) -> AnalyzeResponse:
        """Run the full analysis pipeline for a new incident."""
        incident_id = f"inc-{uuid.uuid4().hex[:8]}"
        logger.info("Analyzing incident '%s' (id=%s)", incident.title, incident_id)

        # Step 1: Build recall query
        recall_query = build_recall_query(incident)
        logger.info("Recall query: '%s'", recall_query)

        # Step 2: Recall memories from Hindsight
        raw_memories = self._hindsight.recall(recall_query)
        logger.info("Retrieved %d memories from Hindsight", len(raw_memories))

        # Step 3: Build memory recall result for the response
        memory_recall = MemoryRecallResult(
            found=len(raw_memories) > 0,
            memories=[
                RecalledMemory(
                    text=mem,
                    relevance_note="Retrieved from Hindsight memory bank based on similarity to current incident.",
                )
                for mem in raw_memories
            ],
            recall_query_used=recall_query,
        )

        # Step 4: Analyze with Groq LLM (passes memories for context injection)
        try:
            analysis = self._groq.analyze_incident(incident, raw_memories)
        except RuntimeError as e:
            logger.error("LLM analysis failed: %s", str(e))
            analysis = IncidentAnalysis(
                summary=f"Automated analysis unavailable: {str(e)}",
                investigation_steps=["Review the incident manually."],
                possible_causes=["Unknown — LLM unavailable."],
                recommended_actions=["Retry or investigate manually."],
                memory_influenced=False,
            )

        # Store record for later resolution
        record = IncidentRecord(
            incident_id=incident_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            request=incident,
            analysis=analysis,
            memory_recall=memory_recall,
            status="open",
        )
        _incidents[incident_id] = record
        logger.info("Incident record stored for id=%s", incident_id)

        return AnalyzeResponse(
            incident_id=incident_id,
            status="analyzed",
            analysis=analysis,
            memory_recall=memory_recall,
        )

    def resolve(self, incident_id: str, resolution: ResolveRequest) -> ResolveResponse:
        """Record the resolution and retain the experience in Hindsight."""
        if incident_id not in _incidents:
            raise KeyError(f"Incident '{incident_id}' not found.")

        record = _incidents[incident_id]
        incident = record.request

        logger.info("Resolving incident id=%s", incident_id)

        # Step 5: Build structured memory text
        memory_text = build_memory_text(incident, resolution, incident_id)
        logger.debug("Memory text to retain:\n%s", memory_text)

        # Step 6: Retain in Hindsight
        stored = self._hindsight.retain(
            content=memory_text,
            document_id=incident_id,
        )

        # Update record
        record.resolution = resolution
        record.status = "resolved"
        _incidents[incident_id] = record

        return ResolveResponse(
            incident_id=incident_id,
            memory_stored=stored,
            document_id=incident_id,
            message=(
                "Incident experience stored in Hindsight memory bank. "
                "The agent will use this for future similar incidents."
                if stored
                else "Resolution recorded but memory storage failed. Check Hindsight connectivity."
            ),
        )

    def get_incident(self, incident_id: str) -> IncidentRecord:
        """Retrieve an incident record by ID."""
        if incident_id not in _incidents:
            raise KeyError(f"Incident '{incident_id}' not found.")
        return _incidents[incident_id]
