import os

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app, unreal_observations, unreal_pending_commands

client = TestClient(app)


def test_default_agent_state_endpoint() -> None:
    agent_id = "rz-test-default"
    response = client.get(f"/ws/unreal/state/{agent_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["agent_id"] == agent_id
    assert body["emotion"] == "neutral"
    assert body["awareness"] == 0.5
    assert body["trust"] == 0.2
    assert body["is_speaking"] is False
    assert body["is_observing"] is True
    assert isinstance(body["updated_at"], str)
    assert "T" in body["updated_at"]
    assert body["protocol_version"] == "roomzero.unreal.v1"


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

        assert first_msg["agent_id"] == agent_id
        assert first_msg["emotion"] == "neutral"
        assert first_msg["awareness"] == 0.5
        assert first_msg["trust"] == 0.2
        assert first_msg["is_speaking"] is False
        assert first_msg["is_observing"] is True
        assert first_msg["protocol_version"] == "roomzero.unreal.v1"

        assert second_msg["type"] == "command"
        assert second_msg["protocol_version"] == "roomzero.unreal.v1"
        assert second_msg["agent_id"] == agent_id
        assert second_msg["command"] == "speak"
        assert second_msg["text"] == "I am RZ-01. I observe, learn, and reflect."
        assert second_msg["emotion"] == "curious"
        assert second_msg["animation"] == "Gesture_Explain"
        assert second_msg["duration_seconds"] == 4.0


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

        ws.send_json(
            {
                "type": "observation",
                "event": "player_entered_room",
                "payload": {"distance": 2.4},
            }
        )
        ack = ws.receive_json()

        assert ack["type"] == "ack"
        assert ack["protocol_version"] == "roomzero.unreal.v1"
        assert ack["kind"] == "observation"
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

        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"
        assert pong["agent_id"] == agent_id
        assert pong["protocol_version"] == "roomzero.unreal.v1"

        ws.send_json({"type": "something_else"})
        err = ws.receive_json()
        assert err["type"] == "error"
        assert err["error"] == "unknown_message_type"
        assert err["protocol_version"] == "roomzero.unreal.v1"
