# ReDigitalBeing / RoomZero Roadmap (Milestone Tracking)

## Completed

- [x] M1 foundation delivered:
  - [x] FastAPI backend baseline
  - [x] Static UI shell and PWA install path
  - [x] Core persona/state/memory/safety flow
- [x] M1.5 UX and flow improvements landed in current UI baseline.
- [x] M2 platform foundation implemented in codebase:
  - [x] SQLite platform layer
  - [x] invitations/users/questions/comments/scenarios/knowledge/audit route families
  - [x] targeted M2 platform test coverage present
- [x] M2.1 backend/frontend integration baseline:
  - [x] static frontend config model (`config.js` / `config.example.js`)
  - [x] deployment docs baseline
  - [x] CORS explicit allowlist model
- [x] M2.1.3 rename alignment completed:
  - [x] public references aligned to Knoksen where in scope
  - [x] intended canonical URL set to `https://knoksen.github.io/ReDigitalBeing`
  - [x] CORS allowlist includes Knoksen Pages origin
  - [x] targeted tests and local smoke previously passed
  - [x] completion commit recorded: `3d45028`

## Current blocker

- [ ] **M2.1.4 Deployment ownership blocker (active):**
  - current remote: `https://github.com/Terratek-AS/ReDigitalBeing.git`
  - intended canonical Pages URL: `https://knoksen.github.io/ReDigitalBeing`
  - blocker: canonical Knoksen Pages URL cannot be authoritative until repo ownership/deployment target is under `knoksen` namespace (transfer/fork/mirror + Pages config)

## Current task

- [ ] Finalize deployment-ownership path so canonical Pages URL is technically valid and controlled by Knoksen.
- [ ] Keep backend stability unchanged while resolving ownership/deployment target.
- [ ] Validate docs + deployment configuration for canonical URL consistency.

## Next milestone

## M2.2 Research MVP Foundation (next implementation milestone)

- [ ] Consolidate and harden research workflows for production-like team usage.
- [ ] Strengthen reviewer/admin governance across question/source/knowledge lifecycles.
- [ ] Improve operational reliability for platform entities and auditability.
- [ ] Define acceptance gates for MVP readiness (roles, lifecycle, observability, docs, and test evidence).

## Backend roadmap

- [ ] Harden API contracts for platform endpoints (clear error semantics and role checks).
- [ ] Add stronger migration/versioning discipline for SQLite schema evolution.
- [ ] Expand audit coverage for sensitive platform actions.
- [ ] Prepare optional externalized persistence path for post-prototype scale.
- [ ] Formalize deployment profiles (local/dev/staging/prod) for config/CORS safety.

## Frontend roadmap

- [ ] Improve static shell resilience for backend-unavailable states.
- [ ] Strengthen environment-aware API base URL handling.
- [ ] Improve route/state persistence and error UX.
- [ ] Add clearer public-vs-admin capability boundaries in UI messaging.
- [ ] Validate Pages build/deploy artifact integrity on each release path.

## Admin dashboard roadmap

- [ ] Improve invitation lifecycle visibility (issued/accepted/expired/revoked).
- [ ] Add richer moderation/review queues with filters and status transitions.
- [ ] Expand recent-activity/audit visualization for governance workflows.
- [ ] Add safer admin action confirmation patterns for high-impact operations.

## Tester interface roadmap

- [ ] Streamline onboarding + invite redemption + consent journey.
- [ ] Improve test session reporting UX and status feedback.
- [ ] Add clearer endpoint/connectivity diagnostics for testers.
- [ ] Improve bug reporting structure and exportability.

## Ethical review roadmap

- [ ] Formalize review checkpoints for memory sensitivity and consent boundaries.
- [ ] Add stronger reviewer workflows for questionable research/source items.
- [ ] Document escalation path for risky/ambiguous content.
- [ ] Expand safety test cases for edge-case policy handling.

## Simulation roadmap

- [ ] Define M3 real-time simulation event model (WebSocket/SSE baseline).
- [ ] Establish event schemas for scenario run telemetry.
- [ ] Introduce phased live-room orchestration model.
- [ ] Keep strict separation between MVP scope and experimental simulation features.

## Knowledge base roadmap

- [ ] Strengthen approved-knowledge provenance metadata and linking.
- [ ] Improve traceability from question -> scenario -> knowledge entry.
- [ ] Define quality scoring/versioning process for promoted knowledge.
- [ ] Prepare connector strategy for future external source ingestion.

## Testing checklist

- [ ] Run targeted backend regression suite:
  - [ ] `python -m pytest -q RoomZero/tests/test_memory.py RoomZero/tests/test_safety.py RoomZero/tests/test_llm_intents.py RoomZero/tests/test_research_jobs.py RoomZero/tests/test_m2_platform.py`
- [ ] Run local smoke checks:
  - [ ] `GET /health` returns 200
  - [ ] `GET /ui` returns 200
- [ ] Run targeted CORS checks for allowed and blocked origins.
- [ ] Ensure docs/deployment references remain canonical and non-conflicting.

## Deployment checklist

- [ ] Decide ownership strategy: transfer vs fork vs mirror.
- [ ] Ensure canonical Pages deployment target is under Knoksen control.
- [ ] Verify Pages source artifact and branch/environment config.
- [ ] Verify canonical URL is published and documented consistently.
- [ ] Confirm backend domain + CORS allowlist alignment with production frontend origin.

## Windows installer checklist

- [ ] Re-verify install/build chain:
  - [ ] `.\install.ps1 -WithBuilder`
  - [ ] `.\build_installer.ps1`
  - [ ] `iscc .\installer\RoomZero.iss`
- [ ] Validate install, first run, upgrade path, and uninstall behavior.
- [ ] Capture release evidence and known caveats.

## Mobile/PWA/APK checklist

- [ ] Keep PWA install route as primary mobile MVP.
- [ ] Validate Android install + offline shell behavior.
- [ ] Defer APK wrapper decision until deployment architecture stabilizes.
- [ ] Document clear backend connectivity requirements for mobile users.

## Unreal Engine future integration notes

- [ ] Keep Unreal integration explicitly post-MVP.
- [ ] Define bridge contract (API/event transport/auth) before prototype plugin work.
- [ ] Validate compatibility with real-time chamber architecture (M3+).
- [ ] Gate Unreal work behind stable backend + simulation event foundations.

## Known risks

- [ ] Ownership mismatch risk: canonical URL claims without matching repo namespace control.
- [ ] Pages-only frontend risk: user expectations may exceed static shell capability.
- [ ] SQLite durability/scale risk for production workloads without migration plan.
- [ ] Configuration drift risk between docs, workflow, frontend config, and CORS policy.
- [ ] Scope creep risk from mixing roadmap planning and feature implementation in same cycle.

## Next recommended task

- [ ] Execute **M2.1.4 Deployment Ownership + Canonical URL Validation** completion:
  - [ ] finalize ownership/deployment target under Knoksen namespace
  - [ ] run canonical URL + CORS + smoke + targeted test validation
  - [ ] publish short deployment ownership decision record in docs
  - [ ] keep runtime and database behavior unchanged while finalizing deployment authority
