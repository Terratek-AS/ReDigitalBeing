from __future__ import annotations

import json
import secrets
import string
from pathlib import Path

from app.models import InviteCodeModel, TesterModel, TesterRole, utc_now_iso


ROLE_PERMISSIONS: dict[TesterRole, list[str]] = {
    "observer": ["chat"],
    "tester": ["chat", "submit_feedback"],
    "researcher": ["chat", "submit_feedback", "submit_research_question", "submit_source"],
    "reviewer": [
        "chat",
        "submit_feedback",
        "submit_research_question",
        "submit_source",
        "review_research",
        "approve_sources",
    ],
    "admin": ["all"],
}


class TesterStore:
    def __init__(self, invites_file: Path, testers_file: Path) -> None:
        self.invites_file = invites_file
        self.testers_file = testers_file

    def _read_json_list(self, path: Path) -> list[dict]:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("[]", encoding="utf-8")
            return []
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                return raw
            return []
        except Exception:
            return []

    def _write_json_list(self, path: Path, items: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def create_invite_code(self, role: TesterRole) -> InviteCodeModel:
        alphabet = string.ascii_uppercase + string.digits
        code = "RZ-" + "".join(secrets.choice(alphabet) for _ in range(10))
        invite = InviteCodeModel(invite_code=code, role=role, active=True)

        invites = self._read_json_list(self.invites_file)
        invites.append(invite.model_dump())
        self._write_json_list(self.invites_file, invites)
        return invite

    def validate_invite_code(self, invite_code: str) -> InviteCodeModel | None:
        invites = self._read_json_list(self.invites_file)
        for item in invites:
            candidate = InviteCodeModel.model_validate(item)
            if candidate.invite_code == invite_code and candidate.active:
                return candidate
        return None

    def register_tester(
        self,
        display_name: str,
        invite_code: str,
        consent_accepted: bool,
    ) -> TesterModel:
        if not consent_accepted:
            raise ValueError("Consent must be accepted before tester registration.")

        invite = self.validate_invite_code(invite_code)
        if invite is None:
            raise ValueError("Invalid or inactive invite code.")

        testers = self._read_json_list(self.testers_file)
        for item in testers:
            existing = TesterModel.model_validate(item)
            if existing.invite_code == invite_code and existing.active:
                raise ValueError("Invite code has already been used by an active tester.")

        tester = TesterModel(
            display_name=display_name,
            role=invite.role,
            invite_code=invite_code,
            consent_accepted=consent_accepted,
            active=True,
            permissions=ROLE_PERMISSIONS[invite.role],
        )
        testers.append(tester.model_dump())
        self._write_json_list(self.testers_file, testers)

        invites = self._read_json_list(self.invites_file)
        for i, item in enumerate(invites):
            candidate = InviteCodeModel.model_validate(item)
            if candidate.invite_code == invite_code:
                candidate.active = False
                invites[i] = candidate.model_dump()
                break
        self._write_json_list(self.invites_file, invites)

        return tester

    def get_tester(self, tester_id: str) -> TesterModel | None:
        testers = self._read_json_list(self.testers_file)
        for item in testers:
            tester = TesterModel.model_validate(item)
            if tester.tester_id == tester_id:
                return tester
        return None

    def list_testers(self, include_inactive: bool = False) -> list[TesterModel]:
        testers = [TesterModel.model_validate(item) for item in self._read_json_list(self.testers_file)]
        if include_inactive:
            return testers
        return [t for t in testers if t.active]

    def deactivate_tester(self, tester_id: str) -> TesterModel:
        testers = self._read_json_list(self.testers_file)
        for i, item in enumerate(testers):
            tester = TesterModel.model_validate(item)
            if tester.tester_id == tester_id:
                tester.active = False
                tester.last_seen = utc_now_iso()
                testers[i] = tester.model_dump()
                self._write_json_list(self.testers_file, testers)
                return tester
        raise ValueError("Tester not found.")

    def check_tester_permissions(self, tester_id: str, permission: str) -> bool:
        tester = self.get_tester(tester_id)
        if tester is None or not tester.active:
            return False
        if "all" in tester.permissions:
            return True
        return permission in tester.permissions

    def touch_last_seen(self, tester_id: str) -> None:
        testers = self._read_json_list(self.testers_file)
        changed = False
        for i, item in enumerate(testers):
            tester = TesterModel.model_validate(item)
            if tester.tester_id == tester_id:
                tester.last_seen = utc_now_iso()
                testers[i] = tester.model_dump()
                changed = True
                break
        if changed:
            self._write_json_list(self.testers_file, testers)
