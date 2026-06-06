# TODO - M3.4 Simulation Review Moderation + Audit Visibility (active)

- [x] Analyze M3.4 scope and inspect required files
- [x] Prepare and confirm additive migration-safe implementation plan

## Step 1 — Execution tracking setup
- [x] Create/update active TODO tracker for M3.4 work
- [ ] Keep all M3.1/M3.2/M3.3 behavior unchanged
- [ ] Keep websocket behavior unchanged
- [ ] Keep all changes additive and migration-safe

## Step 2 — Backend models and lifecycle/audit API
- [x] Update `RoomZero/app/models.py`
  - [x] Add PATCH request model for review note lifecycle updates
  - [x] Add sanitized review-audit response model(s)
- [x] Update `RoomZero/app/main.py`
  - [x] Add allowed review-note statuses (`active`, `resolved`, `flagged`, `archived`)
  - [x] Add status validation helper(s)
  - [x] Add note lookup helper scoped to event_id + note_id
  - [x] Add PATCH `/simulation/events/{event_id}/review-notes/{note_id}`
  - [x] Verify event existence prior to patch
  - [x] Verify note existence and event ownership prior to patch
  - [x] Support safe status update + optional safe note_text update
  - [x] Reject empty note_text; enforce max length
  - [x] Update `updated_at` on changes
  - [x] Add lifecycle audit rows with sanitized details only
  - [x] Add GET `/simulation/events/{event_id}/review-audit`
  - [x] Add safe limit default and cap for review audit endpoint
  - [x] Ensure no raw simulation payload in API responses/audit details

## Step 3 — API tests (lifecycle + audit + regressions)
- [x] Update `RoomZero/tests/test_api_endpoints.py`
  - [x] PATCH status -> resolved
  - [x] PATCH status -> flagged
  - [x] PATCH status -> archived
  - [x] Invalid status rejected
  - [x] Missing event -> 404
  - [x] Missing note -> 404
  - [x] Wrong-event note access rejected/404
  - [x] Optional note_text update validation (empty/max length)
  - [x] Audit rows for lifecycle actions created
  - [x] GET review-audit returns sanitized entries
  - [x] review-audit limit default/cap behavior validated
  - [x] No raw payload leakage in audit endpoint output
  - [x] Regression: existing GET review notes unchanged
  - [x] Regression: existing POST review note unchanged
  - [x] Regression: `/simulation/events` unchanged
  - [x] Regression: `/simulation/events/summary` unchanged

## Step 4 — Frontend lifecycle + audit visibility UI
- [x] Update `RoomZero/app/static/index.html`
  - [x] Add lifecycle controls region for review notes
  - [x] Add compact review-audit mini-panel for selected event
- [x] Update `RoomZero/app/static/app.js`
  - [x] Render note status badge
  - [x] Add note-level lifecycle actions (active/resolved/flagged/archived)
  - [x] Add PATCH lifecycle calls
  - [x] Load and render review-audit for selected event
  - [x] Refresh notes + audit after status/update action
  - [x] Refresh audit after review-note creation
  - [x] Keep clear loading/error/success states
  - [x] Preserve existing filters/summary/list/trace/create-note behavior
  - [x] Restore robust escapeHtml hardening (numeric entity encoding)
- [x] Update `RoomZero/app/static/styles.css`
  - [x] Add lifecycle button/status badge styling
  - [x] Add review-audit panel styling
  - [x] Add archived review-note visual state
  - [x] Keep narrow/mobile layout usable

## Step 5 — Browserless/source verification notes
- [x] Verify `index.html` contains lifecycle + audit UI elements
- [x] Verify `app.js` contains PATCH/status/audit loading behavior
- [x] Verify `styles.css` contains lifecycle + audit styling
- [x] Document browser automation blocker (if still unavailable)
- [x] Add manual UI checklist for M3.4

## Step 6 — Required validation commands
- [ ] `python -m compileall -q RoomZero`
- [ ] `python -m pytest -q`
- [ ] `python -m pytest -q RoomZero/tests/test_ws_unreal.py`
- [ ] `python -m pytest -q RoomZero/tests/test_api_endpoints.py RoomZero/tests/test_research_jobs.py RoomZero/tests/test_m2_platform.py`
- [ ] `docker compose -f docker-compose.yml config`
- [ ] `node --check RoomZero/app/static/app.js` (if node available)

## Step 7 — Final report
- [ ] Report M3.4 frontend parity status
- [ ] Report exact files changed
- [ ] Report exact frontend behavior added
- [ ] Report exact source-level verification results
- [ ] Confirm existing backend behavior unchanged
- [ ] Report exact commands run
- [ ] Report command-by-command pass/fail results
- [ ] Report browser automation availability and deferred items
- [ ] State whether M3.4 is now fully complete
- [ ] Recommend M3.5 next step

## Manual UI checklist (M3.4 frontend parity)
- [ ] Open `/ui` locally.
- [ ] Open Simulation Events.
- [ ] Select an event.
- [ ] Confirm review notes load.
- [ ] Add a note.
- [ ] Confirm audit panel updates after note creation.
- [ ] Mark note resolved.
- [ ] Confirm note status badge changes.
- [ ] Confirm audit panel updates after status change.
- [ ] Mark note flagged.
- [ ] Archive note.
- [ ] Confirm archived state is visible.
- [ ] Confirm filters still work.
- [ ] Confirm summary panel still works.
- [ ] Confirm trace detail still works.
- [ ] Confirm no raw payload is shown.
- [ ] Confirm narrow/mobile layout remains usable.
