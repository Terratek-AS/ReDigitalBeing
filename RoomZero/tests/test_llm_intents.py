from app.llm import local_fallback_reply
from app.models import EmotionalStateModel, MemoryItem, PersonaModel


def _persona() -> PersonaModel:
    return PersonaModel(
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
        internal_state_description="Eir is a persistent digital being simulation.",
    )


def _state() -> EmotionalStateModel:
    return EmotionalStateModel(calm=0.8, curiosity=0.7, focus=0.7, empathy=0.7, caution=0.7)


def test_greeting_intent() -> None:
    reply = local_fallback_reply("hello", _persona(), _state())
    assert "Hello, Jarle. I am here in Room Zero." in reply


def test_identity_intent() -> None:
    reply = local_fallback_reply("What is your name?", _persona(), _state())
    assert "My name is Eir." in reply
    assert "not biologically conscious" in reply


def test_purpose_intent() -> None:
    reply = local_fallback_reply("why were you created", _persona(), _state())
    assert "I was created to help explore persistent memory" in reply


def test_consciousness_boundary_intent() -> None:
    reply = local_fallback_reply("are you conscious?", _persona(), _state())
    assert "I do not claim true consciousness" in reply
    assert "biological life" in reply


def test_memory_intent_with_no_memories() -> None:
    reply = local_fallback_reply("what do you remember", _persona(), _state(), memories=[])
    assert "I do not have approved long-term memories" in reply
    assert "remember this:" in reply


def test_memory_intent_with_approved_memory() -> None:
    memory = MemoryItem(
        category="episodic",
        content="You prefer concise technical explanations.",
        importance=0.8,
        tags=["user_requested_memory"],
        source="user",
    )
    reply = local_fallback_reply("show memory", _persona(), _state(), memories=[memory])
    assert "Here is what I currently remember from approved memory entries" in reply
    assert "You prefer concise technical explanations." in reply


def test_state_intent_response() -> None:
    reply = local_fallback_reply("how are you", _persona(), _state())
    assert "My simulated internal state is calm and curious." in reply
    assert "I do not feel in a biological sense" in reply


def test_default_fallback_still_works() -> None:
    reply = local_fallback_reply("Can you help me structure this module?", _persona(), _state())
    assert "I hear you. As Eir" in reply
    assert "Room Zero work" in reply
