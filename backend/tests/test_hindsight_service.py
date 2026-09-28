import pytest
from unittest.mock import MagicMock, patch
from models.schemas import IncidentRequest, ResolveRequest
from services.hindsight import build_recall_query, build_memory_text, HindsightService


# ---- build_recall_query tests ----

def test_build_recall_query_includes_title_and_service():
    incident = IncidentRequest(
        title="Payment API returns 503 errors after deployment",
        service="payment-api",
        environment="production",
        severity="high",
        description="503 errors after deploy",
        logs="ERROR: connection pool exhausted",
        recent_changes="Deployed v2.3.1",
    )
    query = build_recall_query(incident)
    assert "payment-api" in query
    assert "production" in query
    assert "503" in query


def test_build_recall_query_handles_empty_logs():
    incident = IncidentRequest(
        title="Service down",
        service="auth-api",
        environment="staging",
        severity="medium",
        description="Auth service is not responding",
    )
    query = build_recall_query(incident)
    assert "auth-api" in query
    assert "staging" in query


def test_build_recall_query_truncates_long_logs():
    long_log = "ERROR: " + "x" * 500
    incident = IncidentRequest(
        title="API Error",
        service="order-api",
        environment="production",
        severity="high",
        description="Something broke",
        logs=long_log,
    )
    query = build_recall_query(incident)
    # The query should not contain more than 200 chars from logs
    # (title + service + env + 200 char log snippet)
    assert len(query) < len(long_log)


# ---- build_memory_text tests ----

def make_test_incident():
    return IncidentRequest(
        title="Payment API returns 503 errors after deployment",
        service="payment-api",
        environment="production",
        severity="high",
        description="Error rate jumped to 87% after deploying v2.3.1",
        logs="ERROR: connection pool exhausted (pool size: 10, wait timeout: 30s)",
        recent_changes="Deployed payment-service v2.3.1",
    )


def make_test_resolution():
    return ResolveRequest(
        root_cause="Database connection pool exhaustion due to pool size changed from 50 to 10 in deployment",
        fix="Restored pool size to 50. Rolled back to v2.3.0.",
        outcome="Service recovered. Error rate returned to 0%.",
        resolution_time_minutes=35,
    )


def test_build_memory_text_contains_required_sections():
    incident = make_test_incident()
    resolution = make_test_resolution()
    text = build_memory_text(incident, resolution, "inc-001")

    assert "INCIDENT RESOLVED" in text
    assert "payment-api" in text
    assert "ROOT CAUSE:" in text
    assert "FIX APPLIED:" in text
    assert "OUTCOME:" in text
    assert "connection pool exhaustion" in text
    assert "RESOLUTION TIME: 35 minutes" in text


def test_build_memory_text_without_resolution_time():
    incident = make_test_incident()
    resolution = ResolveRequest(
        root_cause="CPU spike",
        fix="Scaled up instances",
        outcome="Recovered",
    )
    text = build_memory_text(incident, resolution, "inc-002")
    assert "RESOLUTION TIME" not in text


def test_build_memory_text_handles_missing_optional_fields():
    incident = IncidentRequest(
        title="Auth service failure",
        service="auth-api",
        environment="production",
        severity="critical",
        description="Auth service is down",
    )
    resolution = make_test_resolution()
    text = build_memory_text(incident, resolution, "inc-003")
    assert "No logs provided" in text
    assert "No changes recorded" in text


# ---- HindsightService unit tests (mocked) ----

def make_mock_hindsight_service():
    """Return a HindsightService with the underlying client mocked."""
    with patch("services.hindsight.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            hindsight_base_url="http://localhost:8888",
            hindsight_bank_id="incident-memory",
        )
        with patch("services.hindsight.Hindsight") as MockHindsight:
            service = HindsightService()
            service._client = MockHindsight.return_value
            return service


def test_recall_returns_texts_when_memories_found():
    service = make_mock_hindsight_service()
    mock_result_1 = MagicMock()
    mock_result_1.text = "ROOT CAUSE: connection pool exhaustion"
    mock_result_2 = MagicMock()
    mock_result_2.text = "FIX: rolled back deployment"
    service._client.recall.return_value = MagicMock(results=[mock_result_1, mock_result_2])

    results = service.recall("503 payment-api production")
    assert len(results) == 2
    assert "connection pool exhaustion" in results[0]


def test_recall_returns_empty_list_when_no_memories():
    service = make_mock_hindsight_service()
    service._client.recall.return_value = MagicMock(results=[])

    results = service.recall("unrelated query about nothing")
    assert results == []


def test_recall_returns_empty_list_on_exception():
    service = make_mock_hindsight_service()
    service._client.recall.side_effect = Exception("Connection refused")

    results = service.recall("any query")
    assert results == []


def test_retain_returns_true_on_success():
    service = make_mock_hindsight_service()
    service._client.retain.return_value = None

    result = service.retain(content="Incident memory text", document_id="inc-001")
    assert result is True
    service._client.retain.assert_called_once_with(
        bank_id="incident-memory",
        content="Incident memory text",
        document_id="inc-001",
        context="resolved production incident",
    )


def test_retain_returns_false_on_exception():
    service = make_mock_hindsight_service()
    service._client.retain.side_effect = Exception("Server error")

    result = service.retain(content="some content", document_id="inc-002")
    assert result is False
