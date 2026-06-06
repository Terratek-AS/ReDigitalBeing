from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")

from app.main import app, platform_db_path
from app.db import get_connection

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


def test_simulation_events_endpoints_safe_projection_and_order() -> None:
    agent_id = f"rz-sim-api-{uuid4()}"
    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        ws.send_json(
            {
                "type": "observation",
                "event": "alpha_event",
                "payload": {"very_sensitive": "secret-a", "index": 1},
            }
        )
        ack1 = ws.receive_json()
        assert ack1["type"] == "ack"

        ws.send_json(
            {
                "type": "observation",
                "event": "beta_event",
                "payload": {"very_sensitive": "secret-b", "index": 2},
            }
        )
        ack2 = ws.receive_json()
        assert ack2["type"] == "ack"

    list_res = client.get("/simulation/events", params={"limit": 10})
    assert list_res.status_code == 200
    list_body = list_res.json()
    assert isinstance(list_body["count"], int)
    assert isinstance(list_body["items"], list)
    assert len(list_body["items"]) >= 2

    matching_items = [i for i in list_body["items"] if i.get("agent_id") == agent_id]
    assert len(matching_items) >= 2

    latest = matching_items[0]
    previous = matching_items[1]
    assert latest["event_type"] == "unreal.observation.beta_event"
    assert previous["event_type"] == "unreal.observation.alpha_event"

    required_keys = {
        "event_id",
        "created_at",
        "source",
        "event_type",
        "agent_id",
        "status",
        "severity",
        "protocol_version",
        "transport",
        "schema_version",
        "payload_summary",
        "risk_summary",
    }
    assert required_keys.issubset(set(latest.keys()))
    assert "payload" not in latest
    assert "secret-b" not in str(latest)

    event_id = latest["event_id"]
    single_res = client.get(f"/simulation/events/{event_id}")
    assert single_res.status_code == 200
    single = single_res.json()
    assert single["event_id"] == event_id
    assert single["event_type"] == "unreal.observation.beta_event"
    assert "payload" not in single
    assert "secret-b" not in str(single)

    trace_res = client.get(f"/simulation/events/{event_id}/traces")
    assert trace_res.status_code == 200
    trace_body = trace_res.json()
    assert trace_body["count"] == 1
    assert len(trace_body["items"]) == 1
    trace_item = trace_body["items"][0]
    assert trace_item["event_id"] == event_id
    assert "payload_summary" in trace_item
    assert trace_item["payload_summary"]["size"] == 2
    assert "payload" not in trace_item
    assert "secret-b" not in str(trace_item)

    missing_res = client.get(f"/simulation/events/{uuid4()}")
    assert missing_res.status_code == 404
    assert "Simulation event not found" in missing_res.json()["detail"]

    missing_trace_res = client.get(f"/simulation/events/{uuid4()}/traces")
    assert missing_trace_res.status_code == 404
    assert "Simulation event not found" in missing_trace_res.json()["detail"]


def test_simulation_events_filters_limit_and_summary() -> None:
    agent_a = f"rz-filter-a-{uuid4()}"
    agent_b = f"rz-filter-b-{uuid4()}"

    with client.websocket_connect(f"/ws/unreal/{agent_a}") as ws_a:
        _ = ws_a.receive_json()
        _ = ws_a.receive_json()
        ws_a.send_json(
            {
                "type": "observation",
                "event": "gamma_event",
                "payload": {"p": 1},
            }
        )
        _ = ws_a.receive_json()

    with client.websocket_connect(f"/ws/unreal/{agent_b}") as ws_b:
        _ = ws_b.receive_json()
        _ = ws_b.receive_json()
        ws_b.send_json(
            {
                "type": "observation",
                "event": "delta_event",
                "payload": {"p": 2},
            }
        )
        _ = ws_b.receive_json()

    all_res = client.get("/simulation/events")
    assert all_res.status_code == 200
    all_items = all_res.json()["items"]

    source_res = client.get("/simulation/events", params={"source": "unreal.websocket"})
    assert source_res.status_code == 200
    assert source_res.json()["count"] >= 2
    assert all(item["source"] == "unreal.websocket" for item in source_res.json()["items"])

    type_res = client.get("/simulation/events", params={"event_type": "unreal.observation.gamma_event"})
    assert type_res.status_code == 200
    assert type_res.json()["count"] >= 1
    assert all(item["event_type"] == "unreal.observation.gamma_event" for item in type_res.json()["items"])

    agent_res = client.get("/simulation/events", params={"agent_id": agent_a})
    assert agent_res.status_code == 200
    assert agent_res.json()["count"] >= 1
    assert all(item["agent_id"] == agent_a for item in agent_res.json()["items"])

    status_res = client.get("/simulation/events", params={"status": "accepted"})
    assert status_res.status_code == 200
    assert status_res.json()["count"] >= 2
    assert all(item["status"] == "accepted" for item in status_res.json()["items"])

    severity_res = client.get("/simulation/events", params={"severity": "info"})
    assert severity_res.status_code == 200
    assert severity_res.json()["count"] >= 2
    assert all(item["severity"] == "info" for item in severity_res.json()["items"])

    limited_res = client.get("/simulation/events", params={"limit": 1, "source": "unreal.websocket"})
    assert limited_res.status_code == 200
    assert len(limited_res.json()["items"]) == 1
    assert limited_res.json()["count"] >= 2

    invalid_limit_res = client.get("/simulation/events", params={"limit": 0})
    assert invalid_limit_res.status_code == 400
    assert "limit must be >= 1" in invalid_limit_res.json()["detail"]

    summary_res = client.get("/simulation/events/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["total_events"] >= 2
    assert summary["by_source"].get("unreal.websocket", 0) >= 2
    assert summary["by_event_type"].get("unreal.observation.gamma_event", 0) >= 1
    assert summary["by_status"].get("accepted", 0) >= 2
    assert summary["by_severity"].get("info", 0) >= 2

    filtered_summary_res = client.get("/simulation/events/summary", params={"agent_id": agent_a})
    assert filtered_summary_res.status_code == 200
    filtered_summary = filtered_summary_res.json()
    assert filtered_summary["total_events"] >= 1
    assert filtered_summary["by_event_type"].get("unreal.observation.gamma_event", 0) >= 1

    if all_items:
        assert "payload" not in all_items[0]


def test_simulation_event_review_notes_workflow_and_audit() -> None:
    agent_id = f"rz-review-note-{uuid4()}"
    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()
        ws.send_json(
            {
                "type": "observation",
                "event": "review_target",
                "payload": {"very_sensitive": "do-not-leak", "index": 99},
            }
        )
        ack = ws.receive_json()
        assert ack["type"] == "ack"

    list_res = client.get("/simulation/events", params={"agent_id": agent_id, "limit": 1})
    assert list_res.status_code == 200
    event_item = list_res.json()["items"][0]
    event_id = event_item["event_id"]

    get_empty = client.get(f"/simulation/events/{event_id}/review-notes")
    assert get_empty.status_code == 200
    assert get_empty.json()["count"] == 0
    assert get_empty.json()["items"] == []

    note_text = "Initial reviewer note for simulation event."
    create_res = client.post(
        f"/simulation/events/{event_id}/review-notes",
        json={"note_text": note_text, "reviewer_id": "reviewer-api", "status": "active"},
    )
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["status"] == "created"
    assert created["note"]["event_id"] == event_id
    assert created["note"]["note_text"] == note_text
    assert created["note"]["reviewer_id"] == "reviewer-api"
    assert "do-not-leak" not in str(created)

    get_notes = client.get(f"/simulation/events/{event_id}/review-notes")
    assert get_notes.status_code == 200
    notes_body = get_notes.json()
    assert notes_body["count"] >= 1
    first_note = notes_body["items"][0]
    assert first_note["event_id"] == event_id
    assert first_note["note_text"] == note_text
    assert "do-not-leak" not in str(first_note)

    with get_connection(Path(platform_db_path)) as conn:
        row = conn.execute(
            """
            SELECT actor_id, action, target_type, target_id, details
            FROM audit_logs
            WHERE action = 'simulation_event_review_note_created' AND target_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (event_id,),
        ).fetchone()
    assert row is not None
    assert row["actor_id"] == "reviewer-api"
    assert row["target_type"] == "simulation_event"
    assert row["target_id"] == event_id
    details = str(row["details"])
    assert "note_length" in details
    assert "do-not-leak" not in details


def test_simulation_event_review_notes_lifecycle_and_review_audit() -> None:
    agent_id = f"rz-review-note-lifecycle-{uuid4()}"
    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()
        ws.send_json(
            {
                "type": "observation",
                "event": "review_lifecycle_target",
                "payload": {"very_sensitive": "must-not-leak", "index": 7},
            }
        )
        _ = ws.receive_json()

    event_id = client.get("/simulation/events", params={"agent_id": agent_id, "limit": 1}).json()["items"][0]["event_id"]

    create_res = client.post(
        f"/simulation/events/{event_id}/review-notes",
        json={"note_text": "Lifecycle note", "reviewer_id": "reviewer-lifecycle", "status": "active"},
    )
    assert create_res.status_code == 200
    note = create_res.json()["note"]
    note_id = note["id"]
    assert note["status"] == "active"

    patch_resolved = client.patch(
        f"/simulation/events/{event_id}/review-notes/{note_id}",
        json={"status": "resolved"},
    )
    assert patch_resolved.status_code == 200
    assert patch_resolved.json()["note"]["status"] == "resolved"

    patch_flagged = client.patch(
        f"/simulation/events/{event_id}/review-notes/{note_id}",
        json={"status": "flagged"},
    )
    assert patch_flagged.status_code == 200
    assert patch_flagged.json()["note"]["status"] == "flagged"

    patch_archived = client.patch(
        f"/simulation/events/{event_id}/review-notes/{note_id}",
        json={"status": "archived"},
    )
    assert patch_archived.status_code == 200
    assert patch_archived.json()["note"]["status"] == "archived"

    patch_text = client.patch(
        f"/simulation/events/{event_id}/review-notes/{note_id}",
        json={"note_text": "Updated lifecycle note"},
    )
    assert patch_text.status_code == 200
    assert patch_text.json()["note"]["note_text"] == "Updated lifecycle note"

    invalid_status = client.patch(
        f"/simulation/events/{event_id}/review-notes/{note_id}",
        json={"status": "invalid"},
    )
    assert invalid_status.status_code == 400
    assert "Invalid review note status" in invalid_status.json()["detail"]

    empty_text = client.patch(
        f"/simulation/events/{event_id}/review-notes/{note_id}",
        json={"note_text": "   "},
    )
    assert empty_text.status_code == 400
    assert "cannot be empty" in empty_text.json()["detail"].lower()

    missing_event = client.patch(
        f"/simulation/events/{uuid4()}/review-notes/{note_id}",
        json={"status": "resolved"},
    )
    assert missing_event.status_code == 404

    missing_note = client.patch(
        f"/simulation/events/{event_id}/review-notes/{uuid4()}",
        json={"status": "resolved"},
    )
    assert missing_note.status_code == 404

    other_agent_id = f"rz-review-note-lifecycle-other-{uuid4()}"
    with client.websocket_connect(f"/ws/unreal/{other_agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()
        ws.send_json({"type": "observation", "event": "other_target", "payload": {"k": 1}})
        _ = ws.receive_json()
    other_event_id = client.get("/simulation/events", params={"agent_id": other_agent_id, "limit": 1}).json()["items"][0]["event_id"]

    wrong_event = client.patch(
        f"/simulation/events/{other_event_id}/review-notes/{note_id}",
        json={"status": "resolved"},
    )
    assert wrong_event.status_code == 404

    audit_default = client.get(f"/simulation/events/{event_id}/review-audit")
    assert audit_default.status_code == 200
    audit_items = audit_default.json()["items"]
    assert len(audit_items) >= 1
    assert all("action" in item and "created_at" in item and "target_id" in item and "details" in item for item in audit_items)
    assert all(item["target_id"] == event_id for item in audit_items)
    assert all("must-not-leak" not in str(item) for item in audit_items)

    actions = {item["action"] for item in audit_items}
    assert "simulation_event_review_note_status_changed" in actions
    assert "simulation_event_review_note_archived" in actions
    assert "simulation_event_review_note_updated" in actions

    audit_limit = client.get(f"/simulation/events/{event_id}/review-audit", params={"limit": 1})
    assert audit_limit.status_code == 200
    assert audit_limit.json()["count"] <= 1

    audit_invalid_limit = client.get(f"/simulation/events/{event_id}/review-audit", params={"limit": 0})
    assert audit_invalid_limit.status_code == 400

    audit_missing_event = client.get(f"/simulation/events/{uuid4()}/review-audit")
    assert audit_missing_event.status_code == 404


def test_simulation_event_review_notes_validation_and_not_found() -> None:
    missing_event_id = str(uuid4())

    get_missing = client.get(f"/simulation/events/{missing_event_id}/review-notes")
    assert get_missing.status_code == 404
    assert "Simulation event not found" in get_missing.json()["detail"]

    post_missing = client.post(
        f"/simulation/events/{missing_event_id}/review-notes",
        json={"note_text": "will fail"},
    )
    assert post_missing.status_code == 404
    assert "Simulation event not found" in post_missing.json()["detail"]

    agent_id = f"rz-review-note-validation-{uuid4()}"
    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()
        ws.send_json({"type": "observation", "event": "validation_target", "payload": {"a": 1}})
        _ = ws.receive_json()

    event_id = client.get("/simulation/events", params={"agent_id": agent_id, "limit": 1}).json()["items"][0]["event_id"]

    empty_note_res = client.post(
        f"/simulation/events/{event_id}/review-notes",
        json={"note_text": "   "},
    )
    assert empty_note_res.status_code == 400
    assert "cannot be empty" in empty_note_res.json()["detail"].lower()

    too_long_note = "x" * 2001
    too_long_res = client.post(
        f"/simulation/events/{event_id}/review-notes",
        json={"note_text": too_long_note},
    )
    assert too_long_res.status_code == 422 or too_long_res.status_code == 400


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
