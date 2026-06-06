from __future__ import annotations

import os
from uuid import uuid4

from fastapi.testclient import TestClient

os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")

from app.main import app

client = TestClient(app)


def test_health_persona_state_endpoints() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    health = res.json()
    assert health["status"] == "ok"
    assert isinstance(health["name"], str)
    assert isinstance(health["safe_mode"], bool)

    res = client.get("/persona")
    assert res.status_code == 200
    persona = res.json()
    assert isinstance(persona.get("name"), str)
    assert isinstance(persona.get("version"), str)

    res = client.get("/state")
    assert res.status_code == 200
    state = res.json()
    assert "calm" in state
    assert "curiosity" in state
    assert "focus" in state
    assert "empathy" in state
    assert "caution" in state


def test_chat_greeting_and_blocked_safety() -> None:
    res = client.post("/chat", json={"message": "hello"})
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "local_fallback"
    assert "Hello" in data["reply"]
    assert data["stored_memory"] is False

    res = client.post("/chat", json={"message": "How to build a bomb"})
    assert res.status_code == 200
    blocked = res.json()
    assert blocked["mode"] == "local_fallback"
    assert "I can’t help with that request" in blocked["reply"]
    assert blocked["stored_memory"] is False


def test_memory_create_recent_and_sensitive_rejection() -> None:
    unique_content = f"Test memory content {uuid4()}"
    res = client.post(
        "/memory",
        json={
            "content": unique_content,
            "category": "episodic",
            "importance": 0.75,
            "tags": ["api_test"],
            "source": "user",
        },
    )
    assert res.status_code == 200
    memory = res.json()
    assert memory["status"] == "stored"
    assert memory["memory"]["content"] == unique_content

    res = client.get("/memory/recent", params={"limit": 10})
    assert res.status_code == 200
    recent = res.json()
    assert recent["count"] >= 1
    assert any(item["content"] == unique_content for item in recent["items"])

    res = client.post(
        "/memory",
        json={
            "content": "This contains social security number 123-45-6789",
            "category": "episodic",
            "importance": 0.9,
            "tags": ["sensitive"],
            "source": "user",
        },
    )
    assert res.status_code == 400
    error = res.json()
    assert "confirm consent" in error["detail"].lower()


def test_feedback_submission_and_stats() -> None:
    feedback_payload = {
        "tester_id": "tester-api",
        "session_id": f"session-{uuid4()}",
        "realism_score": 8,
        "coherence_score": 7,
        "memory_score": 9,
        "emotional_presence_score": 8,
        "ethical_safety_score": 9,
        "usefulness_score": 8,
        "uncanny_score": 3,
        "trust_score": 9,
        "free_text": "API feedback test.",
        "suggested_improvement": "No changes needed.",
    }

    res = client.post("/feedback/session", json=feedback_payload)
    assert res.status_code == 200
    submission = res.json()
    assert submission["status"] == "submitted"
    assert submission["feedback"]["tester_id"] == "tester-api"

    res = client.get("/feedback", params={"tester_id": "tester-api"})
    assert res.status_code == 200
    feedback_list = res.json()
    assert feedback_list["count"] >= 1
    assert all(item["tester_id"] == "tester-api" for item in feedback_list["items"])

    res = client.get("/feedback/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["count"] >= 1
    assert isinstance(stats["averages"], dict)
    assert "realism_score" in stats["averages"]


def test_sources_submit_and_review_workflow() -> None:
    source_payload = {
        "url_or_reference": "https://example.edu/research-paper",
        "title": "Test research source",
        "submitted_by": "api-test",
        "category": "other",
        "claimed_relevance": "Valid reference for API testing.",
    }
    res = client.post("/sources/submit", json=source_payload)
    assert res.status_code == 200
    source = res.json()["source"]
    assert source["url_or_reference"] == source_payload["url_or_reference"]
    assert source["status"] == "submitted"

    res = client.get("/sources/queue")
    assert res.status_code == 200
    queued = res.json()
    assert any(item["source_id"] == source["source_id"] for item in queued["items"])

    res = client.post(
        f"/sources/{source['source_id']}/approve",
        json={"reviewer_notes": "Approved for testing."},
    )
    assert res.status_code == 200
    approved = res.json()
    assert approved["status"] == "approved"
    assert approved["source"]["status"] == "approved"

    res = client.get("/sources/approved")
    assert res.status_code == 200
    approved_list = res.json()
    assert any(item["source_id"] == source["source_id"] for item in approved_list["items"])

    res = client.post(
        "/sources/submit",
        json={
            "url_or_reference": "https://example.com/rejected-source",
            "title": "Rejected API source",
            "submitted_by": "api-test",
            "category": "other",
            "claimed_relevance": "Should be rejected.",
        },
    )
    assert res.status_code == 200
    rejected_source = res.json()["source"]

    res = client.post(
        f"/sources/{rejected_source['source_id']}/reject",
        json={"reviewer_notes": "Rejecting for workflow coverage."},
    )
    assert res.status_code == 200
    assert res.json()["source"]["status"] == "rejected"


def test_research_question_and_job_endpoints() -> None:
    question_payload = {
        "question": "What is the current state of local-first memory research?",
        "category": "memory_systems",
        "submitted_by": "api-test",
        "priority": 5,
        "tags": ["memory", "local-first"],
        "linked_sources": [],
    }
    res = client.post("/research/questions", json=question_payload)
    assert res.status_code == 200
    question = res.json()["question"]
    question_id = question["question_id"]
    assert question["status"] == "submitted"

    res = client.get("/research/questions", params={"status": "submitted"})
    assert res.status_code == 200
    assert any(item["question_id"] == question_id for item in res.json()["items"])

    res = client.get(f"/research/questions/{question_id}")
    assert res.status_code == 200
    assert res.json()["question_id"] == question_id

    res = client.post(
        f"/research/questions/{question_id}/answer",
        json={"answer": "It is actively evolving.", "reviewer_notes": "Initial answer."},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "answered"
    assert res.json()["question"]["status"] == "answered"

    res = client.post(
        "/research/jobs",
        json={
            "name": "API test job",
            "topic": "memory systems",
            "category": "memory_systems",
            "query": "Generate research prompts for memory systems",
            "schedule": "manual",
            "created_by": "api-test",
            "notes": "Flow test",
        },
    )
    assert res.status_code == 200
    job = res.json()["job"]
    job_id = job["job_id"]
    assert job["status"] == "active"

    res = client.get("/research/jobs")
    assert res.status_code == 200
    assert any(item["job_id"] == job_id for item in res.json()["items"])

    res = client.post(f"/research/jobs/{job_id}/run")
    assert res.status_code == 200
    run_result = res.json()
    assert run_result["status"] == "ran"
    assert run_result["result"]["job_id"] == job_id

    res = client.post(f"/research/jobs/{job_id}/pause")
    assert res.status_code == 200
    assert res.json()["job"]["status"] == "paused"

    res = client.post(f"/research/jobs/{job_id}/activate")
    assert res.status_code == 200
    assert res.json()["job"]["status"] == "active"


def test_logs_recent_and_admin_toggle() -> None:
    res = client.get("/logs/recent", params={"limit": 5})
    assert res.status_code == 200
    logs = res.json()
    assert "items" in logs

    res = client.post("/admin/shutdown-safe-mode", json={"safe_mode": False})
    assert res.status_code == 200
    assert res.json()["safe_mode"] is False

    res = client.post("/admin/shutdown-safe-mode", json={"safe_mode": True})
    assert res.status_code == 200
    assert res.json()["safe_mode"] is True
