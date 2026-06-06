# RoomZero

## First Page — Release Overview

**RoomZero** is a local-first research platform for building persistent digital-being simulations with strong safety controls and transparent workflows.

This release introduces the first digital being, **Eir**, with:
- persistent memory layers
- persona continuity and emotional state modeling
- FastAPI + CLI interfaces for testing and operations
- structured research/testing pipelines
- safety boundaries and ethical constraints by default

Repository: https://github.com/Terratek-AS/ReDigitalBeing

## Project Description

RoomZero is a research prototype for a persistent digital being simulation system.  
Phase 1 creates the first digital being, **Eir**, with local-first memory, persona continuity, emotional state simulation, CLI/API interfaces, and safety boundaries.

## Strategic Direction

RoomZero should evolve as a local-first, testable, ethically governed simulation laboratory where Unreal/MetaHuman acts as the embodiment layer, while the core value lives in the research, event, audit, intelligence, and knowledge architecture behind it.

## Important Ethical Warning

RoomZero does **not** claim true biological consciousness or scientifically proven sentience.  
Eir is a software simulation designed for research into:
- memory persistence
- personality continuity
- stateful interaction
- safe and controllable behavior

Use responsibly, especially when handling personal or sensitive data.

### MetaHuman / Unreal license + AI-use guardrail

MetaHuman may be used as a visual avatar/presentation layer only. MetaHuman assets, animation curves, rendered outputs, facial/motion data, or derived datasets must not be used to train, test, benchmark, evaluate, or enhance AI/ML/neural-network systems.

Additional policy requirements:
- MetaHuman license review is mandatory before commercial release, paid distribution, enterprise use, or public product launch.
- Unreal/MetaHuman visual presentation must remain strictly separated from RoomZero cognition, training, evaluation, simulation research datasets, and knowledge-base data.
- AI research/testing must use original data, user-owned data, synthetic data created independently of MetaHuman assets, or separately licensed datasets.

## Features (Phase 1)

- FastAPI backend
- CLI chat mode
- Persistent persona, memory, and emotional state
- Conversation logging
- Safety filtering and boundaries
- Local fallback response mode
- Optional OpenAI API mode using `.env`
- Modular architecture for future upgrades (vector DB/graph memory)

## Project Structure

```text
RoomZero/
  README.md
  requirements.txt
  .env.example
  .gitignore
  install.ps1
  run.ps1
  app/
    main.py
    cli.py
    config.py
    models.py
    persona.py
    memory.py
    state.py
    safety.py
    llm.py
    logger.py
  data/
    persona/eir.json
    state/eir_state.json
    memory/episodic.json
    memory/semantic.json
    memory/procedural.json
    logs/conversations.json
  tests/
    test_memory.py
    test_safety.py
```

## Install (Windows PowerShell)

From the `RoomZero` directory:

```powershell
.\install.ps1
```

Manual equivalent:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run FastAPI Server

```powershell
.\run.ps1
```

Manual equivalent:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then open:
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Docker Runtime (M2.1.7)

Docker support is additive and does not replace the local `run.ps1` / uvicorn workflow.

### Files

- `RoomZero/Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `.env.example`

### Platform DB path in Docker

Docker compose sets:

- `ROOMZERO_PLATFORM_DB_PATH=/app/data/platform/platform.sqlite`

A named volume is mounted to:

- `/app/data/platform`

Local default path (when no `ROOMZERO_PLATFORM_DB_PATH` is set) is:

- `RoomZero/data/platform/platform.sqlite`

This keeps SQLite runtime writes out of tracked repo files and avoids repeated dirty Git state.

### Build and run

From repository root:

```powershell
docker compose build
docker compose up -d
```

Verify:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/ui`

> Note: A running Docker daemon is required for `docker compose build`, `docker compose up -d`, and `docker compose logs`. If Docker is unavailable in your environment, use `docker compose config` to validate the compose syntax before you run the container.

Logs:

```powershell
docker compose logs
```

Stop:

```powershell
docker compose down
```

## Build Windows Installer

### 1) Prepare environment

```powershell
.\install.ps1 -WithBuilder
```

### 2) Build packaged executable

```powershell
.\build_installer.ps1
```

This generates:

- `dist\RoomZero.exe`

### 3) Build Setup installer (.exe)

Install [Inno Setup](https://jrsoftware.org/isinfo.php), then run:

```powershell
iscc .\installer\RoomZero.iss
```

This generates:

- `dist\installer\RoomZero-Setup.exe`

You can distribute `RoomZero-Setup.exe` as the Windows installer.

## Run CLI Chat

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.cli
```

## CI and validation

The repository includes GitHub Actions workflows at `.github/workflows/ci.yml` and `.github/workflows/codeql.yml`.

The CI workflow is configured for pushes to `main`, `develop`, and `blackboxai/**` branches.

Validation tests for RoomZero are:
- `python -m pytest -q`
- `python RoomZero/scripts/ws_unreal_smoke.py --agent-id rz-smoke`
  - expected pass output: `[smoke] completed successfully`
  - if Unreal token auth is enabled: set `ROOMZERO_WS_TOKEN` or pass `--token`
- `powershell -ExecutionPolicy Bypass -File .\scripts\verify.ps1`
- `powershell -ExecutionPolicy Bypass -File .\build_installer.ps1`

Dependabot configuration lives in `.github/dependabot.yml`.

## Codacy / Static Analysis (Windows + WSL)

The Codacy CLI and some static-analysis tools are not supported natively on Windows without WSL. Two recommended approaches:

- **Run Codacy CLI in WSL (local):**
  1. Install WSL and a Linux distro (example on Windows 10/11):

    ```powershell
    wsl --install -d ubuntu
    ```

  2. Open the installed distro and install required packages:

    ```bash
    sudo apt update && sudo apt install -y openjdk-11-jre-headless curl unzip
    ```

  3. Follow Codacy's official CLI install instructions inside WSL (or use the distro package recommended by Codacy). Once installed, run the analysis from the repository root mounted in WSL:

    ```bash
    # Example (replace with Codacy CLI's actual command from their docs)
    codacy analyze --project .
    ```

- **Use CI / GitHub Actions (recommended for automation):**
  - Add a workflow that runs the Codacy analysis or other scanners (e.g., Trivy for vulnerabilities) so analysis runs consistently in CI regardless of developer OS.
  - If you want, I can add a GitHub Actions workflow that runs Codacy (or Trivy) on every push/PR — tell me which scanner you'd like wired into CI and I will add it.

Notes:
- After adding or updating dependencies (requirements.txt, package.json, etc.), run a vulnerability scan (Trivy or similar) before merging.
- If you need exact Codacy CLI install commands or an automated Action, I can add them once you confirm which Codacy integration you prefer.

## OpenAI API Key (Optional)

1. Copy `.env.example` to `.env`
2. Add your key:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

If no key is present, RoomZero uses local fallback responses.

## API Endpoints

Core:
- `GET /health`
- `GET /persona`
- `GET /state`
- `POST /chat`
- `POST /memory`
- `GET /memory/recent`
- `GET /logs/recent`
- `POST /admin/shutdown-safe-mode`

Research Network + Testing:
- Testers:
  - `POST /testers/invite`
  - `POST /testers/register`
  - `GET /testers`
  - `GET /testers/{tester_id}`
  - `POST /testers/{tester_id}/deactivate`
- Research Questions:
  - `POST /research/questions`
  - `GET /research/questions`
  - `GET /research/questions/{question_id}`
  - `POST /research/questions/{question_id}/answer`
  - `POST /research/questions/{question_id}/approve`
  - `POST /research/questions/{question_id}/reject`
  - `GET /research/knowledge`
  - `GET /research/knowledge/search`
- Sources:
  - `POST /sources/submit`
  - `GET /sources/queue`
  - `POST /sources/{source_id}/approve`
  - `POST /sources/{source_id}/reject`
  - `GET /sources/approved`
- Feedback:
  - `POST /feedback/session`
  - `GET /feedback`
  - `GET /feedback/stats`
- Continuous Research Jobs (manual/local mode):
  - `POST /research/jobs`
  - `GET /research/jobs`
  - `POST /research/jobs/{job_id}/run`
  - `POST /research/jobs/{job_id}/pause`
  - `POST /research/jobs/{job_id}/activate`

## Behavior Rules in Chat Flow

When a user message arrives:
1. Load persona (Eir)
2. Load recent memories
3. Load emotional state
4. Apply safety checks
5. Build system context
6. Use OpenAI mode if configured, else local fallback mode
7. Log conversation
8. Update emotional state slightly
9. Store new memory **only** when user explicitly says “remember” or `/memory` is called

## RoomZero Research Network

RoomZero now supports an invite-based research and beta-testing layer for Eir while keeping core persona, personal memory, and approved knowledge protected.

### Invite-based testing

Roles:
- observer: chat
- tester: chat, submit_feedback
- researcher: chat, submit_feedback, submit_research_question, submit_source
- reviewer: researcher permissions + review_research + approve_sources
- admin: full permissions

Testers are managed via invite codes and consent-based registration. Tester messages can be tracked without automatically writing into personal memory.

### Research question workflow

1. Submit research question (`submitted`)
2. Review and answer (`under_review` / `answered`)
3. Approve to move summary/answer into approved knowledge (`approved`)
4. Or reject/archive (`rejected` / `archived`)

Unreviewed questions and answers stay in queue and are not treated as approved knowledge.

### Source approval workflow

1. Submit source into queue (`submitted`)
2. Reviewer evaluates reliability and relevance
3. Approve into approved sources (`approved`) or reject (`rejected`)
4. Optional `needs_review` status for triage

Reliability score guidance:
- peer-reviewed papers: 9–10
- official docs: 8–10
- university/research institutions: 8–10
- reputable technical articles: 6–8
- blogs/opinions: 3–6
- unknown sources: 1–4

### Feedback workflow

Session feedback captures realism/coherence/memory/emotional presence/ethical safety/usefulness/uncanny/trust scores plus free text and suggestions. Stats endpoints summarize aggregate signals for iterative model behavior improvements.

### Continuous Research Update Loop (manual/local mode)

Research jobs can be created and run locally to generate structured placeholder tasks/questions for reviewers, without fabricating external findings.

Current mode:
- no external API calls yet
- generates safe placeholder research questions
- updates job run timestamps/status lifecycle

Planned connectors:
- arXiv, PubMed, Semantic Scholar, GitHub, official docs, RSS, and curated manual source lists

### Privacy and safety defaults

- local-first JSON storage
- no direct tester edits to core persona/memory/approved knowledge
- reviewer-controlled promotion into approved knowledge
- explicit consent required for tester registration and sensitive memory flows

## Unreal WebSocket Protocol (M1.2)

RoomZero exposes an Unreal-focused WebSocket bridge for local-first agent embodiment integration.

### Endpoints

- WebSocket connect: `ws://127.0.0.1:8000/ws/unreal/{agent_id}`
- State snapshot (REST): `GET /ws/unreal/state/{agent_id}`
- Send command to agent (REST): `POST /ws/unreal/command/{agent_id}`
- Observation list (REST): `GET /ws/unreal/observations`

`agent_id` is the canonical agent key for state/commands/observations.

### Optional auth token

If `ROOMZERO_UNREAL_TOKEN` is unset, Unreal routes are public for local development.

If set, token is required for:
- `POST /ws/unreal/command/{agent_id}`
- `WS /ws/unreal/{agent_id}`

Accepted token inputs:
- query string: `?token=...`
- header: `X-RoomZero-Unreal-Token: ...`
- header: `Authorization: Bearer ...`

### Protocol version

Current expected value: `"roomzero.unreal.v1"`.

All bridge model payloads include `protocol_version` and Unreal clients should verify it on every received message before processing.

### Initial WebSocket state payload

Immediately after connect, backend sends current agent state:

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

Then backend sends a greeting command payload (`type = "command"`).

### Command message shape (backend -> Unreal)

Commands are sent over WS and accepted via REST enqueue/broadcast path:

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

Notes:
- `command` is required.
- `text`, `emotion`, `animation`, `duration_seconds` are optional and command-specific.

### Observation event shape (Unreal -> backend)

Send observations over WS with message `type = "observation"`:

```json
{
  "type": "observation",
  "event": "player_entered_room",
  "payload": {
    "distance": 2.4
  }
}
```

Backend stores observation with server timestamp and returns:

```json
{
  "type": "ack",
  "protocol_version": "roomzero.unreal.v1",
  "kind": "observation",
  "agent_id": "rz-01",
  "created_at": "2025-01-01T12:00:02+00:00"
}
```

If `event` is missing/empty, backend responds with:

```json
{
  "type": "error",
  "protocol_version": "roomzero.unreal.v1",
  "error": "missing_event"
}
```

### Ping / pong behavior

Unreal may send:

```json
{ "type": "ping" }
```

Backend responds:

```json
{
  "type": "pong",
  "protocol_version": "roomzero.unreal.v1",
  "agent_id": "rz-01"
}
```

### Unknown/invalid message handling

Unknown message type returns safe error payload:

```json
{
  "type": "error",
  "protocol_version": "roomzero.unreal.v1",
  "error": "unknown_message_type"
}
```

Additional safety behaviors:
- token failure on WS connect closes socket with code `1008`
- command path/body `agent_id` mismatch returns HTTP 400
- malformed observation payload defaults to `{}` for `payload` if non-object

### Unreal Integration Quick Guide

Protocol contract reference:
- `docs/unreal_ws_contract.md` (schema-focused contract for `roomzero.unreal.v1`)

1. Start backend (`.\run.ps1` or uvicorn).
2. Unreal connects a WebSocket client to:
   - `ws://127.0.0.1:8000/ws/unreal/{agent_id}`
   - add token in query/header if enabled.
3. On connect:
   - read initial `AgentState`
   - read greeting/queued `command` messages
   - verify `protocol_version == "roomzero.unreal.v1"` before handling.
4. Send world observations as `type: "observation"` messages.
5. Listen continuously for command messages and map them to animation/audio/behavior.
6. Optionally send periodic `ping` and verify `pong`.

Blueprint/C++ notes:
- Keep a small dispatcher keyed by `type` (`command`, `ack`, `pong`, `error`, state payload).
- Normalize numeric fields from JSON (`awareness`, `trust`, `duration_seconds`) with clamping.
- Treat unknown fields as forward-compatible extensions; ignore safely.
- Reconnect with backoff and re-read initial state after reconnect.

Local testing:
- Run automated test coverage:
  - `python -m pytest -q RoomZero/tests/test_ws_unreal.py`
- Use smoke client:
  - `python RoomZero/scripts/ws_unreal_smoke.py --agent-id rz-smoke`
  - optional token via env:
    - `set ROOMZERO_WS_TOKEN=your_token_here` (Windows cmd)
- Inspect observations:
  - `GET http://127.0.0.1:8000/ws/unreal/observations`

CI/local validation note:
- Keep smoke execution local/controlled by running backend in the same job/session, then executing:
  - `python RoomZero/scripts/ws_unreal_smoke.py --agent-id rz-smoke`
- This avoids secret requirements when Unreal token auth is disabled for CI smoke scope.
- If token auth is enabled in CI, provide token via ephemeral environment variable and never commit credentials.

### Manual Unreal Integration Readiness Checklist

Backend start command:
- `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`

WebSocket smoke command:
- `python RoomZero/scripts/ws_unreal_smoke.py --agent-id rz-smoke`

Expected smoke output (high level):
- Connected to WS endpoint
- Received initial state with `protocol_version=roomzero.unreal.v1`
- Received greeting command (`type=command`)
- Ping sent and pong received
- Observation sent and observation ack received
- Clean close/disconnect

Common failure causes:
- Wrong endpoint path or port
- Backend not running
- token set in backend but missing/incorrect in client
- firewall/proxy interference on localhost WS
- invalid JSON message shape in client sender

Protocol version verification:
- Confirm every inbound payload includes `protocol_version`
- Confirm value equals exactly `roomzero.unreal.v1`
- If mismatched, log and drop payload (do not execute command blindly)

## Project Progress

| Milestone | Status | Progress |
|---|---|---:|
| M0 Repository Stabilization | ⚠️ Active | `██████░░░░ 60%` |
| M1 PWA / Mobile Launcher | ✅ Completed | `██████████ 100%` |
| M1.2 Unreal Integration Readiness | ✅ Completed | `██████████ 100%` |
| M1.3 Contract Fixtures & Protocol Stability | ✅ Completed | `██████████ 100%` |
| M1.4 Handshake / Schema Hardening | ✅ Completed | `██████████ 100%` |
| M1.5 UI / Product Polish | ⏳ In progress | `██████░░░░ 60%` |
| M2 SQLite Platform Layer | ✅ Foundation complete | `████████░░ 80%` |
| M2.1 Public Backend Configuration | ✅ Foundation complete | `████████░░ 80%` |
| M3 Simulation Event Architecture & Real-Time Chamber | ⏳ In progress | `██████░░░░ 60%` |
| M4 Model Adapter & Intelligence Interface | Planned | `░░░░░░░░░░ 0%` |
| M5 Expanded Simulation Data Model | Planned | `░░░░░░░░░░ 0%` |
| M6 Full Simulation Room Console UI | Planned | `░░░░░░░░░░ 0%` |
| M7 MetaHuman / Digital Human Runtime | Future | `░░░░░░░░░░ 0%` |
| M8 Research Knowledge Engine | Future | `░░░░░░░░░░ 0%` |

Progress percentages are milestone-tracking indicators, not release guarantees. Completion requires passing tests, documentation updates, and review.

## Roadmap

### M0 — Repository Stabilization & CI Recovery

Purpose:  
Restore trust in main, resolve failed CI, keep local artifacts out of commits, and maintain a safe development baseline.

Includes:
- Diagnose and fix failed GitHub Actions after PR #25.
- Restore green CI on main.
- Keep runtime artifacts, local data, cache files, logs, and secrets out of commits.
- Document environment-limited checks such as Codacy CLI requiring WSL on Windows.
- Maintain branch discipline and focused PRs.

### M1 — PWA / Mobile Launcher

Purpose:  
Create the first accessible RoomZero shell that can run as a mobile-friendly, installable research interface.

Includes:
- PWA/mobile launcher.
- Service worker.
- Offline fallback.
- GitHub Pages shell.
- Mobile-friendly app entry point.
- Basic app-like launch experience.

### M1.2 — Unreal Integration Readiness

Purpose:  
Make RoomZero ready to communicate with Unreal Engine through a clear WebSocket bridge.

Includes:
- Unreal WebSocket protocol documentation.
- Smoke tooling.
- Initial state payload.
- Command payload.
- Observation payload.
- Ping/pong behavior.
- Error handling.
- Local bridge validation.

### M1.3 — Contract Fixtures & Protocol Stability

Purpose:  
Make the Unreal bridge regression-safe and contract-based.

Includes:
- Protocol contract document.
- JSON fixtures.
- Fixture-backed tests.
- Stable protocol version checks.
- Runtime message examples.

### M1.4 — Handshake / Schema Hardening

Purpose:  
Strengthen Unreal WebSocket safety, compatibility, and negative-path behavior.

Includes:
- Handshake lifecycle clarification.
- JSON schema artifacts.
- Protocol compatibility policy.
- Invalid/non-object payload handling.
- Negative-path WebSocket tests.
- Smoke client hardening.
- Optional token handling documentation.

### M1.5 — UI / Product Polish

Purpose:  
Make RoomZero usable, serious, and understandable for testers, researchers, observers, and admins.

Includes:
- UI/product polish.
- Onboarding.
- Mobile role navigation.
- Role-based entry points.
- Dashboard cards.
- Research-lab visual identity.
- Better empty states.
- Mobile ergonomics.
- Backend/research/simulation/Unreal status indicators.

### M2 — SQLite Platform Layer

Purpose:  
Create the local-first platform database for users, invitations, research, scenarios, knowledge, and auditability.

Includes:
- SQLite platform layer.
- Users.
- Roles.
- Invitations.
- Research questions.
- Comments.
- Simulation scenarios.
- Knowledge entries.
- Audit logs.
- Permission checks.

Likely platform tables:
- `users`
- `roles`
- `invitations`
- `research_questions`
- `comments`
- `simulation_scenarios`
- `knowledge_entries`
- `audit_logs`
- `sources`

### M2.1 — Public Backend Configuration & Deployment Model

Purpose:  
Make RoomZero deployable and understandable as a public-facing app with a backend connection model.

Includes:
- Public backend configuration.
- CORS.
- Deployment documentation.
- Root README.
- GitHub Pages-to-backend connection model.
- Unreal integration readiness docs.
- Smoke tooling.

### M3 — Simulation Event Architecture & Real-Time Chamber

Purpose:  
Create the core event layer that lets RoomZero behave like a live simulation laboratory.

Status: **In progress (not complete).**

Includes:
- Real-time chamber layer using WebSocket or SSE.
- Live simulation room events.
- Experiment run streaming.
- Activity/event bus.
- Internal simulation event schema.
- Unreal observation → simulation event mapping.
- Audit/log traceability.
- Event lifecycle documentation.

Conceptual event flow:

External input / Unreal observation  
→ normalized simulation event  
→ audit/log trace  
→ chamber state update  
→ optional agent response  
→ streamed to UI / client

Proposed simulation event shape:

```json
{
  "event_id": "evt_...",
  "event_type": "unreal.observation.player_entered_room",
  "source": "unreal.websocket",
  "agent_id": "rz-01",
  "scenario_id": null,
  "simulation_id": null,
  "payload": {},
  "status": "accepted",
  "severity": "info",
  "protocol_version": "roomzero.unreal.v1",
  "created_at": "2026-06-06T16:00Now I need to update RoomZero/README.md with the same advanced roadmap content. Let me create the full updated version.
