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
- [x] M2.1.4 deployment ownership validation completed.

## Current blocker

- [ ] **M2.1.5 Repository Ownership / Knoksen Deployment Decision (active):**
  - current remote owner: `https://github.com/Terratek-AS/ReDigitalBeing.git`
  - intended canonical URL target: `https://knoksen.github.io/ReDigitalBeing`
  - deployment authority for canonical Knoksen Pages URL is pending ownership/deployment decision under `knoksen` namespace
  - M3 Public Tester Platform implementation must not proceed until M2.1.5 is resolved

## Current task

- [ ] Produce planning-only M3 Public Tester Platform roadmap.
- [ ] Keep runtime/app/backend/frontend/database behavior unchanged.
- [ ] Do not modify or stage runtime database files, including `RoomZero/data/platform/platform.sqlite`.
- [ ] M3 planning checklist:
  - [ ] document M3 objective
  - [ ] document what M3 is / is not
  - [ ] document M3 dependencies (M2.1.5 mandatory gate)
  - [ ] define landing/onboarding/invite/role roadmap
  - [ ] define PWA/mobile, feedback, approved research thread, admin monitoring roadmap
  - [ ] define tester safety/ethics rules
  - [ ] define testing/deployment checklists
  - [ ] define implementation order, risks, and next milestone after M3

## M3 Roadmap: Public Tester Platform (planning-only)

### M3 objective

Make RoomZero accessible, understandable, installable, and testable for invited external users through a stable public tester interface.

### What M3 is

- A planning milestone for invited external tester access and usability hardening.
- A product-readiness roadmap for public-facing tester documentation and guided workflows.
- A governance roadmap for invitation-controlled access, role-aware tester experiences, and transparent feedback loops.
- A deployment-readiness checklist for validating that public tester entry points are accurate, controlled, and supportable.

### What M3 is not

- Not a runtime feature-implementation milestone in this task.
- Not a bypass of M2.1.5 Repository Ownership / Knoksen Deployment Decision.
- Not M4 simulation runtime, agent-runtime, synthetic-cognition, Unreal, or MetaHuman implementation.
- Not authorization for database schema/runtime data changes.
- Not authorization to stage/commit `RoomZero/data/platform/platform.sqlite`.

### M3 dependencies

- M2.1.5 Repository Ownership / Knoksen Deployment Decision completed and documented.
- Canonical deployment ownership and URL authority validated for public tester communication.
- Stable baseline for existing tester/research/admin route families and role model.
- Documentation consistency across root + RoomZero docs before external tester invites.
- Existing safety/ethics guardrails preserved, including MetaHuman/Unreal presentation-only policy.

### Public landing page roadmap

- Define a clear landing narrative for invited testers:
  - what RoomZero is
  - what testers can do in this phase
  - what is intentionally out of scope
- Provide explicit environment/state badges:
  - local test mode
  - preview shell mode
  - backend-connected mode
- Add a concise “Start Here” handoff path to onboarding docs.
- Ensure no claim of open public access while access remains invite-controlled.

### Tester onboarding roadmap

- Provide stepwise onboarding for invited external users:
  - install/open path
  - environment verification
  - role expectations
  - first-session actions
- Add troubleshooting paths for API unavailable, CORS issues, and offline shell states.
- Provide expected outcomes for each onboarding step to reduce support overhead.
- Include responsible-use and consent reminders before first active testing session.

### Invitation/access roadmap

- Document invitation lifecycle:
  - invite issued
  - invite accepted
  - tester active
  - invite/tester revoked or expired
- Define access-control communication templates:
  - invite accepted
  - invite invalid/expired
  - access removed
- Clarify that external tester access is invitation-only and auditable.
- Align invitation docs with deployment ownership gate (M2.1.5).

### Role-based tester interface roadmap

- Define role-specific UI expectations:
  - observer
  - tester
  - researcher
  - reviewer
  - admin
- Publish a role-capability matrix for visible actions and restricted actions.
- Add role-aware guidance text in tester-facing docs to reduce confusion.
- Require clear escalation path for permissions/access mismatch reports.

### PWA/mobile roadmap

- Keep PWA install path as primary mobile route for M3.
- Define minimum mobile UX acceptance criteria:
  - installability
  - launch behavior
  - offline fallback behavior
  - backend connectivity notice clarity
- Document supported browser expectations and known limitations.
- Defer APK wrapper decisions until post-M2.1.5 and deployment architecture stabilization.

### Feedback/bug reporting roadmap

- Standardize tester feedback and bug report templates.
- Require minimum reproduction metadata:
  - device
  - OS
  - browser/app mode
  - URL/environment
  - expected vs actual
- Define triage labels:
  - blocker
  - high
  - medium
  - low
  - docs/usability
- Establish response-time and acknowledgement expectations for invited testers.

### Public approved research thread roadmap

- Publish rules for what can be surfaced as approved public research threads.
- Keep only reviewer/approved outputs visible in public tester narratives.
- Enforce separation between unreviewed queue content and approved public-facing summaries.
- Define provenance requirements for any externally visible approved research thread.

### Admin tester monitoring roadmap

- Define admin monitoring panel planning requirements:
  - invite status visibility
  - tester activity summaries
  - feedback/bug queue visibility
  - moderation/escalation states
- Establish audit expectations for admin-side invite and access actions.
- Define privacy-aware reporting boundaries for external tester analytics.
- Provide incident escalation checklist for safety or abuse reports.

### Safety/ethics rules for testers

- External testers must follow explicit consent and responsible-use policies.
- No claims of real consciousness or sentience in tester communications.
- Risky or ethically ambiguous test scenarios require reviewer/admin oversight.
- Prohibit misuse of system outputs for harmful or deceptive activity.
- Keep MetaHuman/Unreal references as future presentation-layer only; no AI-use crossover.

### Testing checklist (docs-only task)

- [ ] Verify M3 planning sections exist across designated docs.
- [ ] Verify M2.1.5 is consistently documented as current dependency gate.
- [ ] Verify no runtime/app/backend/frontend code edits were introduced.
- [ ] Verify `RoomZero/data/platform/platform.sqlite` is not staged.
- [ ] Run final `git status` and capture result.

### Deployment checklist (for M3 readiness validation)

- [ ] M2.1.5 ownership/deployment decision approved and recorded.
- [ ] Canonical URL authority validated under approved namespace.
- [ ] Public tester docs updated to reflect actual deployment state.
- [ ] Invite/access wording aligned with current deployment reality.
- [ ] Frontend shell vs backend-required behavior clearly documented for testers.

### Implementation order (planning sequence)

1. Resolve and document M2.1.5 ownership/deployment authority.
2. Finalize M3 public tester docs baseline (landing/onboarding/access/roles).
3. Validate PWA/mobile tester instructions and environment disclaimers.
4. Finalize feedback/bug reporting and approved research thread policy docs.
5. Finalize admin monitoring and safety/ethics rule documentation.
6. Run docs consistency pass and deployment-readiness checklist.
7. Enter next milestone execution planning after M3 documentation acceptance.

### Risks

- Ownership ambiguity risk if M2.1.5 remains unresolved while public tester messaging expands.
- Expectation mismatch risk if users assume open access instead of invite-only flow.
- Support burden risk from unclear onboarding in backend-unavailable states.
- Governance risk if approved vs unreviewed research outputs are not clearly separated.
- Scope creep risk if M3 planning is treated as authorization for runtime/M4 implementation.

### Next milestone after M3

**M3.1 Public Tester Pilot Execution (post-M2.1.5 resolution)**

- Run controlled invited external tester pilot.
- Validate onboarding completion rates and feedback triage throughput.
- Validate role-based access clarity and admin monitoring workflows.
- Publish pilot evidence package and readiness decision for broader access.

## Next milestone

## M2.2 Research MVP Foundation (next implementation milestone)

- [ ] Consolidate and harden research workflows for production-like team usage.
- [ ] Strengthen reviewer/admin governance across question/source/knowledge lifecycles.
- [ ] Improve operational reliability for platform entities and auditability.
- [ ] Define acceptance gates for MVP readiness (roles, lifecycle, observability, docs, and test evidence).

## M4 planning (future, documentation-only): Simulation Intelligence & Digital Human Layer

- [ ] M4 is **planning-only** in this cycle. No runtime/app/backend/frontend/database implementation in this task.
- [ ] M4 must build on M2/M3 and must not bypass:
  - [ ] M2.1.5 Repository Ownership / Knoksen Deployment Decision
  - [ ] M2.2 Research MVP Foundation stability gates
  - [ ] M3 simulation-event architecture hardening
- [ ] Planning principles:
  - [ ] approved research scenarios can become controlled simulation runs
  - [ ] simulation runs must be repeatable, observable, and auditable
  - [ ] agent behavior must be structured through explicit agent profiles
  - [ ] memory states must be inspectable, reversible, and separated from private user data
  - [ ] medium/high-risk scenarios require ethical approval and human oversight
  - [ ] MetaHuman remains visual avatar/presentation only
  - [ ] avoid real-consciousness claims; use synthetic consciousness markers and consciousness-adjacent behavioral markers
- [ ] M4 roadmap artifacts required in docs:
  - [ ] simulation runtime roadmap
  - [ ] agent profile roadmap
  - [ ] memory state roadmap
  - [ ] observation/metrics roadmap
  - [ ] ethical simulation gate roadmap
  - [ ] Unreal/MetaHuman presentation roadmap
  - [ ] future DB/API/UI model requirements
  - [ ] testing, safety, licensing, implementation order, risks, and post-M4 recommendation

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
- [ ] MetaHuman/Unreal AI-use guardrail:
  - [ ] MetaHuman may be used as a visual avatar/presentation layer only. MetaHuman assets, animation curves, rendered outputs, facial/motion data, or derived datasets must not be used to train, test, benchmark, evaluate, or enhance AI/ML/neural-network systems.
  - [ ] MetaHuman license review is mandatory before commercial release, paid distribution, enterprise use, or public product launch.
  - [ ] Keep Unreal/MetaHuman visual presentation strictly separated from RoomZero cognition, training, evaluation, simulation research datasets, and knowledge-base data.
  - [ ] AI research/testing must use original data, user-owned data, synthetic data created independently of MetaHuman assets, or separately licensed datasets.

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
- [ ] Verify intended canonical URL is published and documented consistently.
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

- [ ] Execute **M2.1.5 Repository Ownership / Knoksen Deployment Decision** completion:
  - [ ] finalize ownership/deployment target under Knoksen namespace
  - [ ] run canonical URL + CORS + smoke + targeted test validation
  - [ ] publish short deployment ownership decision record in docs
  - [ ] keep runtime and database behavior unchanged while finalizing deployment authority
