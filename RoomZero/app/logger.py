from __future__ import annotations

import json
from pathlib import Path

from app.models import ConversationLogItem


class ConversationLogger:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _load(self) -> list[ConversationLogItem]:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("[]", encoding="utf-8")
            return []

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return [ConversationLogItem.model_validate(item) for item in raw]
        except Exception:
            return []

    def _save(self, items: list[ConversationLogItem]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([item.model_dump() for item in items], indent=2),
            encoding="utf-8",
        )

    def add(self, item: ConversationLogItem) -> None:
        logs = self._load()
        logs.append(item)
        logs = logs[-2000:]  # prevent unbounded growth in phase 1
        self._save(logs)

    def recent(self, limit: int = 50) -> list[ConversationLogItem]:
        logs = self._load()
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs[:limit]
