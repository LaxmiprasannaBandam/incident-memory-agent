import pytest
from unittest.mock import MagicMock, patch
from models.schemas import IncidentRequest
from services.groq_client import build_prompt, parse_llm_response, GroqService


def make_incident():
    return IncidentRequest(
        title="Payment API returns 503 errors after deployment",
        service="payment-api",
        environment="production",
        severity="high",
        description="Error rate jumped to 87% after deploying v2.3.1",
        logs="ERROR: connection pool exhausted (pool size: 10)",
        recent_changes="Deployed payment-service v2.3.1",
    )


# ---- build_prompt tests ----

def test_build_prompt_with_no_memories_says_no_history():
    incident = make_incident()
    prompt = build_prompt(incident, memories=[])
    assert "No relevant historical incidents" in prompt
    assert "payment-api" in prompt
    assert "503" in prompt


def test_build_prompt_with_memories_injects_them():
    incident = make_incident()
    memories = [
        "ROOT CAUSE: Database connection pool exhaustion\nFIX: Restored pool size"
    ]
    prompt = build_prompt(incident, memories=memories)
    assert "HISTORICAL INCIDENTS FROM HINDSIGHT MEMORY" in prompt
    assert "Memory 1" in prompt
    assert "connection pool exhaustion" in prompt
    assert "IMPORTANT: Historical memories were found" in prompt


def test_build_prompt_with_multiple_memories_numbers_them():
    incident = make_incident()
    memories = ["Memory about incident A", "Memory about incident B"]
    prompt = build_prompt(incident, memories=memories)
    assert "Memory 1" in prompt
    assert "Memory 2" in prompt


def test_build_prompt_includes_all_incident_fields():
    incident = make_incident()
    prompt = build_prompt(incident, memories=[])
    assert "production" in prompt
    assert "high" in prompt
    assert "connection pool exhausted" in prompt
    assert "v2.3.1" in prompt


# ---- parse_llm_response tests ----

VALID_JSON_RESPONSE = '''{
  "summary": "The incident shows signs of resource exhaustion.",
  "investigation_steps": ["Check connection pool metrics", "Review deployment config"],
  "possible_causes": ["Connection pool exhaustion", "Misconfigured deployment"],
  "recommended_actions": ["Roll back deployment", "Increase pool size"],
  "memory_influenced": true
}'''


def test_parse_llm_response_valid_json():
    result = parse_llm_response(VALID_JSON_RESPONSE)
    assert result.summary == "The incident shows signs of resource exhaustion."
    assert len(result.investigation_steps) == 2
    assert result.memory_influenced is True


def test_parse_llm_response_strips_markdown_fences():
    wrapped = f"```json\n{VALID_JSON_RESPONSE}\n```"
    result = parse_llm_response(wrapped)
    assert result.summary == "The incident shows signs of resource exhaustion."


def test_parse_llm_response_returns_safe_default_on_invalid_json():
    result = parse_llm_response("This is not JSON at all")
    assert result.summary != ""
    assert result.memory_influenced is False
    assert len(result.investigation_steps) > 0


def test_parse_llm_response_handles_partial_json():
    partial = '{"summary": "Partial response"}'
    result = parse_llm_response(partial)
    assert result.summary == "Partial response"
    assert result.investigation_steps == []
