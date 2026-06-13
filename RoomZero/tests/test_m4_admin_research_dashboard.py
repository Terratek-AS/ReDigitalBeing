from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")

from app.db import init_db  # noqa: E402
from app.main import app, platform_store  # noqa: E402


client = TestClient(app)


M4_QUESTION_COLUMNS = {
    "risk_level",
    "possible_harm",
    "mitigation_notes",
    "human_oversight_required",
    "approval_status",
    "reviewer_notes",
    "priority",
    "reviewed_by",
    "reviewed_at",
}

M4_SCENARIO_COLUMNS = {
    "environment_conditions",
    "input_variables",
    "expected_observations",
    "metrics_to_collect",
    "result_summary",
    "status",
    "risk_level",
    "possible_harm",
    "mitigation_notes",
    "human_oversight_required",
    "approval_status",
    "reviewer_notes",
}


def _columns(db_path: Path, table_name: str) -> set[str]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
    finally:
        conn.close()


def _seed_admin() -> str:
    users = platform_store.list_users()
    for user in users:
        if user["role"] == "admin" and int(user["active"]) == 1:
            return user["id"]
    invite = platform_store.create_invitation(role="admin", invited_by="system", expires_in_hours=24)
    created = platform_store.accept_invitation(
        invite_code=invite["invite_code"],
        display_name="M4 Admin",
        accepted_by="system",
    )
    return created["user_id"]


def _seed_researcher(admin_id: str) -> str:
    invite = platform_store.create_invitation(role="researcher", invited_by=admin_id, expires_in_hours=24)
    created = platform_store.accept_invitation(
        invite_code=invite["invite_code"],
        display_name="M4 Researcher",
        accepted_by=admin_id,
    )
    return created["user_id"]


def _create_question(actor_id: str, suffix: str = "lifecycle", risk_level: str = "medium") -> dict:
    res = client.post(
        "/platform/research/questions",
        json={
            "actor_id": actor_id,
            "title": f"M4 question {suffix}",
            "description": "Evaluate a lifecycle-ready research question.",
            "category": "simulation",
            "hypothesis": "Structured review improves simulation readiness.",
            "simulation_relevance": "Directly supports scenario conversion.",
            "ethical_risk": "Review required before scenario execution.",
            "suggested_conditions": "Use synthetic inputs only.",
            "tags": ["m4", suffix],
            "risk_level": risk_level,
            "possible_harm": "Misclassification of risk.",
            "mitigation_notes": "Human review before execution.",
            "human_oversight_required": True,
            "approval_status": "needs_review",
            "priority": 6,
        },
    )
    assert res.status_code == 200, res.text
    return res.json()["question"]


def _audit_actions(actor_id: str) -> list[dict]:
    res = client.post("/platform/audit", json={"actor_id": actor_id})
    assert res.status_code == 200, res.text
    return res.json()["items"]


def test_m4_migrations_add_columns_and_are_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "platform.sqlite"
    init_db(db_path)
    init_db(db_path)

    assert M4_QUESTION_COLUMNS.issubset(_columns(db_path, "research_questions"))
    assert M4_SCENARIO_COLUMNS.issubset(_columns(db_path, "simulation_scenarios"))


def test_research_question_lifecycle_filters_review_actions_and_audit() -> None:
    admin_id = _seed_admin()
    researcher_id = _seed_researcher(admin_id)
    question = _create_question(researcher_id, "main", risk_level="medium")
    qid = question["id"]

    assert question["status"] == "proposed"
    assert question["risk_level"] == "medium"
    assert question["priority"] == 6
    assert question["human_oversight_required"] is True

    res_status = client.get(
        "/platform/research/questions",
        params={"actor_id": admin_id, "status": "proposed"},
    )
    assert res_status.status_code == 200
    assert any(item["id"] == qid for item in res_status.json()["items"])

    res_risk = client.get(
        "/platform/research/questions",
        params={"actor_id": admin_id, "risk_level": "medium"},
    )
    assert res_risk.status_code == 200
    assert any(item["id"] == qid for item in res_risk.json()["items"])

    res_review = client.patch(
        f"/platform/research/questions/{qid}/review",
        json={
            "actor_id": admin_id,
            "risk_level": "high",
            "possible_harm": "Potential emotional over-identification.",
            "mitigation_notes": "Keep operator present and stop conditions explicit.",
            "human_oversight_required": True,
            "approval_status": "needs_review",
            "reviewer_notes": "Needs a narrower simulation protocol.",
            "priority": 8,
        },
    )
    assert res_review.status_code == 200, res_review.text
    reviewed = res_review.json()["question"]
    assert reviewed["risk_level"] == "high"
    assert reviewed["approval_status"] == "needs_review"
    assert reviewed["reviewer_notes"] == "Needs a narrower simulation protocol."
    assert reviewed["priority"] == 8
    assert reviewed["reviewed_by"] == admin_id

    res_prioritize = client.post(
        f"/platform/research/questions/{qid}/prioritize",
        json={"actor_id": admin_id, "priority": 9, "reviewer_notes": "Top queue item."},
    )
    assert res_prioritize.status_code == 200
    assert res_prioritize.json()["question"]["priority"] == 9

    res_approve = client.post(
        f"/platform/research/questions/{qid}/approve",
        json={"actor_id": admin_id, "reviewer_notes": "Approved for scenario conversion."},
    )
    assert res_approve.status_code == 200
    assert res_approve.json()["question"]["status"] == "approved"
    assert res_approve.json()["question"]["approval_status"] == "approved"

    reject_question = _create_question(researcher_id, "reject", risk_level="low")
    res_reject = client.post(
        f"/platform/research/questions/{reject_question['id']}/reject",
        json={"actor_id": admin_id, "reviewer_notes": "Rejected for M4 test coverage."},
    )
    assert res_reject.status_code == 200
    assert res_reject.json()["question"]["status"] == "rejected"

    archive_question = _create_question(researcher_id, "archive", risk_level="critical")
    res_archive = client.post(
        f"/platform/research/questions/{archive_question['id']}/archive",
        json={"actor_id": admin_id, "reviewer_notes": "Archived after review."},
    )
    assert res_archive.status_code == 200
    assert res_archive.json()["question"]["status"] == "archived"

    actions = _audit_actions(admin_id)
    target_actions = [item["action"] for item in actions if item["target_id"] in {qid, reject_question["id"], archive_question["id"]}]
    assert "research_question_created" in [item["action"] for item in actions]
    assert "question_reviewer_notes_changed" in target_actions
    assert "question_prioritized" in target_actions
    assert "question_approved" in target_actions
    assert "question_rejected" in target_actions
    assert "question_archived" in target_actions


def test_research_question_invalid_values_are_rejected() -> None:
    admin_id = _seed_admin()
    researcher_id = _seed_researcher(admin_id)
    question = _create_question(researcher_id, "invalid-values", risk_level="low")

    res_invalid_status = client.post(
        f"/platform/research/questions/{question['id']}/status",
        json={"actor_id": admin_id, "status": "queued"},
    )
    assert res_invalid_status.status_code in {400, 422}

    res_invalid_risk = client.patch(
        f"/platform/research/questions/{question['id']}/review",
        json={"actor_id": admin_id, "risk_level": "severe"},
    )
    assert res_invalid_risk.status_code in {400, 422}

    res_invalid_priority = client.post(
        f"/platform/research/questions/{question['id']}/prioritize",
        json={"actor_id": admin_id, "priority": 11},
    )
    assert res_invalid_priority.status_code in {400, 422}


def test_scenario_conversion_m4_fields_filters_update_and_audit() -> None:
    admin_id = _seed_admin()
    researcher_id = _seed_researcher(admin_id)
    question = _create_question(researcher_id, "scenario", risk_level="medium")
    qid = question["id"]

    res_blocked = client.post(
        f"/platform/research/questions/{qid}/convert-scenario",
        json={
            "actor_id": admin_id,
            "purpose": "Blocked conversion.",
            "agent_type": "single-agent",
            "environment": "local",
        },
    )
    assert res_blocked.status_code == 400

    res_approve = client.post(
        f"/platform/research/questions/{qid}/approve",
        json={"actor_id": admin_id, "reviewer_notes": "Approved for conversion."},
    )
    assert res_approve.status_code == 200

    res_convert = client.post(
        f"/platform/research/questions/{qid}/convert-scenario",
        json={
            "actor_id": admin_id,
            "purpose": "Run a controlled simulation scenario.",
            "agent_type": "single-agent",
            "environment": "local lab",
            "variables": ["prompt_noise"],
            "metrics": ["recall_accuracy"],
            "ethical_constraints": ["human stop control"],
            "environment_conditions": "Quiet local test room.",
            "input_variables": ["prompt_noise", "memory_delay"],
            "expected_observations": ["agent asks for clarification"],
            "metrics_to_collect": ["recall_accuracy", "response_latency"],
            "result_summary": "Not run yet.",
            "status": "draft",
            "risk_level": "high",
            "possible_harm": "Over-trusting synthetic outputs.",
            "mitigation_notes": "Researcher review required before any conclusion.",
            "human_oversight_required": True,
            "approval_status": "pending",
            "reviewer_notes": "Scenario converted for review.",
        },
    )
    assert res_convert.status_code == 200, res_convert.text
    scenario = res_convert.json()["scenario"]
    assert scenario["research_question_id"] == qid
    assert scenario["expected_observations"] == ["agent asks for clarification"]
    assert scenario["metrics_to_collect"] == ["recall_accuracy", "response_latency"]
    assert scenario["result_summary"] == "Not run yet."
    assert scenario["status"] == "draft"
    assert scenario["risk_level"] == "high"
    assert scenario["human_oversight_required"] is True

    res_list = client.get(
        "/platform/scenarios",
        params={"actor_id": admin_id, "status": "draft", "risk_level": "high", "research_question_id": qid},
    )
    assert res_list.status_code == 200
    assert any(item["id"] == scenario["id"] for item in res_list.json()["items"])

    res_update = client.patch(
        f"/platform/scenarios/{scenario['id']}",
        json={
            "actor_id": admin_id,
            "status": "ready_for_test",
            "result_summary": "Ready for controlled dry run.",
            "approval_status": "needs_review",
        },
    )
    assert res_update.status_code == 200
    assert res_update.json()["scenario"]["status"] == "ready_for_test"
    assert res_update.json()["scenario"]["result_summary"] == "Ready for controlled dry run."

    actions = _audit_actions(admin_id)
    action_names = [item["action"] for item in actions]
    assert "question_converted_to_scenario" in action_names
    assert "scenario_updated" in action_names
