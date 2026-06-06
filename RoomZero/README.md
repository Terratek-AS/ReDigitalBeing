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

## Roadmap

### Phase 1B
- richer emotional modeling
- confidence/relevance scoring improvements
- better semantic extraction and tagging
- memory decay + reinforcement mechanics
- optional ChromaDB/Qdrant adapters

### Phase 1C
- voice pipeline (STT/TTS)
- Unreal Engine bridge
- sensor/event input adapters
- multi-agent room simulation primitives

## M4 Roadmap: Simulation Intelligence & Digital Human Layer (Planning-Only)

### M4 objective

Define a future planning blueprint for the **Simulation Intelligence & Digital Human Layer** so M2/M3 architecture decisions remain forward-compatible. M4 in this phase is documentation-only and creates no implementation obligation in the current cycle.

### What M4 is

- A planning framework to evolve approved research scenarios into **controlled simulation runs**
- A design model for repeatable, observable, and auditable simulation execution
- A specification direction for agent behavior orchestration via explicit agent profiles
- A governance roadmap for ethical reasoning tests, risk gating, and human oversight
- A presentation-layer roadmap for Unreal/MetaHuman as avatar visualization only

### What M4 is not

- Not a runtime implementation milestone in this task
- Not a bypass of M2.1.4 deployment ownership or M2.2 Research MVP Foundation
- Not a replacement for M3 event/simulation transport hardening
- Not a claim of real consciousness or proven sentience
- Not permission to use MetaHuman-derived assets/data for AI/ML training, testing, benchmarking, evaluation, or enhancement

### M4 dependencies

- M2.1.4 deployment ownership and canonical URL authority completed
- M2.2 research workflows stabilized with governance and auditability
- M3 simulation-event architecture established (schema + transport + audit trail)
- Stable role/approval model for research-to-simulation conversion
- Baseline observability and incident-response readiness

### Simulation runtime roadmap

- Define simulation run lifecycle:
  - draft -> approved -> scheduled -> running -> paused -> completed -> archived
- Introduce deterministic configuration snapshots per run:
  - scenario version
  - agent profile version
  - memory-state snapshot reference
  - safety policy version
- Add replayability primitives:
  - event log stream
  - seed/config capture
  - run outcome digest
- Enforce audit trace for all control-plane actions and state transitions

### Agent profile roadmap

- Define versioned agent profile schema:
  - role
  - objectives
  - behavioral constraints
  - response style boundaries
  - tool/action permissions
- Separate profile policy from runtime memory content
- Require profile approval workflow for medium/high-impact behavior changes
- Track profile-to-run linkage for post-run analysis and reproducibility

### Memory state roadmap

- Introduce simulation memory-state abstraction:
  - working memory
  - episodic simulation memory
  - scenario-bound semantic memory overlays
- Ensure memory states are:
  - inspectable
  - reversible
  - environment-scoped
- Maintain strict separation from private user data and production personal memory stores
- Add snapshot/restore controls for repeatable testing and controlled rollback

### Metrics and observation roadmap

- Define mandatory telemetry for each controlled simulation run:
  - run identifiers
  - scenario/profile versions
  - timing and transition events
  - safety events and override events
- Define synthetic consciousness markers and consciousness-adjacent behavioral markers as research observables (not consciousness claims)
- Add observer dashboards for run health, drift indicators, and policy violations
- Require exportable audit summaries for review and governance sign-off

### Ethical simulation gate

- Require ethical risk classification before run approval:
  - low / medium / high
- Require explicit ethical approval and human oversight for medium/high-risk scenarios
- Block or flag harmful real-world operational simulation behavior
- Require clear stop/abort controls and post-run incident review for flagged events

### Unreal/MetaHuman presentation layer

- Use Unreal/MetaHuman as visual avatar/presentation layer only
- Keep cognition simulation, agent behavior logic, evaluation pipelines, and knowledge/research datasets outside Unreal/MetaHuman asset domain
- Ensure transport boundary between simulation runtime and visual renderer is contract-based and auditable
- Restrict visual layer to presentation, animation, and user-facing embodiment experiences only

### Future database models

(Planning targets only; no schema changes in this task)

- `simulation_runs`
- `simulation_run_events`
- `agent_profiles`
- `agent_profile_versions`
- `memory_state_snapshots`
- `memory_state_transitions`
- `simulation_observations`
- `simulation_metric_series`
- `ethical_reviews`
- `ethical_review_decisions`
- `simulation_gate_decisions`
- `visual_session_links`
- `run_artifact_index`

### Future APIs

(Planning targets only; no API implementation in this task)

- Simulation runs:
  - `POST /platform/simulations/runs`
  - `GET /platform/simulations/runs`
  - `GET /platform/simulations/runs/{run_id}`
  - `POST /platform/simulations/runs/{run_id}/start|pause|resume|stop`
- Agent profiles:
  - `POST /platform/simulations/agent-profiles`
  - `GET /platform/simulations/agent-profiles`
  - `POST /platform/simulations/agent-profiles/{id}/versions`
- Memory state:
  - `POST /platform/simulations/memory-snapshots`
  - `POST /platform/simulations/runs/{run_id}/restore-memory`
- Observation/metrics:
  - `GET /platform/simulations/runs/{run_id}/events`
  - `GET /platform/simulations/runs/{run_id}/metrics`
- Ethical gate:
  - `POST /platform/simulations/ethics/review`
  - `POST /platform/simulations/runs/{run_id}/gate-decision`

### Future UI

(Planning targets only; no frontend implementation in this task)

- Simulation Control Center
- Agent Profile Manager
- Memory State Inspector + Snapshot Diff Viewer
- Observation & Metrics Console
- Ethical Gate Queue + Decision Workspace
- Run Replay/Audit Timeline Viewer
- Visual Session Monitor (Unreal/MetaHuman presentation linkage only)

### Testing checklist

Docs/planning targets for future implementation:

- Unit tests for run lifecycle state machine transitions
- Contract tests for event schemas and API payloads
- Deterministic replay tests for repeatable run verification
- Access-control tests for simulation control and ethical gate actions
- Safety policy tests for blocked/flagged behavior pathways
- Audit integrity tests (completeness, tamper-evidence assumptions, traceability)
- Renderer-boundary tests confirming no prohibited data crossing into MetaHuman pipelines

### Safety constraints

- No real-consciousness claims in product or research outputs
- Use terms such as:
  - synthetic consciousness markers
  - consciousness-adjacent behavioral markers
  - cognition simulation
- Medium/high-risk scenarios require ethical approval and active human oversight
- Harmful real-world operational simulation behavior must be blocked or flagged
- Emergency stop and post-incident review process required for flagged runs

### Licensing constraints

- MetaHuman may only be used as a visual avatar/presentation layer
- MetaHuman assets, animation curves, rendered outputs, facial/motion data, or derived datasets must not be used for AI/ML training, testing, benchmarking, evaluation, or enhancement
- RoomZero cognition, training, evaluation, simulation research datasets, and knowledge-base data must remain separated from Unreal/MetaHuman assets
- License/compliance review is required before commercial release, paid distribution, enterprise deployment, or public launch using Unreal/MetaHuman presentation components

### Implementation order

1. Complete M2.1.4 deployment ownership authority
2. Complete M2.2 research MVP governance and lifecycle hardening
3. Complete M3 event architecture and simulation transport foundation
4. Implement M4 simulation runtime control plane (minimal vertical slice)
5. Add agent profile versioning and approval workflows
6. Add memory snapshot/restore and observability primitives
7. Add ethical gate enforcement for medium/high-risk scenarios
8. Integrate Unreal/MetaHuman presentation linkage under strict boundary controls
9. Expand validation, audit exports, and operational readiness checks

### Risks

- Scope creep risk if planning language is interpreted as immediate implementation mandate
- Governance risk if ethical gate is bypassed for medium/high-risk runs
- Auditability risk if replay/event capture is incomplete
- Data-boundary risk between cognition simulation data and visual asset ecosystems
- Compliance risk from improper MetaHuman/Unreal usage in AI/ML evaluation flows
- Terminology risk from over-claiming consciousness rather than measured behavioral markers

### Next recommended milestone after M4

**M4.1 Controlled Simulation Pilot (post-M2/M3 completion)**

- Run a constrained internal pilot with approved low-risk scenarios
- Validate repeatability, observability, auditability, and ethical gate operations
- Validate boundary-safe Unreal/MetaHuman presentation workflow
- Publish governance evidence package and readiness decision for wider simulation rollout

## Execution Plan Snapshot (Windows Install + Advanced UI/UX)

This snapshot mirrors the actionable checklist in `TODO.md` for delivery readiness.

### Advanced UI/UX workstreams
- UX architecture and navigation
  - define primary user journeys
  - reduce action depth for tester/research/feedback/source tasks
  - improve section hierarchy and contextual actions
- Visual design system consistency
  - standard spacing/typography/component hierarchy
  - semantic status colors and clear button hierarchy
- Interaction quality
  - loading, empty, success, and error states
  - inline validation and clearer user feedback loops
- Accessibility and responsiveness
  - keyboard/focus behavior, semantic landmarks, contrast checks
  - mobile-first usability for quick admin/testing actions
- Functional wiring and acceptance
  - ensure dashboard controls map cleanly to existing API endpoints
  - verify critical flows can be completed from `/ui` without relying on `/docs`

### Windows installer hardening workstreams
- Build chain verification
  - run and validate full chain:
    - `.\install.ps1 -WithBuilder`
    - `.\build_installer.ps1`
    - `iscc .\installer\RoomZero.iss`
- Installer QA on Windows
  - clean-machine install validation
  - first-run checks (`/health`, `/ui`)
  - uninstall and upgrade-path behavior checks
- Trust and release readiness
  - SmartScreen/signing expectations for unsigned builds
  - rollback guidance and release-note discipline
- Acceptance criteria
  - non-dev installability from docs
  - reproducible build/install flow by another team member
  - checklist/log evidence for final verification

## Safety and Data Defaults

- Local data storage by default (JSON files under `data/`)
- No hardcoded secrets
- Human override is respected
- Eir avoids claims of proven consciousness
- Sensitive memory should require explicit user consent

