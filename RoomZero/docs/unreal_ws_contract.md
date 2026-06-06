# RoomZero Unreal WebSocket Contract (M1.4)

This document defines the Unreal bridge message contract for `roomzero.unreal.v1`.
It is intentionally compact and additive: clients should verify protocol identity and ignore unknown additive fields.

## 1) Protocol identity

- **Protocol name:** `roomzero.unreal.v1`
- **Primary WebSocket endpoint:** `/ws/unreal/{agent_id}`
- **Supporting REST endpoints:**
  - `GET /ws/unreal/state/{agent_id}`
  - `POST /ws/unreal/command/{agent_id}`
  - `GET /ws/unreal/observations`

`agent_id` is the canonical state key for session routing, command delivery, and observation attribution.

## 2) Connection lifecycle and handshake

1. Client opens a WebSocket to `ws://host/ws/unreal/{agent_id}`.
2. If Unreal token auth is enabled and the provided token is missing or invalid, the server closes the socket with code `1008`.
3. After a successful connect, the server sends the following server-first sequence:
   - current **AgentState**
   - greeting **AgentCommand** (`type="command"`)
   - any queued command messages for `agent_id`
4. The client may then send runtime messages.

### Protocol behavior guarantees

- The bridge is **server-first** on connect. Clients may send a `hello` message after connect, but it is not required.
- The server will always include `protocol_version` in outgoing runtime responses.
- Clients should not depend on a client-first handshake before receiving state.
- When the server accepts a connection, it will preserve `agent_id` routing across the session.

## 3) Auth behavior (optional)

Local development may use the bridge without a token if `ROOMZERO_UNREAL_TOKEN` is unset.

If `ROOMZERO_UNREAL_TOKEN` is set, token validation is required for:
- `POST /ws/unreal/command/{agent_id}`
- `WS /ws/unreal/{agent_id}`

Accepted token sources:
- query: `?token=...`
- header: `X-RoomZero-Unreal-Token: ...`
- header: `Authorization: Bearer ...`

## 4) Contract payloads

### 4.1 Initial state payload (server -> client)

```json
{
  "protocol_version": "roomzero.unreal.v1",
  "agent_id": "rz-01",
  "emotion": "neutral",
  "awareness": 0.5,
  "trust": 0.2,
  "is_speaking": false,
  "is_observing": true,
  "updated_at": "2025-01-01T12:00:00+00:00"
}
```

Required fields:
- `protocol_version` (string; must equal `roomzero.unreal.v1`)
- `agent_id` (string)
- `emotion` (string)
- `awareness` (number in `[0.0, 1.0]`)
- `trust` (number in `[0.0, 1.0]`)
- `is_speaking` (boolean)
- `is_observing` (boolean)
- `updated_at` (ISO datetime string)

### 4.2 Agent command payload (server -> client; REST enqueue/broadcast)

```json
{
  "protocol_version": "roomzero.unreal.v1",
  "type": "command",
  "agent_id": "rz-01",
  "command": "speak",
  "text": "I am RZ-01. I observe, learn, and reflect.",
  "emotion": "curious",
  "animation": "Gesture_Explain",
  "duration_seconds": 4.0
}
```

Required fields:
- `protocol_version` (string; exact value)
- `type` (string; stable value: `"command"`)
- `agent_id` (string)
- `command` (string)

Optional fields:
- `text` (string)
- `emotion` (string)
- `animation` (string)
- `duration_seconds` (number)

### 4.3 Observation event payload (client -> server)

```json
{
  "type": "observation",
  "event": "player_entered_room",
  "payload": {
    "distance": 2.4
  }
}
```

Required fields:
- `type` (must be `"observation"`)
- `event` (non-empty string)

Optional fields:
- `payload` (object; if missing or non-object, server normalizes to `{}`)

Server persistence shape (`ObservationEvent`) includes:
- `protocol_version`, `type`, `agent_id`, `event`, `payload`, `created_at`

### 4.4 Ping / pong

Ping (client -> server):
```json
{ "type": "ping" }
```

Pong (server -> client):
```json
{
  "type": "pong",
  "protocol_version": "roomzero.unreal.v1",
  "agent_id": "rz-01"
}
```

Required pong fields:
- `type` = `"pong"`
- `protocol_version`
- `agent_id`

### 4.5 Observation ack payload (server -> client)

```json
{
  "type": "ack",
  "protocol_version": "roomzero.unreal.v1",
  "kind": "observation",
  "agent_id": "rz-01",
  "created_at": "2025-01-01T12:00:02+00:00"
}
```

Required fields:
- `type` = `"ack"`
- `protocol_version`
- `kind` = `"observation"`
- `agent_id`
- `created_at` (ISO datetime string)

### 4.6 Error payloads (server -> client)

Unknown message type:
```json
{
  "type": "error",
  "protocol_version": "roomzero.unreal.v1",
  "error": "unknown_message_type"
}
```

Missing observation event:
```json
{
  "type": "error",
  "protocol_version": "roomzero.unreal.v1",
  "error": "missing_event"
}
```

Malformed or invalid payload:
```json
{
  "type": "error",
  "protocol_version": "roomzero.unreal.v1",
  "error": "invalid_payload"
}
```

Required fields:
- `type` = `"error"`
- `protocol_version`
- `error` (stable string code)

Known stable error codes (current):
- `unknown_message_type`
- `missing_event`
- `invalid_payload`

## 5) Known stable string/enum values

- `protocol_version`: `roomzero.unreal.v1`
- Message `type` values in this contract:
  - `command`
  - `observation`
  - `ack`
  - `pong`
  - `error`
- Ack `kind`:
  - `observation`
- Error codes:
  - `unknown_message_type`
  - `missing_event`
  - `invalid_payload`

## 6) Compatibility rules (v1)

Consumers should:
- verify `protocol_version == "roomzero.unreal.v1"` before acting on payloads.
- route behavior by `type`.
- ignore unknown additive fields safely (forward-compatible extension behavior).
- treat dynamic timestamps (`updated_at`, `created_at`) as runtime-generated values.
- consider server-provided state the authoritative source on connection establishment.

Server-side v1 stability guarantees:
- Existing required fields and stable literal values above must not be removed or renamed in `roomzero.unreal.v1`.
- Existing message types and error codes listed above must remain stable for v1 consumers.

Allowed non-breaking v1 changes:
- adding optional fields
- adding new message types that old clients may ignore safely
- adding new error codes while preserving existing ones

Breaking changes requiring a new protocol version:
- changing/removing required fields
- changing semantic meaning of stable literals (`type`, `kind`, error codes)
- changing endpoint contract behavior in a way that breaks existing v1 clients

## 7) Safe-fail guidance

- Clients may receive unknown fields from newer server versions; ignore values that are not explicitly required.
- If `protocol_version` does not match, the client should reject the payload and close or restart the session.
- If the server returns an error response, the client should treat the session as degraded but can remain connected for future valid messages.
- `payload` fields are additive and may be extended in future versions.

## 8) What future versions must not break

Future protocol versions must preserve:
- explicit protocol version signaling in every contract payload path
- deterministic ack/error structures for safety-critical handling
- stable agent identity routing (`agent_id`) across state/command/observation flows
- ability for clients to reject incompatible protocol versions safely
