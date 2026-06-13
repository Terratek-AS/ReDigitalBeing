# ReDigitalBeing / RoomZero

RoomZero is the canonical backend “simulation room brain” of the ReDigitalBeing project.

- **RoomZero/FastAPI is the official system of record** for intelligence behavior, memory flows, research workflows, invitations, users, audit logs, and simulation operations.
- The GitHub Pages site is a **public static chamber console shell**. It only becomes functional when connected to a reachable RoomZero backend API.

Repository: https://github.com/Terratek-AS/ReDigitalBeing

## Current Status

- M1, M1.5, and M2 foundations are implemented in the RoomZero backend and UI.
- M4.1 is the Admin Research Dashboard backend foundation. The earlier Model Adapter / Intelligence Interface roadmap item is deferred to M5 or later unless the maintainer reprioritizes it.
- Public GitHub Pages preview exists:
  - https://knoksen.github.io/ReDigitalBeing
- Root documentation is now established here for project orientation and backend integration guidance.
- M2.1 focuses on making the static frontend safely configurable for a public backend deployment.

## Strategic Direction

RoomZero should evolve as a local-first, testable, ethically governed simulation laboratory where Unreal/MetaHuman acts as the embodiment layer, while the core value lives in the research, event, audit, intelligence, and knowledge architecture behind it.

## GitHub Pages Preview

Preview URL:  
https://knoksen.github.io/ReDigitalBeing

Important:
- Pages serves static assets only.
- Without a reachable backend API endpoint, the UI acts as a shell and interactive actions will fail or be limited.
- Configure frontend API base URL to point to deployed RoomZero backend.

## Backend Requirement (Canonical Model)

RoomZero backend is required for real functionality:

- `/health` and runtime status
- persona/state-driven chat behavior
- memory persistence and retrieval
- tester invite/register flows
- research queue, jobs, and knowledge approvals
- platform entities (users, invitations, questions, comments, scenarios, knowledge, audit)

Frontend must call RoomZero API over HTTP(S) using configured API base URL.

## Local Development

### 1) Install dependencies (Windows PowerShell)

From `RoomZero` directory:

```powershell
.\install.ps1
```

Manual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2) Start backend (FastAPI)

```powershell
cd RoomZero
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Or:

```powershell
.\run.ps1
```

### 3) Open local UI/API

- UI: http://127.0.0.1:8000/ui
- Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Frontend Backend Configuration (M2.1)

Frontend static config file:

- `RoomZero/app/static/config.js` (runtime/default config)
- `RoomZero/app/static/config.example.js` (production template)

Default local development value:

```js
window.ROOMZERO_CONFIG = {
  API_BASE_URL: "http://127.0.0.1:8000"
};
```

For public deployment, change `API_BASE_URL` to your backend domain, for example:

```js
window.ROOMZERO_CONFIG = {
  API_BASE_URL: "https://roomzero-api.yourdomain.com"
};
```

## PWA / Mobile Install Notes

- RoomZero UI supports PWA install pattern.
- On mobile browser, open the UI and choose **Add to Home Screen** / **Install**.
- For local testing from phone:
  - run backend on your PC
  - use your PC LAN IP with port 8000 (same Wi-Fi)
- Service worker/offline fallback exist for shell experience, but API-backed actions still require backend connectivity.

## Tester Onboarding

Start here:
- `RoomZero/TESTER_START_HERE.md`

Use invite + registration workflow exposed by backend endpoints and UI flows.

## Current Limitations

- GitHub Pages cannot host Python/FastAPI runtime; backend must be deployed separately.
- If backend is unreachable, shell loads but API actions fail.
- M2.1 intentionally does not include full real-time chamber streaming implementation yet.
- Local-first data and SQLite layout are suitable for prototype/research phase, not final production scale.

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

| Milestone | Status | Progress |
|---|---|---|
| M8.1 Real Research Material & Terratek Knowledge Paths | Planned | `░░░░░░░░░░ 0%` |

Progress percentages are milestone-tracking indicators, not release guarantees. Completion requires passing tests, documentation updates, and review. M3 remains in progress. M8.1 remains planned.

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
  "created_at": "2026-06-06T16:00:00Z",
  "metadata": {
    "transport": "websocket",
    "payload_summary": {
      "keys": [],
      "size": 0
    }
  }
}
```

### M8.1 — Real Research Material & Terratek Knowledge Paths (Planning-Only)

Purpose:
Build a structured, traceable research material layer that connects real sources, standards, material profiles, research questions, simulation scenarios, observations, findings, and Terratek project decisions.

Scope:
- curated real research source database
- Terratek-specific research paths
- source reliability scoring
- research claims linked to evidence
- material profiles linked to standards, EPD/LCA data, and simulation scenarios
- human review workflow for approving sources and claims
- exportable research packs for Terratek projects
- future ingestion of papers, PDFs, APIs, manual uploads, standards metadata, and case studies

#### Terratek research paths

- Terratek.Materials
  - timber
  - mass timber
  - low-carbon concrete
  - recycled steel
  - reclaimed brick
  - wood fibre insulation
  - hemp/hempcrete
  - clay/earth materials
  - bio-based boards
  - long-life facades
  - demountable construction systems

- Terratek.Circularity
  - reuse mapping
  - material passports
  - deconstruction planning
  - waste reduction
  - product documentation
  - reuse logistics
  - quality control
  - circular procurement

- Terratek.CarbonLCA
  - NS 3720
  - NS-EN 15978
  - EPD
  - product modules A1-A3
  - transport A4
  - maintenance B2
  - replacement B4
  - construction waste
  - BIM quantity takeoff to carbon calculations

- Terratek.BuildingPhysics
  - moisture safety
  - thermal bridges
  - air tightness
  - vapour control
  - coastal climate
  - durability
  - repairability
  - robust detailing

- Terratek.DigitalTwin
  - Revit / IFC
  - sensor data
  - temperature
  - relative humidity
  - CO2 levels
  - energy use
  - operation monitoring
  - design-performance gap

- Terratek.LowImpactSite
  - reduced excavation
  - reduced blasting
  - sloped terrain
  - point foundations
  - screw foundations
  - stormwater
  - erosion
  - terrain preservation

- Terratek.SocialSustainability
  - local craftsmen
  - training
  - workforce inclusion
  - young professionals
  - people outside employment
  - local value creation
  - cultural heritage and building traditions

#### Proposed future data model

- `research_sources`
  - source_id
  - title
  - authors
  - publisher
  - year
  - source_type
  - url or local_reference
  - jurisdiction
  - domain
  - reliability_level
  - review_status
  - tags
  - added_by
  - created_at
  - updated_at

- `research_paths`
  - path_id
  - name
  - description
  - domain
  - owner
  - priority
  - status
  - created_at
  - updated_at

- `research_materials`
  - material_id
  - name
  - category
  - description
  - use_cases
  - benefits
  - risks
  - documentation_needed
  - standards_refs
  - source_ids
  - tags

- `research_claims`
  - claim_id
  - claim
  - evidence_level
  - source_ids
  - limitations
  - related_materials
  - related_paths
  - review_status

- `research_evidence_links`
  - evidence_id
  - source_id
  - claim_id
  - quote_or_summary
  - relevance_score
  - reviewer_notes

- `material_profiles`
  - material_id
  - name
  - category
  - structural_use
  - climate_impact_notes
  - moisture_risk_notes
  - durability_notes
  - reuse_potential
  - required_documentation
  - BIM_mapping
  - related_standards

- `standard_references`
  - standard_id
  - name
  - jurisdiction
  - description
  - status
  - copyright_note
  - external_reference
  - related_paths

- `case_studies`
  - case_id
  - title
  - location
  - project_type
  - materials
  - outcomes
  - source_ids
  - lessons_learned

- `source_reviews`
  - review_id
  - source_id
  - reviewer_id
  - reliability_assessment
  - relevance_assessment
  - approval_status
  - notes
  - reviewed_at

#### Example research question templates

- Which material combinations provide the lowest embodied carbon while maintaining moisture safety and long service life in Norwegian coastal climate?
- How can BIM quantity takeoff be connected to EPD and NS3720-based early-phase carbon calculations?
- Which reused building products are safest and most practical for early Terratek pilot projects?
- How can low-impact foundations reduce blasting, excavation, cost, and environmental damage on sloped terrain?
- How can sustainable building projects become training arenas for people entering or returning to work?

#### Source quality levels

- Level A — legal/standard/official authority  
  Examples: TEK17 / DiBK, Norwegian Standards metadata, EU regulations, official environmental product declarations

- Level B — research institution / peer-reviewed / technical report  
  Examples: SINTEF, NTNU, universities, peer-reviewed journals, research project reports

- Level C — industry guidance / certification / professional practice  
  Examples: FutureBuilt, BREEAM-NOR guidance, Enova guidance, manufacturer technical documentation

- Level D — case study / field observation  
  Examples: pilot projects, Terratek internal observations, interviews, construction site learnings

- Level E — unverified idea / hypothesis  
  Examples: early concept notes, AI-generated proposals, speculative design ideas

#### Safety, copyright, and review rules

- Do not copy paid standards verbatim into the repository.
- Store metadata, references, summaries, and project-specific notes.
- Use quotes only when legally safe and short.
- Keep clear distinction between source text, human summary, and AI-generated synthesis.
- Research claims must link to evidence.
- Human review is required before claims influence project decisions.
- AI-generated suggestions must be treated as hypotheses until reviewed.

#### Initial Terratek Source Pack plan

Categories:
- TEK17 climate/lifecycle and construction waste provisions
- NS 3720 / NS-EN 15978 / NS 3451 metadata references
- SINTEF reuse and building material reports
- EPD/LCA data sources
- FutureBuilt / circular building criteria
- Enova and energy efficiency references
- Terratek internal field notes and pilot cases

Notes:
- Do not include copyrighted standards text.
- Include references, summaries, and metadata-level descriptions only.
- This section is documentation and architecture planning only; no ingestion or migrations are implemented here.

Example event types:
- `unreal.observation.*`
- `scenario.started`
- `scenario.completed`
- `agent.command.issued`
- `research.question.approved`
- `chamber.state.updated`
- `safety.flag.created`

Transport options:
- WebSocket: active foundation
- SSE: planned option
- REST: existing/foundation
- File replay: future
- Queue/broker: future only, not required for MVP

M3 definition of done:
- Internal simulation event model exists.
- Unreal observations normalize into simulation events.
- Events can be traced safely.
- Payload summaries avoid sensitive full dumps.
- Tests cover event normalization.
- README/TODO clearly mark M3 complete only after validation.

### M4 — Model Adapter & Intelligence Interface

Purpose:  
Create a clean model provider interface so RoomZero can swap intelligence providers without rewriting simulation logic.

Includes:
- Model adapter interface in `llm.py`.
- Clean provider swapping: Local ↔ OpenAI ↔ other providers.
- Provider metadata.
- Timeout handling.
- Fallback policy.
- Safe error handling.
- Provider capability declaration.

Target architecture:

Simulation Runtime  
→ Model Adapter Interface  
→ Provider Router  
→ Local / OpenAI / Other  
→ Response Normalizer  
→ Safety Filter  
→ Agent Command

Provider interface should eventually support:
- `generate_response()`
- `summarize_observation()`
- `classify_intent()`
- `score_risk()`
- `suggest_agent_command()`
- `extract_memory_candidate()`

### M5 — Expanded Simulation Data Model

Purpose:  
Expand the platform from basic records into a research-grade simulation database.

Includes:
- Memory embeddings store.
- Experiment runs.
- Metrics time-series.
- Richer audit trail.
- Observation history.
- Result summaries.
- Future Postgres migration path.

Proposed future tables:
- `simulation_events`
- `experiment_runs`
- `experiment_metrics`
- `agent_memory_entries`
- `memory_embeddings`
- `scenario_results`
- `safety_reviews`
- `model_provider_logs`

### M6 — Full Simulation Room Console UI

Purpose:  
Build the central lab interface where researchers can observe, control, and review live simulations.

Includes:
- Full simulation room console UI.
- Panel-based lab interface.
- Live chamber monitor.
- Agent panel.
- Memory panel.
- Experiment panel.
- Event stream panel.
- Safety/audit panel.
- Scenario control panel.

Suggested panel layout:
- Chamber Monitor
- Agent State
- Event Stream
- Scenario Panel
- Memory Panel
- Metrics Panel
- Safety Panel
- Admin Panel

### M7 — MetaHuman / Digital Human Runtime

Purpose:  
Connect RoomZero cognition and events to a believable embodied digital human in Unreal Engine.

Includes:
- MetaHuman command mapping.
- Emotion → facial expression hooks.
- Speech command → audio/animation flow.
- Animation command → Unreal behavior.
- Look-at / attention commands.
- Idle behavior.
- Observation-driven reactions.
- Safe-mode behavior.

Command categories:
- `speak`
- `set_emotion`
- `play_animation`
- `look_at`
- `set_attention`
- `enter_idle`
- `react_to_observation`
- `safe_pause`

### M8 — Research Knowledge Engine

Purpose:  
Turn RoomZero from a simulation platform into a continuously growing research knowledge system.

Includes:
- Knowledge base enrichment.
- Source references.
- Research findings.
- Scenario result summaries.
- Human review workflow.
- Exportable research logs.
- Source-to-simulation traceability.
- Future paper/API ingestion.

Knowledge relationship:

Research Question  
→ Scenario  
→ Experiment Run  
→ Simulation Events  
→ Observations  
→ Result Summary  
→ Knowledge Entry  
→ Source References

## Recommended Implementation Order

1. M0 — Fix CI and repository hygiene.
2. Review / merge docs-only progress PR if clean.
3. Complete M3 simulation-event architecture.
4. Continue M1.5 UI polish around stable platform features.
5. Start M4 model adapter interface.
6. Expand M5 memory/metrics/data model.
7. Build M6 simulation room console.
8. Connect M7 MetaHuman runtime.
9. Grow M8 research knowledge engine.
