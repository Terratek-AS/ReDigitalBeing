# TODO - Milestone M2: RoomZero research platform MVP (SQLite parallel layer)

## M4.1 — Admin Research Dashboard backend foundation
- [x] Backend-first implementation completed; no Admin UI/M4.2 work started.
- [x] Exact files changed:
  - [x] `RoomZero/app/db.py`
  - [x] `RoomZero/app/models.py`
  - [x] `RoomZero/app/platform_store.py`
  - [x] `RoomZero/app/main.py`
  - [x] `RoomZero/tests/test_m4_admin_research_dashboard.py`
  - [x] `RoomZero/TODO.md`
  - [x] `README.md`
- [x] Migration notes:
  - [x] Added idempotent helpers using `PRAGMA table_info` and `ALTER TABLE ADD COLUMN` only when missing.
  - [x] No destructive migrations, table rewrites, data loss, or new dependencies.
  - [x] `research_questions` M4 columns added/verified: `risk_level`, `possible_harm`, `mitigation_notes`, `human_oversight_required`, `approval_status`, `reviewer_notes`, `priority`, `reviewed_by`, `reviewed_at`.
  - [x] `simulation_scenarios` M4 columns added/verified: `environment_conditions`, `input_variables`, `expected_observations`, `metrics_to_collect`, `result_summary`, `status`, `risk_level`, `possible_harm`, `mitigation_notes`, `human_oversight_required`, `approval_status`, `reviewer_notes`.
- [x] New/extended API endpoints:
  - [x] `GET /platform/research/questions` with `status`, `risk_level`, `author`, `priority_min` filters.
  - [x] `PATCH /platform/research/questions/{question_id}/review`
  - [x] `POST /platform/research/questions/{question_id}/approve`
  - [x] `POST /platform/research/questions/{question_id}/reject`
  - [x] `POST /platform/research/questions/{question_id}/archive`
  - [x] `POST /platform/research/questions/{question_id}/prioritize`
  - [x] `POST /platform/research/questions/{question_id}/convert-scenario` extended with M4 scenario/review fields.
  - [x] `GET /platform/scenarios` with `status`, `risk_level`, `research_question_id` filters.
  - [x] `PATCH /platform/scenarios/{scenario_id}`
  - [x] Existing generic `POST /platform/research/questions/{question_id}/status` preserved.
- [x] New audit action names:
  - [x] `research_question_created`
  - [x] `question_approved`
  - [x] `question_rejected`
  - [x] `question_archived`
  - [x] `question_prioritized`
  - [x] `question_reviewer_notes_changed`
  - [x] `question_converted_to_scenario`
  - [x] `scenario_updated`
- [x] Known limitations:
  - [x] Admin UI is not implemented in M4.1; next milestone is M4.2.
  - [x] Actor identity remains `actor_id` based, not real authentication.
  - [x] Stateful JSON/SQLite-backed tests should be run sequentially.
  - [x] Existing Starlette/httpx deprecation warning remains upstream.
- [ ] Validation commands:
  - [x] `python -m compileall -q RoomZero` -> PASS
  - [x] `python -m pytest -q` -> PASS (`46 passed`, 1 Starlette/httpx deprecation warning)
  - [x] `python -m pytest -q RoomZero/tests` -> PASS (`46 passed`, 1 Starlette/httpx deprecation warning)
  - [x] `python -m pytest -q RoomZero/tests/test_m2_platform.py` -> PASS (`4 passed`, 1 Starlette/httpx deprecation warning)
  - [x] `python -m pytest -q RoomZero/tests/test_m4_admin_research_dashboard.py` -> PASS (`4 passed`, 1 Starlette/httpx deprecation warning)
  - [x] `python -m pytest -q RoomZero/tests/test_ws_unreal.py` -> PASS (`15 passed`, 1 Starlette/httpx deprecation warning)
  - [x] `python -m pytest -q RoomZero/tests/test_api_endpoints.py` -> PASS (`7 passed`, 1 Starlette/httpx deprecation warning)
  - [x] `docker compose -f docker-compose.yml config` -> PASS
  - [x] `docker compose -f docker-compose.yml up --build -d` -> PASS
  - [x] `docker compose -f docker-compose.yml ps` -> PASS (`roomzero-backend` Up, `0.0.0.0:8000->8000/tcp`)
  - [x] Docker `GET /health` -> PASS (`200`)
  - [x] Docker `GET /ui` -> PASS (`200`)
  - [x] Docker `GET /platform/research/questions?actor_id=<valid-admin>` -> PASS (`200`, empty list)
  - [x] Docker `GET /platform/scenarios?actor_id=<valid-admin>` -> PASS (`200`, empty list)
  - [x] `docker compose -f docker-compose.yml logs --tail=80` -> checked; normal startup and successful endpoint requests only.
  - [x] `docker compose -f docker-compose.yml down` -> PASS
- [x] Next recommended milestone:
  - [x] M4.2 Admin Dashboard UI.

## M3.4/M3 final closure proof - 2026-06-07
- [x] Closure status: completed for dependency stabilization, frontend closure evidence, validation matrix, and Docker runtime proof.
- [x] Exact files changed:
  - [x] `RoomZero/TODO.md`
  - [x] `TODO.md` (root helper marked non-active)
  - [x] `RoomZero/requirements.txt` verified already stabilized; no final diff remains.
- [x] Dependency stabilization:
  - [x] Removed duplicate/conflicting pins for `uvicorn`, `pydantic`, `python-dotenv`, and `openai`.
  - [x] Kept newer listed versions: `uvicorn[standard]==0.49.0`, `pydantic==2.13.4`, `python-dotenv==1.2.2`, `openai==2.41.0`.
  - [x] No new dependencies introduced; unrelated packages left unchanged.
- [x] Dependency validation:
  - [x] `python -m pip install -r RoomZero/requirements.txt` -> PASS
  - [x] `python -m pip check` -> PASS (`No broken requirements found.`)
- [x] Frontend closure evidence:
  - [x] `escapeHtml` in `RoomZero/app/static/app.js` is exact.
  - [x] No malformed template literals, broken quote escaping, or JavaScript syntax errors found.
  - [x] `node --check RoomZero/app/static/app.js` -> PASS
  - [x] Required UI IDs present in `RoomZero/app/static/index.html`: `simulation-events-output`, `event-review-note-input`, `btn-save-event-review-note`, `btn-clear-event-review-notes`, `event-review-notes-output`, `review-audit-panel`, `review-audit-status`, `review-audit-action`.
  - [x] Required CSS classes present in `RoomZero/app/static/styles.css`: `.review-audit-panel`, `.review-audit-header`, `.review-audit-title`, `.review-audit-status`, `.review-audit-action`.
  - [x] `innerHTML` use limited to Review Audit action with `escapeHtml`; `textContent`/`pretty()` used where HTML rendering is unnecessary.
- [x] Validation commands:
  - [x] `python -m compileall -q RoomZero` -> PASS
  - [x] `python -m pytest -q` -> PASS (`42 passed`, 1 Starlette/httpx deprecation warning)
  - [x] `python -m pytest -q RoomZero/tests` -> PASS (`42 passed`, 1 Starlette/httpx deprecation warning)
  - [x] `python -m pytest -q RoomZero/tests/test_ws_unreal.py` -> PASS (`15 passed`, 1 Starlette/httpx deprecation warning)
  - [x] `python -m pytest -q RoomZero/tests/test_api_endpoints.py` -> PASS (`7 passed`, 1 Starlette/httpx deprecation warning)
  - [x] `python -m pytest -q RoomZero/tests/test_research_jobs.py RoomZero/tests/test_m2_platform.py` -> PASS (`7 passed`, 1 Starlette/httpx deprecation warning)
  - [x] `docker compose -f docker-compose.yml config` -> PASS
  - [x] `node --check RoomZero/app/static/app.js` -> PASS
  - [x] No npm commands run; no `package.json` exists at repository root or `RoomZero/package.json`.
- [x] Docker runtime validation:
  - [x] `docker compose -f docker-compose.yml up --build -d` -> PASS
  - [x] `docker compose -f docker-compose.yml ps` -> `roomzero-backend` Up, `0.0.0.0:8000->8000/tcp`.
  - [x] `GET http://127.0.0.1:8000/health` -> `200`, `{"status":"ok","name":"Eir","safe_mode":true}`
  - [x] `GET http://127.0.0.1:8000/ui` -> `200`, HTML length `13747`
  - [x] `GET http://127.0.0.1:8000/ws/unreal/observations` -> `200`, `{"count":0,"items":[]}`
  - [x] `GET http://127.0.0.1:8000/ws/unreal/state/rz-smoke` -> `200`, protocol `roomzero.unreal.v1`, agent `rz-smoke`
  - [x] `docker compose -f docker-compose.yml logs --tail=80` -> checked; normal startup and successful endpoint requests only.
  - [x] No startup errors, import errors, dependency errors, database path errors, static file serving errors, websocket route errors, or unhandled exceptions observed in logs.
  - [x] `docker compose -f docker-compose.yml down` -> PASS
- [x] Smoke test results:
  - [x] Docker `/health` smoke -> PASS (`200`)
  - [x] Docker `/ui` smoke -> PASS (`200`)
  - [x] Docker Unreal observations smoke -> PASS (`200`)
  - [x] Docker Unreal state smoke -> PASS (`200`)
- [x] Remaining risks:
  - [x] Tests share mutable JSON-backed state; avoid running stateful pytest targets concurrently. A concurrent run produced one transient `RoomZero/tests` failure while the same suite passed sequentially.
  - [x] Upstream Starlette/httpx deprecation warning remains; not part of M3.4 closure behavior.
- [x] Next recommended milestone:
  - [x] M3 is clean for closure; next work may proceed to M4 planning only after maintainer approval. Do not start M4 runtime implementation from this closure pass.

## M3.4 — Frontend parity + stabilization (closure)
- [x] Confirm exact safe escaping helper in `RoomZero/app/static/app.js`:
  - [x] `function escapeHtml(value) { const text = String(value ?? ""); return text.replace(/[&<>"']/g, (ch) => \`&#${ch.charCodeAt(0)};\`); }`
- [x] Keep rendering safe:
  - [x] Use `escapeHtml` where HTML rendering is required (Review Audit action).
  - [x] Preserve `textContent`/`pretty()` usage for non-HTML rendering paths.
- [x] Add/verify additive frontend parity sections in `RoomZero/app/static/index.html`:
  - [x] Simulation Events
  - [x] Event Review Notes
  - [x] Review Audit mini-panel
- [x] Complete Review Audit styling in `RoomZero/app/static/styles.css` with existing dark lab aesthetic.
- [x] Preserve existing frontend flow:
  - [x] Simulation Events remain functional
  - [x] Event Review Notes remain functional (save/reload/clear wiring present)
  - [x] Existing dashboard/status behavior preserved
- [x] Validation commands executed:
  - [x] `python -m compileall -q RoomZero` → PASS
  - [x] `python -m pytest -q` → PASS (`42 passed`)
  - [x] `python -m pytest -q RoomZero/tests/test_ws_unreal.py` → PASS (`15 passed`)
  - [x] `python -m pytest -q RoomZero/tests/test_api_endpoints.py` → PASS (`7 passed`)
  - [x] `python -m pytest -q RoomZero/tests/test_research_jobs.py RoomZero/tests/test_m2_platform.py` → PASS (`7 passed`)
  - [x] `docker compose -f docker-compose.yml config` → PASS
- [x] Smoke checks:
  - [x] `GET /health` → PASS (`200`)
  - [x] `GET /ui` → PASS (`200`)
- [x] Environment/tooling limitations captured:
  - [x] `docker compose -f docker-compose.yml up -d roomzero-backend` unavailable locally (Docker daemon not running).
  - [x] Browser automation unavailable (browser tool disabled); interactive browser verification could not be fully automated.
- [x] Files changed for M3.4 closure:
  - [x] `RoomZero/app/static/index.html`
  - [x] `RoomZero/app/static/app.js`
  - [x] `RoomZero/app/static/styles.css`
  - [x] `RoomZero/TODO.md`
- [x] Remaining risks / limitations:
  - [x] Manual in-browser click-through verification should be run when browser tooling is available.
- [x] Next recommended milestone:
  - [x] Continue with M3 transport/schema/doc completion tasks after this frontend stabilization closeout.

## M1.3 Contract Hardening & Integration Fixtures (current task)
- [x] Review runtime bridge files, models, tests, and docs
- [x] Draft and confirm implementation plan with maintainer
- [ ] Add compact Unreal WS contract document (`docs/unreal_ws_contract.md`)
- [ ] Add reusable Unreal WS JSON fixtures (`tests/fixtures/unreal_ws/`)
- [ ] Add fixture-backed protocol stability tests in `tests/test_ws_unreal.py`
- [ ] Harden `scripts/ws_unreal_smoke.py` minimally (env token + clearer errors)
- [ ] Add README note for contract doc + CI/local smoke validation guidance
- [ ] Run validation:
  - [ ] `python -m compileall -q RoomZero`
  - [ ] `python -m pytest -q`
  - [ ] `python -m pytest -q RoomZero/tests/test_ws_unreal.py`
  - [ ] `python RoomZero/scripts/ws_unreal_smoke.py --agent-id rz-smoke`
  - [ ] `docker compose -f docker-compose.yml config`
- [ ] Finalize M1.3 TODO updates and completion report

## M1.4 Unreal WebSocket contract + schema hardening
- [ ] Clarify handshake lifecycle, endpoint format, agent_id routing, v1 compatibility, and error behavior in `RoomZero/docs/unreal_ws_contract.md`
- [ ] Add dependency-free JSON Schema artifacts for Unreal WS messages in `RoomZero/docs/schemas/unreal_ws/`
- [ ] Harden smoke client in `RoomZero/scripts/ws_unreal_smoke.py` with `--expect-protocol`, `--send-unknown-message`, and `--timeout`
- [ ] Add focused websocket negative-path tests in `RoomZero/tests/test_ws_unreal.py`
- [ ] Update `RoomZero/README.md` with smoke validation guidance, backend startup notes, `ROOMZERO_WS_TOKEN`, and expected pass output
- [ ] Validate compileall, full pytest, ws-only pytest, smoke client, and `docker compose config`

## M1.2 Unreal integration readiness tracker (completed baseline)
- [x] Review runtime bridge files, models, tests, and docs
- [x] Draft and confirm implementation plan with maintainer
- [x] Add Unreal protocol documentation and integration guide
- [x] Add standalone Unreal WebSocket smoke client script
- [x] Add manual Unreal integration readiness checklist
- [x] Run compile/test/compose validation commands
- [x] Finalize TODO M1.2 checklist updates

## Planning notice: M4 Simulation Intelligence & Digital Human Layer (future only)

- [ ] M4 is documentation/planning-only in the current cycle.
- [ ] Do not implement M4 runtime/app/backend/frontend/database changes from this TODO.
- [ ] M4 must build on M2/M3 completion and must not bypass M2.1.4 or M2.2.
- [ ] M4 design target: controlled simulation runs that are repeatable, observable, auditable, and ethically gated.
- [ ] Use language such as synthetic consciousness markers and consciousness-adjacent behavioral markers; avoid claims of real consciousness.
- [ ] Unreal/MetaHuman is visual presentation only and must remain separated from cognition/training/evaluation/simulation research datasets.

## 0) Execution tracking for approved scope
- [x] Plan approved by maintainer
- [x] Safe migration path approved
- [x] Dedicated `research_comments` table approved
- [ ] Keep existing JSON flows and endpoints intact
- [ ] Do not remove M1 functionality

## Execution tracking: Unreal MVP WebSocket bridge (approved)
- [x] Plan approved by maintainer
- [x] Additive changes only (no route regressions)
- [x] Update models with reusable Unreal bridge schemas
- [x] Add WebSocket route `/ws/unreal/{agent_id}`
- [x] Add REST routes:
  - [x] `GET /ws/unreal/state/{agent_id}`
  - [x] `POST /ws/unreal/command/{agent_id}`
  - [x] `GET /ws/unreal/observations`
- [x] Add optional token auth for `/ws/unreal/*` routes
- [x] Add per-agent queued command fallback
- [x] Add queued command flush on WebSocket connect
- [x] Cap observation retention to 500
- [x] Implement connect behavior:
  - [x] Accept socket
  - [x] Send current AgentState
  - [x] Send greeting command
- [x] Implement inbound handling:
  - [x] `hello` -> current state
  - [x] `observation` -> store + ack
  - [x] `state_update` -> update + state response
  - [x] `ping` -> pong
  - [x] unknown type -> safe error response
- [x] Add focused tests:
  - [x] default state endpoint
  - [x] websocket initial state
  - [x] websocket greeting command
  - [x] observation ack
  - [x] ping/pong + unknown message safety
  - [x] queue delivery behavior
  - [x] observation cap pruning
- [x] Run validation:
  - [x] `python -m compileall -q RoomZero`
  - [x] `python -m pytest -q`

## 1) Data layer (SQLite + migration/bootstrap)
- [ ] Add SQLite database config path in app config
- [ ] Add DB bootstrap/migration module
- [ ] Validate migration execution and idempotency
- [ ] Tables to create:
  - [ ] `users`
  - [ ] `invitations`
  - [ ] `research_questions`
  - [ ] `research_comments`
  - [ ] `simulation_scenarios`
  - [ ] `knowledge_entries`
  - [ ] `audit_logs`

## 2) Invitation system
- [ ] Invite code generation in SQLite
- [ ] Invite expiration support
- [ ] `invited_by` tracking
- [ ] Invite acceptance workflow
- [ ] Audit log events for create/accept/expire/fail

## 3) User management
- [ ] User registration from invite
- [ ] Role assignment
- [ ] Contributor mapping support (safe compatibility)
- [ ] User listing/retrieval endpoints
- [ ] Audit log events for registration/role changes

## 4) Research platform entities
- [ ] New research question schema and lifecycle:
  - [ ] fields: id/title/description/category/hypothesis/simulation_relevance/ethical_risk/suggested_conditions/status/author/created_at/updated_at/tags
  - [ ] statuses: proposed/approved/testing/completed/archived
- [ ] Submission/edit endpoints (owner-aware)
- [ ] Comment workflow (`research_comments`)
- [ ] Status transition endpoints with role checks
- [ ] Audit log events for submit/edit/comment/status change/approval

## 5) Scenario conversion + knowledge foundation
- [ ] Convert approved research question -> `simulation_scenarios`
- [ ] Scenario fields: purpose/agent_type/environment/variables/metrics/ethical_constraints
- [ ] Knowledge entries linked to questions/scenarios/observations
- [ ] Audit log events for conversion + knowledge creation/updates

## 6) API integration (non-breaking)
- [ ] Add new M2 routes in `app/main.py` (parallel with legacy routes)
- [ ] Add role permission checks for M2 routes
- [ ] Keep all legacy JSON routes untouched and functional
- [ ] Wire `PlatformStore` and SQLite bootstrap into startup path
- [ ] Add admin/research route families:
  - [ ] `/platform/invitations` (create/list/accept)
  - [ ] `/platform/users` (list/get)
  - [ ] `/platform/research/questions` (create/list/get/update/status)
  - [ ] `/platform/research/questions/{id}/comments` (add/list)
  - [ ] `/platform/research/questions/{id}/convert-scenario`
  - [ ] `/platform/scenarios` (list/get)
  - [ ] `/platform/knowledge` (create/list/get)
  - [ ] `/platform/audit` (recent activity)

## 7) Admin + research UI updates
- [ ] Add admin dashboard sections in static UI:
  - [ ] users
  - [ ] invitations
  - [ ] research questions
  - [ ] approvals
  - [ ] recent activity
- [ ] Add research submission UI:
  - [ ] submit
  - [ ] edit own submissions
  - [ ] comment
  - [ ] view status
- [ ] Do not break current role dashboards or M1 install/PWA flow

## 8) Validation required
- [ ] Database migration validation
- [ ] API endpoint testing (new M2 + legacy smoke)
- [ ] Endpoint tests (M2 happy-path + error-path)
- [ ] Startup smoke test
- [ ] Role permission checks
- [ ] Audit log write/read checks
- [ ] Approved question -> scenario conversion test
- [ ] Full test run (`python -m pytest -q RoomZero/tests`)
- [ ] `powershell -ExecutionPolicy Bypass -File RoomZero/scripts/verify.ps1`

## 9) Completion deliverables
- [ ] Final report includes:
  - [ ] changed files
  - [ ] new tables
  - [ ] new API routes
  - [ ] test results
  - [ ] remaining blockers
- [ ] Commit with exact message:
  - [ ] `Implement RoomZero research platform MVP`
