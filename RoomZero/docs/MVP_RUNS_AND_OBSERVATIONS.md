# MVP: persistent simulation runs and observations

## Scope

This increment closes the persistence gap between an approved scenario and its
research evidence. It is additive to the existing M2/M4 platform, keeps the
legacy JSON modules compatible, and links run-scoped Unreal observations to the
SQLite evidence trail.

## Data model

### `simulation_runs`

- Belongs to one `simulation_scenario`.
- Uses a unique, increasing `run_number` within the scenario.
- Stores lifecycle state, timestamps, input snapshot, collected metrics, result
  summary, creator, and audit history.
- Enforces `queued -> running -> completed|failed|cancelled`; terminal runs are
  immutable and only one run per scenario may be active.
- A run can only be created when the scenario is ethically approved and marked
  `ready_for_test` or already in repeatable `testing` state.

### `observations`

- Belongs to one run and repeats its scenario ID for efficient traceability.
- Stores observer, type, narrative content, structured data, severity, and
  timestamps.
- Observer, tester, contributor, researcher, reviewer, and admin roles may add
  observations while a run is active; inactive and unknown users are rejected.
- Unreal observations with a `run_id` (or compatibility alias `simulation_id`)
  are persisted, audited, and acknowledged with an `observation_id`. Persisted
  payloads are capped at 64 KiB.

## Governance and concurrency controls

- Researchers may draft questions and scenarios but cannot approve or review
  their own work.
- Admin and reviewer roles own approval, rejection, prioritization, and scenario
  readiness decisions. Reviewers cannot invite new admin/reviewer accounts.
- Medium-, high-, and critical-risk scenario approval requires human oversight;
  high and critical risk also require mitigation notes.
- SQLite write transactions serialize run numbering, run state transitions, and
  observation admission so concurrent requests cannot create two active runs or
  attach evidence after completion.

## Migration safety

Tables and indexes use `CREATE TABLE/INDEX IF NOT EXISTS`; existing tables and
columns are preserved. `schema_migrations` records bootstrap versions 1-3,
initialization is idempotent, and every startup runs `PRAGMA foreign_key_check`.
This remains a lightweight local migration layer, not a full Alembic
upgrade/rollback workflow.

## Verification performed

- Dependency consistency: `python -m pip check`
- Python compile check: `python -m compileall -q app tests scripts`
- Migration smoke test against a new temporary SQLite database
- Idempotent migration ledger and foreign-key validation tests
- Run concurrency, role-boundary, state-machine, and negative API tests
- Isolated full pytest suite that does not mutate tracked runtime data
- Ruff, JavaScript syntax, release-asset parity, and duplicate-HTML-ID checks

## Deferred deliberately

- Automatic execution of Unreal or model processes from a run record
- Live end-to-end verification with an actual Unreal Engine client
- Full Alembic upgrade/rollback and backup/restore automation
- Email delivery and credential-based authentication
- Deterministic replay, run comparison, and CSV export

These are separate security and reliability milestones and should not be coupled
to this persistence increment.
