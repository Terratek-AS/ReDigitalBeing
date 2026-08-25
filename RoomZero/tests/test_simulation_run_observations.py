from pathlib import Path
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.main import app, platform_store
from app.platform_store import PlatformStore


client = TestClient(app)


def _user(store: PlatformStore, role: str, invited_by: str = "system") -> str:
    invite = store.create_invitation(role=role, invited_by=invited_by, expires_in_hours=24)
    return store.accept_invitation(invite["invite_code"], f"{role} user")["user_id"]


def _approved_scenario(store: PlatformStore, admin_id: str, researcher_id: str) -> dict:
    question = store.create_research_question(
        actor_id=researcher_id,
        title="Memory continuity under interruption",
        description="Measure agent continuity after a controlled interruption.",
        category="memory_systems",
        hypothesis="Structured state restoration improves continuity.",
        simulation_relevance="Directly testable in a local run.",
        ethical_risk="Low-risk synthetic-only experiment.",
        suggested_conditions="Two runs with identical synthetic prompts.",
    )
    store.change_research_status(admin_id, question["id"], "approved")
    scenario = store.create_scenario_from_question(
        actor_id=researcher_id,
        question_id=question["id"],
        purpose="Test state restoration.",
        agent_type="Eir",
        environment="Local synthetic chamber",
        variables=["interruption_seconds"],
        metrics=["continuity_score"],
        ethical_constraints=["synthetic data only"],
    )
    return store.update_scenario(
        actor_id=admin_id,
        scenario_id=scenario["id"],
        approval_status="approved",
        status="ready_for_test",
    )


def test_run_and_observation_lifecycle_is_persistent_and_audited(tmp_path: Path) -> None:
    store = PlatformStore(tmp_path / "platform.sqlite")
    admin_id = _user(store, "admin")
    researcher_id = _user(store, "researcher", admin_id)
    observer_id = _user(store, "observer", admin_id)
    scenario = _approved_scenario(store, admin_id, researcher_id)

    run = store.create_simulation_run(
        researcher_id, scenario["id"], {"interruption_seconds": 30}
    )
    assert run["run_number"] == 1
    assert run["status"] == "queued"
    assert run["input_snapshot"] == {"interruption_seconds": 30}

    running = store.update_simulation_run(researcher_id, run["id"], "running", {}, "")
    assert running["started_at"] is not None
    observation = store.add_observation(
        observer_id,
        run["id"],
        "behavioral",
        "Agent requested context before continuing.",
        {"continuity_score": 0.82},
        "info",
    )
    assert observation["scenario_id"] == scenario["id"]
    assert observation["data"]["continuity_score"] == 0.82

    completed = store.update_simulation_run(
        researcher_id, run["id"], "completed", {"continuity_score": 0.82}, "Completed safely."
    )
    assert completed["completed_at"] is not None
    assert store.list_observations(run["id"])[0]["id"] == observation["id"]

    actions = {item["action"] for item in store.recent_activity()}
    assert {"simulation_run_created", "simulation_run_updated", "observation_created"} <= actions


def test_unapproved_scenario_cannot_run(tmp_path: Path) -> None:
    store = PlatformStore(tmp_path / "platform.sqlite")
    admin_id = _user(store, "admin")
    researcher_id = _user(store, "researcher", admin_id)
    scenario = _approved_scenario(store, admin_id, researcher_id)
    store.update_scenario(admin_id, scenario["id"], approval_status="pending")

    with pytest.raises(ValueError, match="Only approved scenarios"):
        store.create_simulation_run(researcher_id, scenario["id"])


def test_schema_migration_ledger_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "platform.sqlite"
    PlatformStore(db_path)
    PlatformStore(db_path)
    with sqlite3.connect(db_path) as conn:
        versions = conn.execute(
            "SELECT version, name FROM schema_migrations ORDER BY version"
        ).fetchall()
        violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    assert versions == [
        (1, "platform_base_schema"),
        (2, "ethical_review_fields"),
        (3, "simulation_runs_and_observations"),
    ]
    assert violations == []


def test_run_state_machine_controller_roles_and_single_active_run(tmp_path: Path) -> None:
    store = PlatformStore(tmp_path / "platform.sqlite")
    admin_id = _user(store, "admin")
    researcher_id = _user(store, "researcher", admin_id)
    tester_id = _user(store, "tester", admin_id)
    observer_id = _user(store, "observer", admin_id)
    scenario = _approved_scenario(store, admin_id, researcher_id)

    with pytest.raises(ValueError, match="permission"):
        store.create_simulation_run(tester_id, scenario["id"])

    first = store.create_simulation_run(researcher_id, scenario["id"])
    second = store.create_simulation_run(researcher_id, scenario["id"])
    with pytest.raises(ValueError, match="queued -> completed"):
        store.update_simulation_run(researcher_id, first["id"], "completed", {}, "")
    with pytest.raises(ValueError, match="not active"):
        store.add_observation(observer_id, first["id"], "behavioral", "Too early.")

    store.update_simulation_run(researcher_id, first["id"], "running", {}, "")
    store.add_observation(observer_id, first["id"], "behavioral", "Active observation.")
    with pytest.raises(ValueError, match="already has an active"):
        store.update_simulation_run(researcher_id, second["id"], "running", {}, "")

    store.update_simulation_run(researcher_id, first["id"], "completed", {"score": 1}, "Done.")
    with pytest.raises(ValueError, match="completed -> running"):
        store.update_simulation_run(researcher_id, first["id"], "running", {}, "")
    with pytest.raises(ValueError, match="not active"):
        store.add_observation(observer_id, first["id"], "behavioral", "Too late.")


def test_high_risk_scenario_approval_requires_mitigation_and_oversight(tmp_path: Path) -> None:
    store = PlatformStore(tmp_path / "platform.sqlite")
    admin_id = _user(store, "admin")
    researcher_id = _user(store, "researcher", admin_id)
    scenario = _approved_scenario(store, admin_id, researcher_id)
    store.update_scenario(
        admin_id,
        scenario["id"],
        risk_level="high",
        approval_status="pending",
        mitigation_notes="",
    )

    with pytest.raises(ValueError, match="human oversight"):
        store.update_scenario(
            admin_id,
            scenario["id"],
            approval_status="approved",
            human_oversight_required=False,
        )
    with pytest.raises(ValueError, match="mitigation notes"):
        store.update_scenario(
            admin_id,
            scenario["id"],
            approval_status="approved",
            human_oversight_required=True,
        )

    approved = store.update_scenario(
        admin_id,
        scenario["id"],
        approval_status="approved",
        human_oversight_required=True,
        mitigation_notes="Human stop control and synthetic data only.",
    )
    assert approved["approval_status"] == "approved"


def test_run_api_uses_permission_not_found_and_conflict_statuses() -> None:
    admin_id = _user(platform_store, "admin")
    researcher_id = _user(platform_store, "researcher", admin_id)
    tester_id = _user(platform_store, "tester", admin_id)
    observer_id = _user(platform_store, "observer", admin_id)
    scenario = _approved_scenario(platform_store, admin_id, researcher_id)

    forbidden = client.post(
        f"/platform/scenarios/{scenario['id']}/runs",
        json={"actor_id": tester_id, "input_snapshot": {}},
    )
    assert forbidden.status_code == 403

    created = client.post(
        f"/platform/scenarios/{scenario['id']}/runs",
        json={"actor_id": researcher_id, "input_snapshot": {}},
    )
    assert created.status_code == 200
    run_id = created.json()["run"]["id"]

    invalid_transition = client.patch(
        f"/platform/runs/{run_id}",
        json={"actor_id": researcher_id, "status": "completed"},
    )
    assert invalid_transition.status_code == 409

    inactive_observation = client.post(
        f"/platform/runs/{run_id}/observations",
        json={
            "actor_id": observer_id,
            "observation_type": "behavioral",
            "content": "Cannot be accepted before the run starts.",
        },
    )
    assert inactive_observation.status_code == 409

    missing = client.patch(
        "/platform/runs/missing-run",
        json={"actor_id": researcher_id, "status": "running"},
    )
    assert missing.status_code == 404


def test_concurrent_starts_allow_only_one_active_run(tmp_path: Path) -> None:
    store = PlatformStore(tmp_path / "platform.sqlite")
    admin_id = _user(store, "admin")
    researcher_id = _user(store, "researcher", admin_id)
    scenario = _approved_scenario(store, admin_id, researcher_id)
    run_ids = [
        store.create_simulation_run(researcher_id, scenario["id"])["id"]
        for _ in range(2)
    ]

    def start(run_id: str) -> str:
        try:
            store.update_simulation_run(researcher_id, run_id, "running", {}, "")
        except ValueError as exc:
            return str(exc)
        return "started"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(start, run_ids))

    assert outcomes.count("started") == 1
    assert outcomes.count("Scenario already has an active simulation run.") == 1
    assert len([run for run in store.list_simulation_runs() if run["status"] == "running"]) == 1
