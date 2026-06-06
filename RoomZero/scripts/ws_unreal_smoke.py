from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import Any, cast

try:
    import websockets
except ImportError as exc:  # pragma: no cover - runtime guard for optional dependency
    raise SystemExit(
        "Missing dependency: websockets. Install with `pip install websockets`."
    ) from exc


def _build_ws_url(base_url: str, agent_id: str, token: str | None) -> str:
    base = base_url.rstrip("/")
    url = f"{base}/ws/unreal/{agent_id}"
    if token:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}token={token}"
    return url


async def run_smoke(
    base_url: str,
    agent_id: str,
    token: str | None = None,
    expect_protocol: str = "roomzero.unreal.v1",
    send_unknown_message: bool = False,
    timeout_seconds: float = 8.0,
) -> int:
    ws_url = _build_ws_url(base_url=base_url, agent_id=agent_id, token=token)
    headers: dict[str, str] = {}
    if token:
        headers["X-RoomZero-Unreal-Token"] = token

    print(f"[smoke] connecting: {ws_url}")
    try:
        async with websockets.connect(ws_url, additional_headers=headers) as ws:
            initial_state_raw = cast(Any, await asyncio.wait_for(ws.recv(), timeout=timeout_seconds))
            state_obj = json.loads(cast(str, initial_state_raw))
            print("[smoke] initial_state:", json.dumps(state_obj, indent=2))

            greeting_raw = cast(Any, await asyncio.wait_for(ws.recv(), timeout=timeout_seconds))
            greeting_obj = json.loads(cast(str, greeting_raw))
            print("[smoke] greeting_or_command:", json.dumps(greeting_obj, indent=2))

            if state_obj.get("protocol_version") != expect_protocol:
                print(
                    f"[smoke] ERROR: unexpected protocol_version in initial state; expected {expect_protocol}"
                )
                return 2

            await ws.send(json.dumps({"type": "ping"}))
            pong_raw = cast(Any, await asyncio.wait_for(ws.recv(), timeout=timeout_seconds))
            pong_obj = json.loads(cast(str, pong_raw))
            print("[smoke] pong:", json.dumps(pong_obj, indent=2))

            if pong_obj.get("protocol_version") != expect_protocol:
                print(
                    f"[smoke] ERROR: unexpected protocol_version in pong; expected {expect_protocol}"
                )
                return 3

            if send_unknown_message:
                await ws.send(json.dumps({"type": "unsupported_message"}))
                unknown_raw = cast(Any, await asyncio.wait_for(ws.recv(), timeout=timeout_seconds))
                unknown_obj = json.loads(cast(str, unknown_raw))
                print("[smoke] unknown_message_error:", json.dumps(unknown_obj, indent=2))
                if (
                    unknown_obj.get("type") != "error"
                    or unknown_obj.get("error") != "unknown_message_type"
                    or unknown_obj.get("protocol_version") != expect_protocol
                ):
                    print("[smoke] ERROR: expected stable unknown_message_type error")
                    return 6

            observation_msg = {
                "type": "observation",
                "event": "smoke_test_event",
                "payload": {"source": "ws_unreal_smoke.py", "ok": True},
            }
            await ws.send(json.dumps(observation_msg))
            ack_raw = cast(Any, await asyncio.wait_for(ws.recv(), timeout=timeout_seconds))
            ack_obj = json.loads(cast(str, ack_raw))
            print("[smoke] observation_ack:", json.dumps(ack_obj, indent=2))

            if ack_obj.get("type") != "ack":
                print("[smoke] ERROR: observation ack not received")
                return 4
    except TimeoutError:
        print(f"[smoke] ERROR: timed out waiting for message (> {timeout_seconds}s)")
        return 5
    except Exception as exc:
        print(f"[smoke] ERROR: smoke run failed: {exc}")
        return 7

    print("[smoke] completed successfully")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RoomZero Unreal WebSocket smoke client")
    parser.add_argument(
        "--base-url",
        default="ws://127.0.0.1:8000",
        help="WebSocket base URL (default: ws://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--agent-id",
        default="rz-smoke",
        help="Agent id for the Unreal bridge (default: rz-smoke)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Optional Unreal token (defaults to ROOMZERO_WS_TOKEN env var when unset)",
    )
    parser.add_argument(
        "--expect-protocol",
        default="roomzero.unreal.v1",
        help="Expected protocol version for incoming messages (default: roomzero.unreal.v1)",
    )
    parser.add_argument(
        "--send-unknown-message",
        action="store_true",
        help="Send an unsupported message and verify the bridge returns a stable unknown_message_type error.",
    )
    parser.add_argument(
        "--timeout-seconds",
        "--timeout",
        dest="timeout_seconds",
        type=float,
        default=8.0,
        help="Read timeout for each recv call (default: 8.0)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = args.token if args.token else os.getenv("ROOMZERO_WS_TOKEN")
    if token and not args.token:
        print("[smoke] using token from ROOMZERO_WS_TOKEN")
    exit_code = asyncio.run(
        run_smoke(
            base_url=args.base_url,
            agent_id=args.agent_id,
            token=token,
            expect_protocol=args.expect_protocol,
            send_unknown_message=args.send_unknown_message,
            timeout_seconds=args.timeout_seconds,
        )
    )
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
