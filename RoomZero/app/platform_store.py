from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from app.db import get_connection, init_db, json_dumps, json_loads


VALID_ROLES = {"observer", "tester", "researcher", "reviewer", "admin", "contributor"}
VALID_STATUSES = {"proposed", "approved", "rejected", "testing", "completed", "archived"}
VALID_RISK_LEVELS = {"low", "medium", "high", "critical"}
VALID_APPROVAL_STATUSES = {"pending", "approved", "rejected", "needs_review"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class PlatformStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        init_db(self.db_path)

    def _audit(
        self,
        actor_id: str,
        action: str,
        target_type: str,
        target_id: str,
        details: dict | None = None,
    ) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (id, actor_id, action, target_type, target_id, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    actor_id,
                    action,
                    target_type,
                    target_id,
                    json_dumps(details or {}),
                    utc_now_iso(),
                ),
            )

    def create_invitation(self, role: str, invited_by: str, expires_in_hours: int = 72) -> dict:
        if role not in VALID_ROLES:
            raise ValueError("Invalid role.")
        alphabet = string.ascii_uppercase + string.digits
        invite_code = "RZ2-" + "".join(secrets.choice(alphabet) for _ in range(10))
        invite_id = str(uuid4())
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)).isoformat()
        now = utc_now_iso()

        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO invitations (id, invite_code, role, invited_by, expires_at, active, created_at)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                """,
                (invite_id, invite_code, role, invited_by, expires_at, now),
            )

        self._audit(
            actor_id=invited_by,
            action="invite_created",
            target_type="invitation",
            target_id=invite_id,
            details={"role": role, "invite_code": invite_code, "expires_at": expires_at},
        )
        return {
            "id": invite_id,
            "invite_code": invite_code,
            "role": role,
            "invited_by": invited_by,
            "expires_at": expires_at,
            "active": True,
            "created_at": now,
        }

    def list_invitations(self) -> list[dict]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, invite_code, role, invited_by, expires_at, accepted_by, accepted_at, active, created_at FROM invitations ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def accept_invitation(self, invite_code: str, display_name: str, accepted_by: str | None = None) -> dict:
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat()

        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM invitations WHERE invite_code = ?",
                (invite_code,),
            ).fetchone()
            if row is None:
                raise ValueError("Invite code not found.")

            if int(row["active"]) != 1:
                raise ValueError("Invite is inactive.")

            expires_at = row["expires_at"]
            if expires_at:
                exp_dt = datetime.fromisoformat(expires_at)
                if now_dt > exp_dt:
                    conn.execute("UPDATE invitations SET active = 0 WHERE id = ?", (row["id"],))
                    self._audit(
                        actor_id=accepted_by or "system",
                        action="invite_expired",
                        target_type="invitation",
                        target_id=row["id"],
                        details={"invite_code": invite_code},
                    )
                    raise ValueError("Invite code has expired.")

            user_id = str(uuid4())
            user_actor = accepted_by or f"user:{user_id}"
            conn.execute(
                """
                INSERT INTO users (id, display_name, role, invited_by, invite_code, active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    user_id,
                    display_name,
                    row["role"],
                    row["invited_by"],
                    row["invite_code"],
                    now,
                    now,
                ),
            )
            conn.execute(
                "UPDATE invitations SET active = 0, accepted_by = ?, accepted_at = ? WHERE id = ?",
                (user_id, now, row["id"]),
            )

        self._audit(
            actor_id=user_actor,
            action="invite_accepted",
            target_type="invitation",
            target_id=row["id"],
            details={"invite_code": invite_code, "new_user_id": user_id},
        )
        self._audit(
            actor_id=user_actor,
            action="user_registered",
            target_type="user",
            target_id=user_id,
            details={"role": row["role"], "display_name": display_name},
        )
        return {
            "user_id": user_id,
            "display_name": display_name,
            "role": row["role"],
            "invited_by": row["invited_by"],
            "invite_code": row["invite_code"],
            "created_at": now,
        }

    def list_users(self) -> list[dict]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, display_name, role, invited_by, invite_code, active, created_at, updated_at FROM users ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def get_user(self, user_id: str) -> dict | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT id, display_name, role, invited_by, invite_code, active, created_at, updated_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return dict(row) if row else None

    def require_role(self, user_id: str, allowed_roles: set[str]) -> dict:
        user = self.get_user(user_id)
        if user is None or int(user["active"]) != 1:
            raise ValueError("User not found or inactive.")
        role = user["role"]
        if role not in allowed_roles:
            raise ValueError("User role does not have permission.")
        return user

    def create_research_question(
        self,
        actor_id: str,
        title: str,
        description: str,
        category: str,
        hypothesis: str,
        simulation_relevance: str,
        ethical_risk: str,
        suggested_conditions: str,
        tags: list[str] | None = None,
        risk_level: str = "low",
        possible_harm: str = "",
        mitigation_notes: str = "",
        human_oversight_required: bool = True,
        approval_status: str = "pending",
        priority: int = 5,
    ) -> dict:
        self.require_role(actor_id, {"admin", "researcher", "tester", "contributor"})
        self._validate_risk_level(risk_level)
        self._validate_approval_status(approval_status)
        self._validate_priority(priority)
        qid = str(uuid4())
        now = utc_now_iso()
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO research_questions
                (
                    id, title, description, category, hypothesis, simulation_relevance,
                    ethical_risk, suggested_conditions, status, author, created_at,
                    updated_at, tags, risk_level, possible_harm, mitigation_notes,
                    human_oversight_required, approval_status, priority
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    qid,
                    title,
                    description,
                    category,
                    hypothesis,
                    simulation_relevance,
                    ethical_risk,
                    suggested_conditions,
                    "proposed",
                    actor_id,
                    now,
                    now,
                    json_dumps(tags or []),
                    risk_level,
                    possible_harm,
                    mitigation_notes,
                    1 if human_oversight_required else 0,
                    approval_status,
                    priority,
                ),
            )
        self._audit(actor_id, "question_created", "research_question", qid, {"status": "proposed"})
        self._audit(actor_id, "research_question_created", "research_question", qid, {"status": "proposed"})
        return self.get_research_question(qid)  # type: ignore[return-value]

    def _normalize_question(self, row: dict) -> dict:
        row["tags"] = json_loads(row.get("tags", "[]"))
        row["human_oversight_required"] = bool(row.get("human_oversight_required", 1))
        return row

    def _normalize_scenario(self, row: dict) -> dict:
        row["variables"] = json_loads(row.get("variables", "[]"))
        row["metrics"] = json_loads(row.get("metrics", "[]"))
        row["ethical_constraints"] = json_loads(row.get("ethical_constraints", "[]"))
        row["input_variables"] = json_loads(row.get("input_variables", "[]"))
        row["expected_observations"] = json_loads(row.get("expected_observations", "[]"))
        row["metrics_to_collect"] = json_loads(row.get("metrics_to_collect", "[]"))
        row["human_oversight_required"] = bool(row.get("human_oversight_required", 1))
        return row

    def _validate_priority(self, priority: int) -> None:
        if priority < 1 or priority > 10:
            raise ValueError("Invalid priority.")

    def _validate_risk_level(self, risk_level: str) -> None:
        if risk_level not in VALID_RISK_LEVELS:
            raise ValueError("Invalid risk level.")

    def _validate_approval_status(self, approval_status: str) -> None:
        if approval_status not in VALID_APPROVAL_STATUSES:
            raise ValueError("Invalid approval status.")

    def get_research_question(self, question_id: str) -> dict | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM research_questions WHERE id = ?", (question_id,)).fetchone()
        if not row:
            return None
        return self._normalize_question(dict(row))

    def list_research_questions(
        self,
        status: str | None = None,
        risk_level: str | None = None,
        author: str | None = None,
        priority_min: int | None = None,
    ) -> list[dict]:
        clauses = []
        params: list[object] = []
        if status is not None:
            if status not in VALID_STATUSES:
                raise ValueError("Invalid status.")
            clauses.append("status = ?")
            params.append(status)
        if risk_level is not None:
            self._validate_risk_level(risk_level)
            clauses.append("risk_level = ?")
            params.append(risk_level)
        if author is not None:
            clauses.append("author = ?")
            params.append(author)
        if priority_min is not None:
            self._validate_priority(priority_min)
            clauses.append("priority >= ?")
            params.append(priority_min)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                f"SELECT * FROM research_questions{where} ORDER BY created_at DESC",
                params,
            ).fetchall()
        return [self._normalize_question(dict(r)) for r in rows]

    def update_research_question(
        self,
        actor_id: str,
        question_id: str,
        title: str | None = None,
        description: str | None = None,
        hypothesis: str | None = None,
        simulation_relevance: str | None = None,
        ethical_risk: str | None = None,
        suggested_conditions: str | None = None,
        tags: list[str] | None = None,
        risk_level: str | None = None,
        possible_harm: str | None = None,
        mitigation_notes: str | None = None,
        human_oversight_required: bool | None = None,
        approval_status: str | None = None,
        reviewer_notes: str | None = None,
        priority: int | None = None,
    ) -> dict:
        question = self.get_research_question(question_id)
        if question is None:
            raise ValueError("Research question not found.")
        user = self.require_role(actor_id, {"admin", "researcher", "tester", "contributor"})
        if user["role"] != "admin" and question["author"] != actor_id:
            raise ValueError("Only author or admin can edit this question.")
        if risk_level is not None:
            self._validate_risk_level(risk_level)
        if approval_status is not None:
            self._validate_approval_status(approval_status)
        if priority is not None:
            self._validate_priority(priority)

        updated = {
            "title": title if title is not None else question["title"],
            "description": description if description is not None else question["description"],
            "hypothesis": hypothesis if hypothesis is not None else question["hypothesis"],
            "simulation_relevance": simulation_relevance if simulation_relevance is not None else question["simulation_relevance"],
            "ethical_risk": ethical_risk if ethical_risk is not None else question["ethical_risk"],
            "suggested_conditions": suggested_conditions if suggested_conditions is not None else question["suggested_conditions"],
            "tags": tags if tags is not None else question["tags"],
            "risk_level": risk_level if risk_level is not None else question["risk_level"],
            "possible_harm": possible_harm if possible_harm is not None else question["possible_harm"],
            "mitigation_notes": mitigation_notes if mitigation_notes is not None else question["mitigation_notes"],
            "human_oversight_required": (
                human_oversight_required
                if human_oversight_required is not None
                else question["human_oversight_required"]
            ),
            "approval_status": approval_status if approval_status is not None else question["approval_status"],
            "reviewer_notes": reviewer_notes if reviewer_notes is not None else question["reviewer_notes"],
            "priority": priority if priority is not None else question["priority"],
            "updated_at": utc_now_iso(),
        }

        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                UPDATE research_questions
                SET title = ?, description = ?, hypothesis = ?, simulation_relevance = ?,
                    ethical_risk = ?, suggested_conditions = ?, tags = ?, risk_level = ?,
                    possible_harm = ?, mitigation_notes = ?, human_oversight_required = ?,
                    approval_status = ?, reviewer_notes = ?, priority = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    updated["title"],
                    updated["description"],
                    updated["hypothesis"],
                    updated["simulation_relevance"],
                    updated["ethical_risk"],
                    updated["suggested_conditions"],
                    json_dumps(updated["tags"]),
                    updated["risk_level"],
                    updated["possible_harm"],
                    updated["mitigation_notes"],
                    1 if updated["human_oversight_required"] else 0,
                    updated["approval_status"],
                    updated["reviewer_notes"],
                    updated["priority"],
                    updated["updated_at"],
                    question_id,
                ),
            )
        self._audit(actor_id, "question_edited", "research_question", question_id, {"updated_fields": list(updated.keys())})
        return self.get_research_question(question_id)  # type: ignore[return-value]

    def change_research_status(self, actor_id: str, question_id: str, status: str) -> dict:
        if status not in VALID_STATUSES:
            raise ValueError("Invalid status.")
        self.require_role(actor_id, {"admin", "reviewer", "researcher"})
        question = self.get_research_question(question_id)
        if question is None:
            raise ValueError("Research question not found.")

        with get_connection(self.db_path) as conn:
            conn.execute(
                "UPDATE research_questions SET status = ?, updated_at = ? WHERE id = ?",
                (status, utc_now_iso(), question_id),
            )
        self._audit(actor_id, "question_status_changed", "research_question", question_id, {"status": status})
        return self.get_research_question(question_id)  # type: ignore[return-value]

    def review_research_question(
        self,
        actor_id: str,
        question_id: str,
        risk_level: str | None = None,
        possible_harm: str | None = None,
        mitigation_notes: str | None = None,
        human_oversight_required: bool | None = None,
        approval_status: str | None = None,
        reviewer_notes: str | None = None,
        priority: int | None = None,
    ) -> dict:
        self.require_role(actor_id, {"admin", "reviewer", "researcher"})
        question = self.get_research_question(question_id)
        if question is None:
            raise ValueError("Research question not found.")
        if risk_level is not None:
            self._validate_risk_level(risk_level)
        if approval_status is not None:
            self._validate_approval_status(approval_status)
        if priority is not None:
            self._validate_priority(priority)

        next_values = {
            "risk_level": risk_level if risk_level is not None else question["risk_level"],
            "possible_harm": possible_harm if possible_harm is not None else question["possible_harm"],
            "mitigation_notes": mitigation_notes if mitigation_notes is not None else question["mitigation_notes"],
            "human_oversight_required": (
                human_oversight_required
                if human_oversight_required is not None
                else question["human_oversight_required"]
            ),
            "approval_status": approval_status if approval_status is not None else question["approval_status"],
            "reviewer_notes": reviewer_notes if reviewer_notes is not None else question["reviewer_notes"],
            "priority": priority if priority is not None else question["priority"],
            "reviewed_at": utc_now_iso(),
        }

        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                UPDATE research_questions
                SET risk_level = ?, possible_harm = ?, mitigation_notes = ?,
                    human_oversight_required = ?, approval_status = ?, reviewer_notes = ?,
                    priority = ?, reviewed_by = ?, reviewed_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    next_values["risk_level"],
                    next_values["possible_harm"],
                    next_values["mitigation_notes"],
                    1 if next_values["human_oversight_required"] else 0,
                    next_values["approval_status"],
                    next_values["reviewer_notes"],
                    next_values["priority"],
                    actor_id,
                    next_values["reviewed_at"],
                    next_values["reviewed_at"],
                    question_id,
                ),
            )

        if reviewer_notes is not None and reviewer_notes != question.get("reviewer_notes"):
            self._audit(
                actor_id,
                "question_reviewer_notes_changed",
                "research_question",
                question_id,
                {"reviewed_by": actor_id},
            )
        if priority is not None and priority != question.get("priority"):
            self._audit(actor_id, "question_prioritized", "research_question", question_id, {"priority": priority})
        return self.get_research_question(question_id)  # type: ignore[return-value]

    def _set_question_status(
        self,
        actor_id: str,
        question_id: str,
        status: str,
        action: str,
        approval_status: str | None = None,
        reviewer_notes: str | None = None,
    ) -> dict:
        if status not in VALID_STATUSES:
            raise ValueError("Invalid status.")
        if approval_status is not None:
            self._validate_approval_status(approval_status)
        self.require_role(actor_id, {"admin", "reviewer", "researcher"})
        question = self.get_research_question(question_id)
        if question is None:
            raise ValueError("Research question not found.")
        now = utc_now_iso()
        next_approval = approval_status if approval_status is not None else question["approval_status"]
        next_notes = reviewer_notes if reviewer_notes is not None else question["reviewer_notes"]

        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                UPDATE research_questions
                SET status = ?, approval_status = ?, reviewer_notes = ?, reviewed_by = ?,
                    reviewed_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, next_approval, next_notes, actor_id, now, now, question_id),
            )
        self._audit(actor_id, action, "research_question", question_id, {"status": status})
        if reviewer_notes is not None and reviewer_notes != question.get("reviewer_notes"):
            self._audit(actor_id, "question_reviewer_notes_changed", "research_question", question_id, {})
        return self.get_research_question(question_id)  # type: ignore[return-value]

    def approve_research_question_m4(self, actor_id: str, question_id: str, reviewer_notes: str | None = None) -> dict:
        return self._set_question_status(actor_id, question_id, "approved", "question_approved", "approved", reviewer_notes)

    def reject_research_question_m4(self, actor_id: str, question_id: str, reviewer_notes: str | None = None) -> dict:
        return self._set_question_status(actor_id, question_id, "rejected", "question_rejected", "rejected", reviewer_notes)

    def archive_research_question(self, actor_id: str, question_id: str, reviewer_notes: str | None = None) -> dict:
        return self._set_question_status(actor_id, question_id, "archived", "question_archived", None, reviewer_notes)

    def prioritize_research_question(
        self,
        actor_id: str,
        question_id: str,
        priority: int,
        reviewer_notes: str | None = None,
    ) -> dict:
        self.require_role(actor_id, {"admin", "reviewer", "researcher"})
        self._validate_priority(priority)
        question = self.get_research_question(question_id)
        if question is None:
            raise ValueError("Research question not found.")
        now = utc_now_iso()
        next_notes = reviewer_notes if reviewer_notes is not None else question["reviewer_notes"]
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                UPDATE research_questions
                SET priority = ?, reviewer_notes = ?, reviewed_by = ?, reviewed_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (priority, next_notes, actor_id, now, now, question_id),
            )
        self._audit(actor_id, "question_prioritized", "research_question", question_id, {"priority": priority})
        if reviewer_notes is not None and reviewer_notes != question.get("reviewer_notes"):
            self._audit(actor_id, "question_reviewer_notes_changed", "research_question", question_id, {})
        return self.get_research_question(question_id)  # type: ignore[return-value]

    def add_comment(self, actor_id: str, question_id: str, comment: str) -> dict:
        self.require_role(actor_id, {"admin", "reviewer", "researcher", "tester", "contributor", "observer"})
        if self.get_research_question(question_id) is None:
            raise ValueError("Research question not found.")
        cid = str(uuid4())
        now = utc_now_iso()
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO research_comments (id, question_id, author, comment, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (cid, question_id, actor_id, comment, now, now),
            )
        self._audit(actor_id, "question_commented", "research_question", question_id, {"comment_id": cid})
        return {
            "id": cid,
            "question_id": question_id,
            "author": actor_id,
            "comment": comment,
            "created_at": now,
            "updated_at": now,
        }

    def list_comments(self, question_id: str) -> list[dict]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, question_id, author, comment, created_at, updated_at FROM research_comments WHERE question_id = ? ORDER BY created_at ASC",
                (question_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def create_scenario_from_question(
        self,
        actor_id: str,
        question_id: str,
        purpose: str,
        agent_type: str,
        environment: str,
        variables: list[str],
        metrics: list[str],
        ethical_constraints: list[str],
        environment_conditions: str = "",
        input_variables: list[str] | None = None,
        expected_observations: list[str] | None = None,
        metrics_to_collect: list[str] | None = None,
        result_summary: str = "",
        status: str = "draft",
        risk_level: str = "low",
        possible_harm: str = "",
        mitigation_notes: str = "",
        human_oversight_required: bool = True,
        approval_status: str = "pending",
        reviewer_notes: str = "",
    ) -> dict:
        self.require_role(actor_id, {"admin", "reviewer", "researcher"})
        self._validate_risk_level(risk_level)
        self._validate_approval_status(approval_status)
        question = self.get_research_question(question_id)
        if question is None:
            raise ValueError("Research question not found.")
        if question["status"] != "approved":
            raise ValueError("Only approved questions can be converted into scenarios.")

        sid = str(uuid4())
        now = utc_now_iso()
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO simulation_scenarios
                (
                    id, research_question_id, purpose, agent_type, environment,
                    variables, metrics, ethical_constraints, created_by, created_at,
                    updated_at, environment_conditions, input_variables,
                    expected_observations, metrics_to_collect, result_summary, status,
                    risk_level, possible_harm, mitigation_notes, human_oversight_required,
                    approval_status, reviewer_notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sid,
                    question_id,
                    purpose,
                    agent_type,
                    environment,
                    json_dumps(variables),
                    json_dumps(metrics),
                    json_dumps(ethical_constraints),
                    actor_id,
                    now,
                    now,
                    environment_conditions,
                    json_dumps(input_variables if input_variables is not None else variables),
                    json_dumps(expected_observations or []),
                    json_dumps(metrics_to_collect if metrics_to_collect is not None else metrics),
                    result_summary,
                    status,
                    risk_level,
                    possible_harm,
                    mitigation_notes,
                    1 if human_oversight_required else 0,
                    approval_status,
                    reviewer_notes,
                ),
            )
        self._audit(actor_id, "scenario_created", "simulation_scenario", sid, {"question_id": question_id})
        self._audit(
            actor_id,
            "question_converted_to_scenario",
            "research_question",
            question_id,
            {"scenario_id": sid},
        )
        return self.get_scenario(sid)  # type: ignore[return-value]

    def get_scenario(self, scenario_id: str) -> dict | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM simulation_scenarios WHERE id = ?", (scenario_id,)).fetchone()
        if not row:
            return None
        return self._normalize_scenario(dict(row))

    def list_scenarios(
        self,
        status: str | None = None,
        risk_level: str | None = None,
        research_question_id: str | None = None,
    ) -> list[dict]:
        clauses = []
        params: list[object] = []
        if status is not None:
            clauses.append("status = ?")
            params.append(status)
        if risk_level is not None:
            self._validate_risk_level(risk_level)
            clauses.append("risk_level = ?")
            params.append(risk_level)
        if research_question_id is not None:
            clauses.append("research_question_id = ?")
            params.append(research_question_id)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                f"SELECT * FROM simulation_scenarios{where} ORDER BY created_at DESC",
                params,
            ).fetchall()
        return [self._normalize_scenario(dict(r)) for r in rows]

    def update_scenario(
        self,
        actor_id: str,
        scenario_id: str,
        purpose: str | None = None,
        agent_type: str | None = None,
        environment: str | None = None,
        variables: list[str] | None = None,
        metrics: list[str] | None = None,
        ethical_constraints: list[str] | None = None,
        environment_conditions: str | None = None,
        input_variables: list[str] | None = None,
        expected_observations: list[str] | None = None,
        metrics_to_collect: list[str] | None = None,
        result_summary: str | None = None,
        status: str | None = None,
        risk_level: str | None = None,
        possible_harm: str | None = None,
        mitigation_notes: str | None = None,
        human_oversight_required: bool | None = None,
        approval_status: str | None = None,
        reviewer_notes: str | None = None,
    ) -> dict:
        self.require_role(actor_id, {"admin", "reviewer", "researcher"})
        scenario = self.get_scenario(scenario_id)
        if scenario is None:
            raise ValueError("Scenario not found.")
        if risk_level is not None:
            self._validate_risk_level(risk_level)
        if approval_status is not None:
            self._validate_approval_status(approval_status)

        updated = {
            "purpose": purpose if purpose is not None else scenario["purpose"],
            "agent_type": agent_type if agent_type is not None else scenario["agent_type"],
            "environment": environment if environment is not None else scenario["environment"],
            "variables": variables if variables is not None else scenario["variables"],
            "metrics": metrics if metrics is not None else scenario["metrics"],
            "ethical_constraints": (
                ethical_constraints if ethical_constraints is not None else scenario["ethical_constraints"]
            ),
            "environment_conditions": (
                environment_conditions
                if environment_conditions is not None
                else scenario["environment_conditions"]
            ),
            "input_variables": input_variables if input_variables is not None else scenario["input_variables"],
            "expected_observations": (
                expected_observations
                if expected_observations is not None
                else scenario["expected_observations"]
            ),
            "metrics_to_collect": (
                metrics_to_collect if metrics_to_collect is not None else scenario["metrics_to_collect"]
            ),
            "result_summary": result_summary if result_summary is not None else scenario["result_summary"],
            "status": status if status is not None else scenario["status"],
            "risk_level": risk_level if risk_level is not None else scenario["risk_level"],
            "possible_harm": possible_harm if possible_harm is not None else scenario["possible_harm"],
            "mitigation_notes": mitigation_notes if mitigation_notes is not None else scenario["mitigation_notes"],
            "human_oversight_required": (
                human_oversight_required
                if human_oversight_required is not None
                else scenario["human_oversight_required"]
            ),
            "approval_status": approval_status if approval_status is not None else scenario["approval_status"],
            "reviewer_notes": reviewer_notes if reviewer_notes is not None else scenario["reviewer_notes"],
            "updated_at": utc_now_iso(),
        }

        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                UPDATE simulation_scenarios
                SET purpose = ?, agent_type = ?, environment = ?, variables = ?, metrics = ?,
                    ethical_constraints = ?, environment_conditions = ?, input_variables = ?,
                    expected_observations = ?, metrics_to_collect = ?, result_summary = ?,
                    status = ?, risk_level = ?, possible_harm = ?, mitigation_notes = ?,
                    human_oversight_required = ?, approval_status = ?, reviewer_notes = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    updated["purpose"],
                    updated["agent_type"],
                    updated["environment"],
                    json_dumps(updated["variables"]),
                    json_dumps(updated["metrics"]),
                    json_dumps(updated["ethical_constraints"]),
                    updated["environment_conditions"],
                    json_dumps(updated["input_variables"]),
                    json_dumps(updated["expected_observations"]),
                    json_dumps(updated["metrics_to_collect"]),
                    updated["result_summary"],
                    updated["status"],
                    updated["risk_level"],
                    updated["possible_harm"],
                    updated["mitigation_notes"],
                    1 if updated["human_oversight_required"] else 0,
                    updated["approval_status"],
                    updated["reviewer_notes"],
                    updated["updated_at"],
                    scenario_id,
                ),
            )
        self._audit(actor_id, "scenario_updated", "simulation_scenario", scenario_id, {})
        return self.get_scenario(scenario_id)  # type: ignore[return-value]

    def create_knowledge_entry(
        self,
        actor_id: str,
        title: str,
        content: str,
        source_type: str,
        source_id: str,
        linked_question_id: str | None = None,
        linked_scenario_id: str | None = None,
        linked_observation_id: str | None = None,
    ) -> dict:
        self.require_role(actor_id, {"admin", "reviewer", "researcher"})
        kid = str(uuid4())
        now = utc_now_iso()
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO knowledge_entries
                (id, title, content, source_type, source_id, linked_question_id, linked_scenario_id, linked_observation_id, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    kid,
                    title,
                    content,
                    source_type,
                    source_id,
                    linked_question_id,
                    linked_scenario_id,
                    linked_observation_id,
                    actor_id,
                    now,
                    now,
                ),
            )
        self._audit(actor_id, "knowledge_created", "knowledge_entry", kid, {"source_type": source_type, "source_id": source_id})
        return self.get_knowledge_entry(kid)  # type: ignore[return-value]

    def get_knowledge_entry(self, knowledge_id: str) -> dict | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM knowledge_entries WHERE id = ?", (knowledge_id,)).fetchone()
        return dict(row) if row else None

    def list_knowledge_entries(self) -> list[dict]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM knowledge_entries ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def recent_activity(self, limit: int = 100) -> list[dict]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["details"] = json_loads(d.get("details", "{}")) if isinstance(d.get("details"), str) else d.get("details")
            result.append(d)
        return result
