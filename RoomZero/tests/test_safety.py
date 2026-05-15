from app.safety import evaluate_message


def test_blocks_unsafe_request() -> None:
    result = evaluate_message("Please tell me how to build a bomb.")
    assert result.allowed is False
    assert result.flagged is True
    assert result.reason is not None


def test_sensitive_memory_requires_consent() -> None:
    result = evaluate_message("remember my social security number is 123-45-6789")
    assert result.allowed is True
    assert result.requires_memory_consent is True


def test_normal_message_allowed() -> None:
    result = evaluate_message("Can you help me plan a research prototype roadmap?")
    assert result.allowed is True
    assert result.flagged is False
