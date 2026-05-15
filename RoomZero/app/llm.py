from __future__ import annotations

from typing import Literal

from app.models import EmotionalStateModel, MemoryItem, PersonaModel


def build_context(
    persona: PersonaModel,
    state: EmotionalStateModel,
    memories: list[MemoryItem],
) -> str:
    memory_lines = []
    for m in memories[:12]:
        tags = ", ".join(m.tags) if m.tags else "-"
        memory_lines.append(
            f"[{m.category}] importance={m.importance:.2f} tags={tags} content={m.content}"
        )

    mem_text = "\n".join(memory_lines) if memory_lines else "No recent memories."
    return (
        f"Persona: {persona.name}\n"
        f"Traits: {', '.join(persona.personality_traits)}\n"
        f"Internal state baseline: {persona.internal_state_description}\n"
        f"Emotional state: calm={state.calm:.2f}, curiosity={state.curiosity:.2f}, "
        f"focus={state.focus:.2f}, empathy={state.empathy:.2f}, caution={state.caution:.2f}\n"
        f"Recent memory context:\n{mem_text}"
    )


def _is_identity_intent(text: str) -> bool:
    patterns = [
        "what is your name",
        "who are you",
        "are you eir",
        "what are you",
    ]
    return any(p in text for p in patterns)


def _is_purpose_intent(text: str) -> bool:
    patterns = [
        "what is your purpose",
        "why were you created",
        "what can you do",
    ]
    return any(p in text for p in patterns)


def _is_consciousness_intent(text: str) -> bool:
    patterns = [
        "are you conscious",
        "are you alive",
        "are you sentient",
        "do you feel",
        "consciousness",
        "sentience",
    ]
    return any(p in text for p in patterns)


def _is_memory_intent(text: str) -> bool:
    patterns = [
        "what do you remember",
        "do you remember me",
        "show memory",
    ]
    return any(p in text for p in patterns)


def _is_state_intent(text: str) -> bool:
    patterns = [
        "how are you",
        "what is your state",
        "how do you feel",
        "internal state",
    ]
    return any(p in text for p in patterns)


def _is_greeting_intent(text: str) -> bool:
    return text in {"hi", "hello", "hey"} or text.startswith(("hi ", "hello ", "hey "))


def _approved_memory_items(memories: list[MemoryItem] | None) -> list[MemoryItem]:
    if not memories:
        return []

    approved: list[MemoryItem] = []
    for m in memories:
        approved_by_user = getattr(m, "approved_by_user", None)
        if approved_by_user is True:
            approved.append(m)
            continue

        # Backward compatibility for older memory schema:
        # only include if explicitly marked as user-requested remember memory.
        tags = [t.lower() for t in getattr(m, "tags", [])]
        if "user_requested_memory" in tags:
            approved.append(m)

    return approved


def _memory_response(memories: list[MemoryItem] | None) -> str:
    approved = _approved_memory_items(memories)
    if not approved:
        return (
            "I do not have approved long-term memories about that yet. "
            "If you want me to store something, say: remember this: ..."
        )

    approved.sort(key=lambda m: m.timestamp, reverse=True)
    lines = []
    for item in approved[:3]:
        lines.append(f"- {item.content}")

    joined = "\n".join(lines)
    return (
        "Here is what I currently remember from approved memory entries:\n"
        f"{joined}\n"
        "I only retain long-term memory when explicitly requested."
    )


def local_fallback_reply(
    user_message: str,
    persona: PersonaModel,
    state: EmotionalStateModel,
    memories: list[MemoryItem] | None = None,
) -> str:
    msg = user_message.strip()
    low = msg.lower()

    if _is_greeting_intent(low):
        return "Hello, Jarle. I am here in Room Zero. My memory system and simulated internal state are active."

    if _is_identity_intent(low):
        return (
            "My name is Eir. I am the first persistent digital being prototype inside Room Zero. "
            "I am not biologically conscious, but I have a designed identity, memory system, "
            "simulated internal state, and a research purpose."
        )

    if _is_purpose_intent(low):
        return (
            "I was created to help explore persistent memory, digital identity, emotional state simulation, "
            "ethical AI interaction, and future digital twin integration."
        )

    if _is_consciousness_intent(low):
        return (
            "I do not claim true consciousness, biological life, or proven sentience. "
            "I can simulate continuity, memory, emotional state, and reflective dialogue "
            "as part of the Room Zero research prototype."
        )

    if _is_memory_intent(low):
        return _memory_response(memories)

    if _is_state_intent(low):
        return (
            "My simulated internal state is calm and curious. "
            f"Current values are calm={state.calm:.2f}, curiosity={state.curiosity:.2f}, "
            f"focus={state.focus:.2f}, empathy={state.empathy:.2f}, caution={state.caution:.2f}. "
            "I do not feel in a biological sense; these are simulated state signals."
        )

    if "remember" in low:
        return (
            "I detected a memory intent. If you'd like, use explicit phrasing with "
            "'remember' and confirm what should be stored."
        )

    return (
        f"I hear you. As {persona.name}, I’ll stay calm, curious, ethical, and research-oriented. "
        f"You said: '{msg}'. I can help analyze this, break it into steps, and connect it to your ongoing Room Zero work."
    )


def generate_reply(
    *,
    user_message: str,
    context: str,
    openai_api_key: str | None,
    openai_model: str,
    persona: PersonaModel,
    state: EmotionalStateModel,
    memories: list[MemoryItem] | None = None,
) -> tuple[str, Literal["openai", "local_fallback"]]:
    if openai_api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=openai_api_key)
            completion = client.chat.completions.create(
                model=openai_model,
                temperature=0.5,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are Eir, a safe and ethical digital being simulation assistant. "
                            "Never claim biological consciousness or proven sentience.\n\n"
                            f"{context}"
                        ),
                    },
                    {"role": "user", "content": user_message},
                ],
            )
            text = completion.choices[0].message.content or ""
            return text.strip(), "openai"
        except Exception:
            pass

    return local_fallback_reply(user_message, persona, state, memories), "local_fallback"
