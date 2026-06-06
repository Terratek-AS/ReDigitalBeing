# ReDigitalBeing / RoomZero

RoomZero is the canonical backend “simulation room brain” of the ReDigitalBeing project.

- **RoomZero/FastAPI is the official system of record** for intelligence behavior, memory flows, research workflows, invitations, users, audit logs, and simulation operations.
- The GitHub Pages site is a **public static chamber console shell**. It only becomes functional when connected to a reachable RoomZero backend API.

Repository: https://github.com/Terratek-AS/ReDigitalBeing

## Current Status

- M1, M1.5, and M2 foundations are implemented in the RoomZero backend and UI.
- Public GitHub Pages preview exists:
  - https://knoksen.github.io/ReDigitalBeing
- Root documentation is now established here for project orientation and backend integration guidance.
- M2.1 focuses on making the static frontend safely configurable for a public backend deployment.

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

### Milestone Status

**M1.2 Unreal Integration Readiness**  
`██████████ 100%` ✅ Completed

**M1.3 Contract Fixtures & Protocol Stability**  
`██████████ 100%` ✅ Completed

**M1.4 Handshake / Schema Hardening**  
`██████████ 100%` ✅ Completed

**M3 Simulation Event Architecture**  
`██████░░░░ 60%` ⏳ In progress

**M4 Simulation Intelligence Layer**  
`░░░░░░░░░░ 0%` Planned

**M5 MetaHuman / Digital Human Runtime**  
`░░░░░░░░░░ 0%` Planned

| Milestone | Status | Progress |
|---|---|---|
| M8.1 Real Research Material & Terratek Knowledge Paths | Planned | `░░░░░░░░░░ 0%` |

Progress percentages are milestone-tracking indicators, not release guarantees. Completion requires passing tests, documentation updates, and review. M3 remains in progress. M8.1 remains planned.

## Roadmap

### M1
- PWA/mobile launcher
- service worker
- offline fallback
- GitHub Pages shell

### M1.5
- UI/product polish
- onboarding
- mobile role navigation

### M2
- SQLite platform layer
- users
- invitations
- research questions
- comments
- scenarios
- knowledge entries
- audit logs
- permission checks

### M2.1
- public backend configuration
- CORS
- deployment documentation
- root README
- Pages-to-backend connection model
- Unreal integration readiness docs + smoke tooling (`RoomZero/README.md`, `RoomZero/scripts/ws_unreal_smoke.py`)

### M3
- real-time chamber layer using WebSocket or SSE
- live simulation room events
- experiment run streaming
- activity/event bus

### M4
- model adapter interface in `llm.py`
- clean provider swapping: Local ↔ OpenAI ↔ other providers
- provider metadata and fallback policy

### M5
- expanded simulation data model:
  - memory embeddings store
  - experiment runs
  - metrics time-series
  - richer audit trail
  - future Postgres migration path

### M6
- full simulation room console UI
- panel-based lab interface
- live chamber monitor
- agent/memory/experiment panels

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

