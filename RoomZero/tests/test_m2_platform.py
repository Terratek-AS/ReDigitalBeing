from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")

from app.main import app, platform_store  # noqa: E402


client = TestClient(app)


def _seed_admin() -> str:
    users = platform_store.list_users()
    for u in users:
        if u["role"] == "admin" and int(u["active"]) == 1:
            return u["id"]

    invite = platform_store.create_invitation(role="admin", invited_by="system", expires_in_hours=24)
    created = platform_store.accept_invitation(
        invite_code=invite["invite_code"],
        display_name="Admin User",
        accepted_by="system",
    )
    return created["user_id"]


def _seed_researcher(admin_id: str) -> str:
    invite = platform_store.create_invitation(role="researcher", invited_by=admin_id, expires_in_hours=24)
    created = platform_store.accept_invitation(
        invite_code=invite["invite_code"],
        display_name="Research User",
        accepted_by=admin_id,
    )
    return created["user_id"]


def _seed_observer(admin_id: str) -> str:
    invite = platform_store.create_invitation(role="observer", invited_by=admin_id, expires_in_hours=24)
    created = platform_store.accept_invitation(
        invite_code=invite["invite_code"],
        display_name="Observer User",
        accepted_by=admin_id,
    )
    return created["user_id"]


def test_migration_bootstrap_and_db_file_exists() -> None:
    db_path = Path("RoomZero/data/platform/platform.sqlite")
    assert db_path.exists(), "Platform DB file should exist after app import/bootstrap."


def test_invitation_user_permission_and_audit_flow() -> None:
    admin_id = _seed_admin()

    res_create = client.post(
        "/platform/invitations",
        json={"actor_id": admin_id, "role": "tester", "expires_in_hours": 24},
    )
    assert res_create.status_code == 200, res_create.text
    invitation = res_create.json()["invitation"]
    assert invitation["invite_code"].startswith("RZ2-")

    res_accept = client.post(
        "/platform/invitations/accept",
        json={
            "invite_code": invitation["invite_code"],
            "display_name": "Tester Via API",
            "accepted_by": admin_id,
        },
    )
    assert res_accept.status_code == 200, res_accept.text
    user = res_accept.json()["user"]
    assert user["role"] == "tester"

    res_users = client.get("/platform/users", params={"actor_id": admin_id})
    assert res_users.status_code == 200
    assert any(u["id"] == user["user_id"] for u in res_users.json()["items"])

    res_audit = client.post("/platform/audit", json={"actor_id": admin_id})
    assert res_audit.status_code == 200
    actions = [a["action"] for a in res_audit.json()["items"]]
    assert "invite_created" in actions
    assert "invite_accepted" in actions
    assert "user_registered" in actions


def test_permission_denied_for_non_admin_listing_users() -> None:
    admin_id = _seed_admin()
    observer_id = _seed_observer(admin_id)

    res = client.get("/platform/users", params={"actor_id": observer_id})
    assert res.status_code == 403


def test_question_lifecycle_comment_status_and_conversion() -> None:
    admin_id = _seed_admin()
    researcher_id = _seed_researcher(admin_id)

    res_create_q = client.post(
        "/platform/research/questions",
        json={
            "actor_id": researcher_id,
            "title": "Memory retention under noisy prompts",
            "description": "Evaluate retention of key facts with distractors.",
            "category": "memory_systems",
            "hypothesis": "Structured prompts improve retention.",
            "simulation_relevance": "High for persistent-agent scenarios.",
            "ethical_risk": "Low",
            "suggested_conditions": "Use anonymized synthetic conversations.",
            "tags": ["memory", "retention"],
        },
    )
    assert res_create_q.status_code == 200, res_create_q.text
    question = res_create_q.json()["question"]
    question_id = question["id"]
    assert question["status"] == "proposed"

    res_comment = client.post(
        f"/platform/research/questions/{question_id}/comments",
        json={"actor_id": researcher_id, "comment": "Initial protocol draft added."},
    )
    assert res_comment.status_code == 200
    comment_id = res_comment.json()["comment"]["id"]

    res_comments = client.get(
        f"/platform/research/questions/{question_id}/comments",
        params={"actor_id": researcher_id},
    )
    assert res_comments.status_code == 200
    assert any(c["id"] == comment_id for c in res_comments.json()["items"])

    # conversion should fail before approval
    res_convert_fail = client.post(
        f"/platform/research/questions/{question_id}/convert-scenario",
        json={
            "actor_id": researcher_id,
            "purpose": "Run retention simulation.",
            "agent_type": "single-agent",
            "environment": "local",
            "variables": ["noise_level"],
            "metrics": ["recall_score"],
            "ethical_constraints": ["no sensitive data"],
        },
    )
    assert res_convert_fail.status_code == 400

    # approve and convert
    res_status = client.post(
        f"/platform/research/questions/{question_id}/status",
        json={"actor_id": admin_id, "status": "approved"},
    )
    assert res_status.status_code == 200
    assert res_status.json()["question"]["status"] == "approved"

    res_convert_ok = client.post(
        f"/platform/research/questions/{question_id}/convert-scenario",
        json={
            "actor_id": admin_id,
            "purpose": "Run retention simulation.",
            "agent_type": "single-agent",
            "environment": "local",
            "variables": ["noise_level"],
            "metrics": ["recall_score"],
            "ethical_constraints": ["no sensitive data"],
        },
    )
    assert res_convert_ok.status_code == 200, res_convert_ok.text
    scenario = res_convert_ok.json()["scenario"]
    assert scenario["research_question_id"] == question_id

    res_scenarios = client.get("/platform/scenarios", params={"actor_id": researcher_id})
    assert res_scenarios.status_code == 200
    assert any(s["id"] == scenario["id"] for s in res_scenarios.json()["items"])
