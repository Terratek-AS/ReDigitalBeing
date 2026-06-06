# TODO - Milestone M2: RoomZero research platform MVP (SQLite parallel layer)

## M1.1 runtime hardening implementation tracker (current task)
- [x] Review runtime bridge files and tests
- [x] Draft and confirm implementation plan with maintainer
- [ ] Implement main.py hardening updates
- [ ] Expand ws unreal tests for M1.1
- [ ] Run compile/test/compose validation commands
- [ ] Finalize TODO runtime hardening checklist updates

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
