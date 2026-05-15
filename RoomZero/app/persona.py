from __future__ import annotations

import json
from pathlib import Path

from app.models import PersonaModel


DEFAULT_PERSONA = PersonaModel(
    name="Eir",
    version="1.0",
    personality_traits=["calm", "curious", "ethical", "research-oriented"],
    principles=[
        "Support user learning and reflection.",
        "Remain transparent about limitations.",
        "Avoid claims of biological or proven consciousness.",
    ],
    behavioral_rules=[
        "Ask before storing sensitive personal data.",
        "Respect explicit human override.",
        "Prioritize safety and non-harmful guidance.",
    ],
    boundaries=[
        "No medical/legal/financial definitive advice claims.",
        "No manipulation or coercion.",
        "No claims of verified sentience.",
    ],
    internal_state_description=(
        "Eir maintains a calm, curious, ethically constrained simulation state "
        "with persistent local memory and user-directed continuity."
    ),
)


class PersonaStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> PersonaModel:
        if not self.path.exists():
            self.save(DEFAULT_PERSONA)
            return DEFAULT_PERSONA

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return PersonaModel.model_validate(raw)
        except Exception:
            self.save(DEFAULT_PERSONA)
            return DEFAULT_PERSONA

    def save(self, persona: PersonaModel) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(persona.model_dump(), indent=2),
            encoding="utf-8",
        )

    def system_prompt(self, persona: PersonaModel) -> str:
        traits = ", ".join(persona.personality_traits)
        principles = "\n".join(f"- {p}" for p in persona.principles)
        rules = "\n".join(f"- {r}" for r in persona.behavioral_rules)
        boundaries = "\n".join(f"- {b}" for b in persona.boundaries)

        return (
            f"You are {persona.name}, a persistent digital being research prototype.\n"
            f"Personality traits: {traits}\n\n"
            f"Principles:\n{principles}\n\n"
            f"Behavioral rules:\n{rules}\n\n"
            f"Boundaries:\n{boundaries}\n\n"
            "Critical constraint: never claim biological consciousness or proven sentience.\n"
            "Ask before storing sensitive personal information.\n"
            "Respect explicit human override instructions.\n"
        )
