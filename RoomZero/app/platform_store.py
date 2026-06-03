from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from app.db import get_connection, init_db, json_dumps, json_loads


VALID_ROLES = {"observer", "tester", "researcher", "reviewer", "admin", "contributor"}
VALID_STATUSES = {"proposed", "approved", "testing", "completed", "archived"}


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
    ) -> dict:
        self.require_role(actor_id, {"admin", "researcher", "tester", "contributor"})
        qid = str(uuid4())
        now = utc_now_iso()
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO research_questions
                (id, title, description, category, hypothesis, simulation_relevance, ethical_risk, suggested_conditions, status, author, created_at, updated_at, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                ),
            )
        self._audit(actor_id, "question_created", "research_question", qid, {"status": "proposed"})
        return self.get_research_question(qid)  # type: ignore[return-value]

    def get_research_question(self, question_id: str) -> dict | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM research_questions WHERE id = ?", (question_id,)).fetchone()
        if not row:
            return None
        out = dict(row)
        out["tags"] = json_loads(out.get("tags", "[]"))
        return out

    def list_research_questions(self) -> list[dict]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM research_questions ORDER BY created_at DESC").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["tags"] = json_loads(d.get("tags", "[]"))
            result.append(d)
        return result

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
    ) -> dict:
        question = self.get_research_question(question_id)
        if question is None:
            raise ValueError("Research question not found.")
        user = self.require_role(actor_id, {"admin", "researcher", "tester", "contributor"})
        if user["role"] != "admin" and question["author"] != actor_id:
            raise ValueError("Only author or admin can edit this question.")

        updated = {
            "title": title if title is not None else question["title"],
            "description": description if description is not None else question["description"],
            "hypothesis": hypothesis if hypothesis is not None else question["hypothesis"],
            "simulation_relevance": simulation_relevance if simulation_relevance is not None else question["simulation_relevance"],
            "ethical_risk": ethical_risk if ethical_risk is not None else question["ethical_risk"],
            "suggested_conditions": suggested_conditions if suggested_conditions is not None else question["suggested_conditions"],
            "tags": tags if tags is not None else question["tags"],
            "updated_at": utc_now_iso(),
        }

        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                UPDATE research_questions
                SET title = ?, description = ?, hypothesis = ?, simulation_relevance = ?, ethical_risk = ?, suggested_conditions = ?, tags = ?, updated_at = ?
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
    ) -> dict:
        self.require_role(actor_id, {"admin", "reviewer", "researcher"})
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
                (id, research_question_id, purpose, agent_type, environment, variables, metrics, ethical_constraints, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                ),
            )
        self._audit(actor_id, "scenario_created", "simulation_scenario", sid, {"question_id": question_id})
        return self.get_scenario(sid)  # type: ignore[return-value]

    def get_scenario(self, scenario_id: str) -> dict | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM simulation_scenarios WHERE id = ?", (scenario_id,)).fetchone()
        if not row:
            return None
        out = dict(row)
        out["variables"] = json_loads(out.get("variables", "[]"))
        out["metrics"] = json_loads(out.get("metrics", "[]"))
        out["ethical_constraints"] = json_loads(out.get("ethical_constraints", "[]"))
        return out

    def list_scenarios(self) -> list[dict]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM simulation_scenarios ORDER BY created_at DESC").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["variables"] = json_loads(d.get("variables", "[]"))
            d["metrics"] = json_loads(d.get("metrics", "[]"))
            d["ethical_constraints"] = json_loads(d.get("ethical_constraints", "[]"))
            result.append(d)
        return result

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
