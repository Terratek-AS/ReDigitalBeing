import json
import os
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import (
    UNREAL_SIMULATION_EVENT_CAP,
    app,
    unreal_observations,
    unreal_pending_commands,
    unreal_simulation_events,
)

client = TestClient(app)
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "unreal_ws"


def _load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_default_agent_state_endpoint() -> None:
    agent_id = "rz-test-default"
    response = client.get(f"/ws/unreal/state/{agent_id}")
    assert response.status_code == 200
    body = response.json()
    expected = _load_fixture("initial_state.json")
    assert body["protocol_version"] == expected["protocol_version"]
    assert body["agent_id"] == agent_id
    assert body["emotion"] == expected["emotion"]
    assert body["awareness"] == expected["awareness"]
    assert body["trust"] == expected["trust"]
    assert body["is_speaking"] == expected["is_speaking"]
    assert body["is_observing"] == expected["is_observing"]
    assert isinstance(body["updated_at"], str)
    assert "T" in body["updated_at"]


def test_token_auth_unset_allows_public_access() -> None:
    original_token = os.environ.get("ROOMZERO_UNREAL_TOKEN")
    os.environ.pop("ROOMZERO_UNREAL_TOKEN", None)
    agent_id = "rz-test-token-unset"

    try:
        response = client.get(f"/ws/unreal/state/{agent_id}")
        assert response.status_code == 200
        assert response.json()["agent_id"] == agent_id

        post_payload = {
            "protocol_version": "roomzero.unreal.v1",
            "agent_id": agent_id,
            "command": "speak",
            "text": "No token required",
        }
        post_response = client.post(f"/ws/unreal/command/{agent_id}", json=post_payload)
        assert post_response.status_code == 200
        body = post_response.json()
        assert body["queued"] is True
        assert body["delivered"] is False
        assert body["agent_id"] == agent_id
        assert body["protocol_version"] == "roomzero.unreal.v1"

        with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
            state = ws.receive_json()
            assert state["agent_id"] == agent_id
            assert state["protocol_version"] == "roomzero.unreal.v1"
    finally:
        if original_token is None:
            os.environ.pop("ROOMZERO_UNREAL_TOKEN", None)
        else:
            os.environ["ROOMZERO_UNREAL_TOKEN"] = original_token


def test_token_auth_valid_invalid_for_rest_and_websocket() -> None:
    original_token = os.environ.get("ROOMZERO_UNREAL_TOKEN")
    os.environ["ROOMZERO_UNREAL_TOKEN"] = "secret-token"
    unreal_pending_commands.clear()
    unreal_observations.clear()

    try:
        agent_id = "rz-test-token-auth"

        state_response = client.get(f"/ws/unreal/state/{agent_id}")
        assert state_response.status_code == 200
        assert state_response.json()["agent_id"] == agent_id

        payload = {
            "protocol_version": "roomzero.unreal.v1",
            "agent_id": agent_id,
            "command": "speak",
            "text": "token guarded command",
        }

        missing_token = client.post(f"/ws/unreal/command/{agent_id}", json=payload)
        assert missing_token.status_code == 401

        invalid_token = client.post(
            f"/ws/unreal/command/{agent_id}",
            json=payload,
            params={"token": "invalid"},
        )
        assert invalid_token.status_code == 401

        valid_query_token = client.post(
            f"/ws/unreal/command/{agent_id}",
            json=payload,
            params={"token": "secret-token"},
        )
        assert valid_query_token.status_code == 200
        assert valid_query_token.json()["protocol_version"] == "roomzero.unreal.v1"

        valid_header_token = client.post(
            f"/ws/unreal/command/{agent_id}",
            json=payload,
            headers={"X-RoomZero-Unreal-Token": "secret-token"},
        )
        assert valid_header_token.status_code == 200
        assert valid_header_token.json()["protocol_version"] == "roomzero.unreal.v1"

        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(f"/ws/unreal/{agent_id}?token=invalid"):
                pass
        assert exc_info.value.code == 1008

        with pytest.raises(WebSocketDisconnect) as exc_missing:
            with client.websocket_connect(f"/ws/unreal/{agent_id}"):
                pass
        assert exc_missing.value.code == 1008

        with client.websocket_connect(f"/ws/unreal/{agent_id}?token=secret-token") as ws:
            state = ws.receive_json()
            assert state["agent_id"] == agent_id
            assert state["protocol_version"] == "roomzero.unreal.v1"
    finally:
        if original_token is None:
            os.environ.pop("ROOMZERO_UNREAL_TOKEN", None)
        else:
            os.environ["ROOMZERO_UNREAL_TOKEN"] = original_token


def test_websocket_initial_state_and_greeting_command() -> None:
    agent_id = "rz-test-ws-init"
    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        first_msg = ws.receive_json()
        second_msg = ws.receive_json()

        expected_state = _load_fixture("initial_state.json")
        assert first_msg["protocol_version"] == expected_state["protocol_version"]
        assert first_msg["agent_id"] == agent_id
        assert first_msg["emotion"] == expected_state["emotion"]
        assert first_msg["awareness"] == expected_state["awareness"]
        assert first_msg["trust"] == expected_state["trust"]
        assert first_msg["is_speaking"] == expected_state["is_speaking"]
        assert first_msg["is_observing"] == expected_state["is_observing"]

        expected_command = _load_fixture("greeting_command.json")
        assert second_msg["type"] == expected_command["type"]
        assert second_msg["protocol_version"] == expected_command["protocol_version"]
        assert second_msg["agent_id"] == agent_id
        assert second_msg["command"] == expected_command["command"]
        assert second_msg["text"] == expected_command["text"]
        assert second_msg["emotion"] == expected_command["emotion"]
        assert second_msg["animation"] == expected_command["animation"]
        assert second_msg["duration_seconds"] == expected_command["duration_seconds"]


def test_queued_command_flush_on_connect() -> None:
    agent_id = "rz-test-queue-flush"
    unreal_pending_commands.clear()
    unreal_observations.clear()

    first_payload = {
        "protocol_version": "roomzero.unreal.v1",
        "agent_id": agent_id,
        "command": "speak",
        "text": "First queued command",
    }
    second_payload = {
        "protocol_version": "roomzero.unreal.v1",
        "agent_id": agent_id,
        "command": "speak",
        "text": "Second queued command",
    }

    res1 = client.post(f"/ws/unreal/command/{agent_id}", json=first_payload)
    assert res1.status_code == 200
    assert res1.json()["queued"] is True
    assert res1.json()["delivered"] is False
    assert res1.json()["protocol_version"] == "roomzero.unreal.v1"

    res2 = client.post(f"/ws/unreal/command/{agent_id}", json=second_payload)
    assert res2.status_code == 200
    assert res2.json()["queued"] is True
    assert res2.json()["delivered"] is False
    assert res2.json()["protocol_version"] == "roomzero.unreal.v1"

    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        queued_first = ws.receive_json()
        queued_second = ws.receive_json()

        assert queued_first["protocol_version"] == "roomzero.unreal.v1"
        assert queued_first["command"] == "speak"
        assert queued_first["text"] == "First queued command"

        assert queued_second["protocol_version"] == "roomzero.unreal.v1"
        assert queued_second["command"] == "speak"
        assert queued_second["text"] == "Second queued command"


def test_observation_ack() -> None:
    unreal_observations.clear()
    agent_id = "rz-test-observation"

    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        ws.send_json(_load_fixture("observation_event.json"))
        ack = ws.receive_json()

        expected_ack = _load_fixture("observation_ack.json")
        assert ack["type"] == expected_ack["type"]
        assert ack["protocol_version"] == expected_ack["protocol_version"]
        assert ack["kind"] == expected_ack["kind"]
        assert ack["agent_id"] == agent_id
        assert isinstance(ack["created_at"], str)

    obs_response = client.get("/ws/unreal/observations")
    assert obs_response.status_code == 200
    obs_body = obs_response.json()
    assert obs_body["count"] >= 1
    last_item = obs_body["items"][-1]
    assert last_item["agent_id"] == agent_id
    assert last_item["event"] == "player_entered_room"
    assert last_item["payload"] == {"distance": 2.4}


def test_observation_retention_cap_prunes_oldest() -> None:
    unreal_observations.clear()
    agent_id = "rz-test-observation-cap"

    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        for index in range(502):
            ws.send_json(
                {
                    "type": "observation",
                    "event": f"event_{index + 1}",
                    "payload": {"count": index + 1},
                }
            )
            ack = ws.receive_json()
            assert ack["type"] == "ack"

    obs_response = client.get("/ws/unreal/observations")
    assert obs_response.status_code == 200
    obs_body = obs_response.json()
    assert obs_body["count"] == 500
    assert obs_body["items"][0]["event"] == "event_3"
    assert obs_body["items"][-1]["event"] == "event_502"


def test_ping_pong_and_unknown_message_safety() -> None:
    agent_id = "rz-test-ping"
    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        ws.send_json(_load_fixture("ping.json"))
        pong = ws.receive_json()
        expected_pong = _load_fixture("pong.json")
        assert pong["type"] == expected_pong["type"]
        assert pong["agent_id"] == agent_id
        assert pong["protocol_version"] == expected_pong["protocol_version"]

        ws.send_json({"type": "something_else"})
        err = ws.receive_json()
        expected_error = _load_fixture("unknown_message_error.json")
        assert err["type"] == expected_error["type"]
        assert err["error"] == expected_error["error"]
        assert err["protocol_version"] == expected_error["protocol_version"]


def test_websocket_invalid_non_object_payload_returns_invalid_payload_error() -> None:
    agent_id = "rz-test-invalid-payload"
    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        ws.send_text(json.dumps("not-an-object"))
        err = ws.receive_json()

        assert err["type"] == "error"
        assert err["error"] == "invalid_payload"
        assert err["protocol_version"] == "roomzero.unreal.v1"


def test_websocket_observation_payload_non_object_is_normalized() -> None:
    unreal_observations.clear()
    agent_id = "rz-test-observation-non-object-payload"

    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        ws.send_json(
            {
                "type": "observation",
                "event": "smoke_payload_normalization",
                "payload": "not-an-object",
            }
        )
        ack = ws.receive_json()

        assert ack["type"] == "ack"
        assert ack["protocol_version"] == "roomzero.unreal.v1"
        assert ack["agent_id"] == agent_id

    obs_response = client.get("/ws/unreal/observations")
    assert obs_response.status_code == 200
    assert obs_response.json()["items"][-1]["payload"] == {}


def test_websocket_missing_observation_event_returns_error() -> None:
    agent_id = "rz-test-missing-event"
    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        ws.send_json({"type": "observation", "payload": {"distance": 1.0}})
        err = ws.receive_json()

        assert err["type"] == "error"
        assert err["error"] == "missing_event"
        assert err["protocol_version"] == "roomzero.unreal.v1"


def test_websocket_runtime_responses_always_include_protocol_version() -> None:
    agent_id = "rz-test-protocol-version"
    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        ws.send_json({"type": "hello"})
        hello_response = ws.receive_json()
        assert hello_response["protocol_version"] == "roomzero.unreal.v1"

        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["protocol_version"] == "roomzero.unreal.v1"

        ws.send_text(json.dumps("broken payload"))
        invalid_payload_response = ws.receive_json()
        assert invalid_payload_response["protocol_version"] == "roomzero.unreal.v1"
        assert invalid_payload_response["error"] == "invalid_payload"


def test_simulation_event_normalization_from_observation() -> None:
    unreal_observations.clear()
    unreal_simulation_events.clear()
    agent_id = "rz-test-sim-normalization"

    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        ws.send_json(
            {
                "type": "observation",
                "event": "player_entered_room",
                "payload": {"distance": 2.4, "zone": "A1"},
            }
        )
        ack = ws.receive_json()
        assert ack["type"] == "ack"
        assert ack["kind"] == "observation"

    assert len(unreal_simulation_events) >= 1
    event = unreal_simulation_events[-1]
    dumped = event.model_dump()

    assert dumped["event_type"] == "unreal.observation.player_entered_room"
    assert dumped["source"] == "unreal.websocket"
    assert dumped["agent_id"] == agent_id
    assert dumped["protocol_version"] == "roomzero.unreal.v1"
    assert dumped["status"] == "accepted"
    assert dumped["severity"] == "info"
    assert dumped["transport"] == "websocket"
    assert dumped["schema_version"] == "roomzero.simulation-event.v1"
    assert dumped["correlation_id"] == f"{agent_id}:{dumped['created_at']}"

    assert dumped["metadata"]["observation_event"] == "player_entered_room"
    assert dumped["metadata"]["normalization_rule"] == "strip+lower+space_to_underscore"
    assert dumped["metadata"]["transport"] == "websocket"
    payload_summary = dumped["metadata"]["payload_summary"]
    assert payload_summary["keys"] == ["distance", "zone"]
    assert payload_summary["size"] == 2


def test_simulation_event_retention_cap_prunes_oldest() -> None:
    unreal_simulation_events.clear()
    agent_id = "rz-test-sim-cap"

    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        for idx in range(UNREAL_SIMULATION_EVENT_CAP + 2):
            ws.send_json(
                {
                    "type": "observation",
                    "event": f"sim_event_{idx + 1}",
                    "payload": {"index": idx + 1},
                }
            )
            ack = ws.receive_json()
            assert ack["type"] == "ack"

    assert len(unreal_simulation_events) == UNREAL_SIMULATION_EVENT_CAP
    first = unreal_simulation_events[0].model_dump()
    last = unreal_simulation_events[-1].model_dump()
    assert first["event_type"] == "unreal.observation.sim_event_3"
    assert last["event_type"] == f"unreal.observation.sim_event_{UNREAL_SIMULATION_EVENT_CAP + 2}"


def test_simulation_event_trace_logging_uses_payload_summary_only(capsys: pytest.CaptureFixture[str]) -> None:
    unreal_simulation_events.clear()
    agent_id = "rz-test-sim-trace"

    with client.websocket_connect(f"/ws/unreal/{agent_id}") as ws:
        _ = ws.receive_json()
        _ = ws.receive_json()

        ws.send_json(
            {
                "type": "observation",
                "event": "trace_check",
                "payload": {"very_sensitive_value": "secret-123", "level": 7},
            }
        )
        ack = ws.receive_json()
        assert ack["type"] == "ack"

    captured = capsys.readouterr().out
    assert "[simulation-event]" in captured
    assert "event_type=unreal.observation.trace_check" in captured
    assert "payload_summary=" in captured
    assert "very_sensitive_value" in captured
    assert "secret-123" not in captured
