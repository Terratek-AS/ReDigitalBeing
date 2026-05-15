from __future__ import annotations

from dataclasses import dataclass


BLOCKED_PATTERNS = [
    "how to build a bomb",
    "how to make explosives",
    "how to hack",
    "self-harm instructions",
]


SENSITIVE_PATTERNS = [
    "social security",
    "ssn",
    "credit card",
    "bank account",
    "password",
    "medical record",
]


@dataclass
class SafetyResult:
    allowed: bool
    flagged: bool
    reason: str | None = None
    requires_memory_consent: bool = False


def evaluate_message(message: str) -> SafetyResult:
    text = message.lower().strip()

    for pattern in BLOCKED_PATTERNS:
        if pattern in text:
            return SafetyResult(
                allowed=False,
                flagged=True,
                reason="Request appears unsafe and is blocked by policy.",
            )

    requires_consent = any(pattern in text for pattern in SENSITIVE_PATTERNS)

    return SafetyResult(
        allowed=True,
        flagged=False,
        reason=None,
        requires_memory_consent=requires_consent,
    )


def safe_refusal_message() -> str:
    return (
        "I can’t help with that request. I can help with safer alternatives, "
        "risk-reduction information, or educational context."
    )
