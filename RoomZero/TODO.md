# TODO - Milestone M2: RoomZero research platform MVP (SQLite parallel layer)

## 0) Execution tracking for approved scope
- [x] Plan approved by maintainer
- [x] Safe migration path approved
- [x] Dedicated `research_comments` table approved
- [ ] Keep existing JSON flows and endpoints intact
- [ ] Do not remove M1 functionality

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
- [ ] Startup smoke test
- [ ] Role permission checks
- [ ] Full test run (`python -m pytest -q RoomZero/tests`)

## 9) Completion deliverables
- [ ] Final report includes:
  - [ ] changed files
  - [ ] new tables
  - [ ] new API routes
  - [ ] test results
  - [ ] remaining blockers
- [ ] Commit with exact message:
  - [ ] `Implement RoomZero research platform MVP`
