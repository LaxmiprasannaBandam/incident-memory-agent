import json
import logging
from typing import List
from groq import Groq
from config import get_settings
from models.schemas import IncidentRequest, IncidentAnalysis

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert incident response agent for software engineering and DevOps teams.

Your role is to analyze production incidents and provide structured investigation guidance.

When historical incident memories are provided, you MUST:
1. Explicitly reference what happened in the historical incident.
2. Explain why that history is relevant to the current incident.
3. Use that experience to prioritize your investigation steps and recommendations.

Always respond with a valid JSON object matching this exact schema:
{
  "summary": "<one or two sentence summary of the incident and your assessment>",
  "investigation_steps": ["<step 1>", "<step 2>", "..."],
  "possible_causes": ["<cause 1>", "<cause 2>", "..."],
  "recommended_actions": ["<action 1>", "<action 2>", "..."],
  "memory_influenced": <true if historical memories shaped your analysis, false otherwise>
}

Provide 3-5 items per list. Be specific and actionable. Do not include markdown, code blocks, or any text outside the JSON object."""


def build_prompt(incident: IncidentRequest, memories: List[str]) -> str:
    """
    Build the user-turn prompt for the LLM.
    Injects retrieved historical memories when present.
    """
    prompt_parts = []

    if memories:
        prompt_parts.append("HISTORICAL INCIDENTS FROM HINDSIGHT MEMORY:")
        prompt_parts.append(
            "The following incidents were retrieved from the persistent memory system "
            "because they are similar to the current incident. Use them to inform your analysis."
        )
        for i, memory in enumerate(memories, 1):
            prompt_parts.append(f"\n--- Memory {i} ---")
            prompt_parts.append(memory)
        prompt_parts.append("--- End of historical memories ---\n")
    else:
        prompt_parts.append(
            "HISTORICAL INCIDENTS FROM HINDSIGHT MEMORY:\n"
            "No relevant historical incidents were found in memory. "
            "Provide general incident investigation guidance.\n"
        )

    prompt_parts.append("CURRENT INCIDENT:")
    prompt_parts.append(f"Title: {incident.title}")
    prompt_parts.append(f"Service: {incident.service}")
    prompt_parts.append(f"Environment: {incident.environment}")
    prompt_parts.append(f"Severity: {incident.severity}")
    prompt_parts.append(f"\nDescription:\n{incident.description}")

    if incident.logs:
        prompt_parts.append(f"\nLogs / Error Output:\n{incident.logs}")

    if incident.recent_changes:
        prompt_parts.append(f"\nRecent Changes / Deployments:\n{incident.recent_changes}")

    if memories:
        prompt_parts.append(
            "\nIMPORTANT: Historical memories were found. Your response MUST explicitly "
            "reference what happened previously and explain the connection to the current incident."
        )

    prompt_parts.append(
        "\nAnalyze this incident and respond with a JSON object as specified in the system prompt."
    )

    return "\n".join(prompt_parts)


def parse_llm_response(content: str) -> IncidentAnalysis:
    """
    Parse the LLM JSON response into an IncidentAnalysis object.
    Falls back to a safe default if parsing fails.
    """
    try:
        # Strip any accidental markdown code fences
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        data = json.loads(cleaned)
        return IncidentAnalysis(
            summary=data.get("summary", "Analysis unavailable."),
            investigation_steps=data.get("investigation_steps", []),
            possible_causes=data.get("possible_causes", []),
            recommended_actions=data.get("recommended_actions", []),
            memory_influenced=data.get("memory_influenced", False),
        )
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error("Failed to parse LLM response as JSON: %s\nRaw content: %s", str(e), content)
        return IncidentAnalysis(
            summary="The agent analyzed the incident but could not structure the response. Please review logs.",
            investigation_steps=["Review backend logs for the raw LLM response."],
            possible_causes=["Unknown — LLM response parsing failed."],
            recommended_actions=["Retry the analysis."],
            memory_influenced=False,
        )


class GroqService:
    """Wraps the official Groq Python SDK for incident analysis."""

    def __init__(self):
        settings = get_settings()
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.groq_model

    def analyze_incident(self, incident: IncidentRequest, memories: List[str]) -> IncidentAnalysis:
        """
        Analyze an incident using Groq LLM.
        Injects historical memories into the prompt when provided.
        """
        user_prompt = build_prompt(incident, memories)
        logger.info(
            "Calling Groq model '%s' with %d memory context(s)",
            self._model,
            len(memories),
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,  # Low temperature for consistent, factual analysis
                max_tokens=1500,
            )
            raw_content = response.choices[0].message.content
            logger.info("Groq response received (%d chars)", len(raw_content))
            return parse_llm_response(raw_content)

        except Exception as e:
            logger.error("Groq API call failed: %s", str(e))
            raise RuntimeError(f"LLM analysis failed: {str(e)}") from e
