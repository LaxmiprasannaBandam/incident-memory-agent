import logging
from typing import List, Optional
from hindsight_client import Hindsight
from config import get_settings
from models.schemas import IncidentRequest, ResolveRequest

logger = logging.getLogger(__name__)


def build_recall_query(incident: IncidentRequest) -> str:
    """
    Build a dense factual query for Hindsight recall.
    Short and specific to maximize semantic + keyword matching.
    """
    parts = []

    # Start with the most discriminating signal: error type + service + env
    parts.append(incident.title)
    parts.append(incident.service)
    parts.append(incident.environment)

    # Pull keywords from logs (first 200 chars to stay concise)
    if incident.logs:
        parts.append(incident.logs[:200])

    # Add recent changes context
    if incident.recent_changes:
        parts.append(incident.recent_changes[:150])

    return " ".join(parts)


def build_memory_text(
    incident: IncidentRequest,
    resolution: ResolveRequest,
    incident_id: str,
) -> str:
    """
    Build the structured memory text that will be stored in Hindsight.

    Plain structured text lets Hindsight's internal extraction identify
    entities (service names, error types), facts (root cause), and
    relationships (service → deployment → failure) automatically.
    """
    resolution_time_str = (
        f"\nRESOLUTION TIME: {resolution.resolution_time_minutes} minutes"
        if resolution.resolution_time_minutes
        else ""
    )

    return f"""INCIDENT RESOLVED

Title: {incident.title}
Service: {incident.service}
Environment: {incident.environment}
Severity: {incident.severity}
Incident ID: {incident_id}

DESCRIPTION:
{incident.description}

SYMPTOMS / LOGS:
{incident.logs or 'No logs provided'}

RECENT CHANGES:
{incident.recent_changes or 'No changes recorded'}

ROOT CAUSE:
{resolution.root_cause}

FIX APPLIED:
{resolution.fix}

OUTCOME:
{resolution.outcome}{resolution_time_str}
"""


class HindsightService:
    """
    Wrapper around the official hindsight-client SDK.
    Provides retain and recall operations for incident memories.
    """

    def __init__(self):
        settings = get_settings()
        self._base_url = settings.hindsight_base_url
        self._bank_id = settings.hindsight_bank_id
        self._client = Hindsight(base_url=self._base_url, timeout=30.0)

    async def ensure_bank_exists(self) -> bool:
        """Create the memory bank if it does not already exist.

        Must be awaited — uses acreate_bank to avoid running a blocking
        sync wrapper inside an already-running asyncio event loop (which
        would raise 'This event loop is already running' and leave the
        underlying coroutine un-awaited).
        """
        try:
            await self._client.acreate_bank(
                bank_id=self._bank_id,
                name="Incident Memory Bank",
                mission=(
                    "You store resolved production incidents. Each memory describes "
                    "an incident's symptoms, root cause, fix applied, and outcome. "
                    "Use this knowledge to help engineers recognize patterns in future incidents."
                ),
            )
            logger.info("Created Hindsight bank '%s'", self._bank_id)
            return True
        except Exception as e:
            logger.debug("Bank creation returned: %s (may already exist)", str(e))
            return True

    def health_check(self) -> bool:
        """Verify Hindsight server is reachable."""
        try:
            version = self._client.get_version()
            logger.info("Hindsight version: %s", version.api_version)
            return True
        except Exception as e:
            logger.error("Hindsight health check failed: %s", str(e))
            return False

    def recall(self, query: str) -> List[str]:
        """
        Search Hindsight for memories relevant to the given query.
        Returns a list of memory text strings.
        """
        try:
            logger.info("Recalling memories with query: '%s'", query)
            response = self._client.recall(
                bank_id=self._bank_id,
                query=query,
                budget="mid",
            )
            texts = [r.text for r in response.results if r.text]
            logger.info("Recall returned %d memories", len(texts))
            return texts
        except Exception as e:
            logger.error("Hindsight recall failed: %s", str(e))
            return []

    def retain(self, content: str, document_id: str) -> bool:
        """
        Store a resolved incident memory in Hindsight.
        Uses document_id to allow upserts if the same incident is updated.
        """
        try:
            logger.info("Retaining memory with document_id='%s'", document_id)
            self._client.retain(
                bank_id=self._bank_id,
                content=content,
                document_id=document_id,
                context="resolved production incident",
            )
            logger.info("Memory retained successfully for document_id='%s'", document_id)
            return True
        except Exception as e:
            logger.error("Hindsight retain failed: %s", str(e))
            return False
