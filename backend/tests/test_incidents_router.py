import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


ANALYZE_PAYLOAD = {
    "title": "Payment API returns 503 errors after deployment",
    "service": "payment-api",
    "environment": "production",
    "severity": "high",
    "description": "Error rate jumped to 87% after deploying v2.3.1. Customers cannot complete payments.",
    "logs": "ERROR: connection pool exhausted (pool size: 10, wait timeout: 30s)",
    "recent_changes": "Deployed payment-service v2.3.1",
}


RESOLVE_PAYLOAD = {
    "root_cause": "Database connection pool exhaustion due to pool size changed from 50 to 10 in deployment",
    "fix": "Restored pool size to 50. Rolled back to v2.3.0.",
    "outcome": "Service recovered. Error rate returned to 0%.",
    "resolution_time_minutes": 35,
}


@patch("routers.incidents.AgentService")
def test_analyze_returns_200_with_expected_fields(MockAgentService):
    mock_agent = MockAgentService.return_value
    mock_agent.analyze.return_value = MagicMock(
        incident_id="inc-test001",
        status="analyzed",
        analysis=MagicMock(
            summary="Test summary",
            investigation_steps=["Step 1"],
            possible_causes=["Cause 1"],
            recommended_actions=["Action 1"],
            memory_influenced=False,
        ),
        memory_recall=MagicMock(
            found=False,
            memories=[],
            recall_query_used="503 payment-api production",
        ),
    )
    response = client.post("/incidents/analyze", json=ANALYZE_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == "inc-test001"
    assert "analysis" in data
    assert "memory_recall" in data


def test_analyze_returns_422_on_missing_required_fields():
    response = client.post("/incidents/analyze", json={"title": "Missing fields"})
    assert response.status_code == 422


@patch("routers.incidents.AgentService")
def test_resolve_returns_200(MockAgentService):
    mock_agent = MockAgentService.return_value
    mock_agent.resolve.return_value = MagicMock(
        incident_id="inc-test001",
        memory_stored=True,
        document_id="inc-test001",
        message="Experience stored.",
    )
    response = client.post("/incidents/inc-test001/resolve", json=RESOLVE_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["memory_stored"] is True


@patch("routers.incidents.AgentService")
def test_resolve_returns_404_for_unknown_incident(MockAgentService):
    mock_agent = MockAgentService.return_value
    mock_agent.resolve.side_effect = KeyError("Incident 'unknown' not found.")
    response = client.post("/incidents/unknown/resolve", json=RESOLVE_PAYLOAD)
    assert response.status_code == 404


def test_health_returns_200():
    with patch("routers.health.HindsightService") as MockHindsight:
        MockHindsight.return_value.health_check.return_value = True
        response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
