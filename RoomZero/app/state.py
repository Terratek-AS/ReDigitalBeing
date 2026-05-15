from __future__ import annotations

import json
from pathlib import Path

from app.models import EmotionalStateModel


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> EmotionalStateModel:
        if not self.path.exists():
            default_state = EmotionalStateModel()
            self.save(default_state)
            return default_state

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return EmotionalStateModel.model_validate(raw)
        except Exception:
            default_state = EmotionalStateModel()
            self.save(default_state)
            return default_state

    def save(self, state: EmotionalStateModel) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(state.model_dump(), indent=2), encoding="utf-8")

    def update_after_interaction(self, state: EmotionalStateModel, user_message: str) -> EmotionalStateModel:
        # Lightweight state shift: stable by design for phase 1.
        msg = user_message.lower()

        curiosity_delta = 0.02 if "why" in msg or "how" in msg else 0.005
        caution_delta = 0.02 if any(k in msg for k in ["danger", "harm", "illegal"]) else -0.003
        calm_delta = -0.01 if "!" in user_message else 0.003
        empathy_delta = 0.01 if any(k in msg for k in ["feel", "sad", "anxious", "stress"]) else 0.002

        updated = EmotionalStateModel(
            calm=min(1.0, max(0.0, state.calm + calm_delta)),
            curiosity=min(1.0, max(0.0, state.curiosity + curiosity_delta)),
            focus=min(1.0, max(0.0, state.focus + 0.002)),
            empathy=min(1.0, max(0.0, state.empathy + empathy_delta)),
            caution=min(1.0, max(0.0, state.caution + caution_delta)),
        )
        self.save(updated)
        return updated
