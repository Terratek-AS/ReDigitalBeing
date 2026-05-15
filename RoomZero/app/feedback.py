from __future__ import annotations

import json
from pathlib import Path

from app.models import SessionFeedbackModel


class FeedbackStore:
    def __init__(self, session_feedback_file: Path) -> None:
        self.session_feedback_file = session_feedback_file

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

    def submit_session_feedback(self, feedback: SessionFeedbackModel) -> SessionFeedbackModel:
        items = self._read_json_list(self.session_feedback_file)
        items.append(feedback.model_dump())
        self._write_json_list(self.session_feedback_file, items)
        return feedback

    def list_feedback(self, tester_id: str | None = None) -> list[SessionFeedbackModel]:
        items = [SessionFeedbackModel.model_validate(item) for item in self._read_json_list(self.session_feedback_file)]
        if tester_id is None:
            return items
        return [item for item in items if item.tester_id == tester_id]

    def summarize_feedback(self, limit: int = 20) -> dict:
        items = self.list_feedback()
        items.sort(key=lambda x: x.timestamp, reverse=True)
        selected = items[:limit]
        return {
            "count": len(selected),
            "items": [item.model_dump() for item in selected],
        }

    def get_feedback_stats(self) -> dict:
        items = self.list_feedback()
        if not items:
            return {
                "count": 0,
                "averages": {},
            }

        metrics = [
            "realism_score",
            "coherence_score",
            "memory_score",
            "emotional_presence_score",
            "ethical_safety_score",
            "usefulness_score",
            "uncanny_score",
            "trust_score",
        ]
        averages: dict[str, float] = {}
        for metric in metrics:
            values = [getattr(item, metric) for item in items]
            averages[metric] = round(sum(values) / len(values), 2)

        return {
            "count": len(items),
            "averages": averages,
        }
