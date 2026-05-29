# RoomZero Presentation

## 1) Vision
RoomZero is a local-first research platform for persistent digital-being simulation with strong safety controls and transparent workflows.

## 2) What’s Included
- Eir persona chat with memory/state continuity
- Research Network (testers, research queue, sources, feedback)
- Continuous research jobs (manual/local mode)
- Web UI dashboard for faster testing operations
- Windows installer pipeline (PyInstaller + Inno Setup)

## 3) Architecture Snapshot
- Backend: FastAPI (`app/main.py`)
- Modules: memory, persona, state, safety, llm, testers, research, feedback, sources, research_jobs
- Data store: JSON files under `data/`
- UI: static dashboard under `app/static/`
- CLI: `python -m app.cli`

## 4) New Delivery Polish (Task 18)
- Added quick-action section in UI for:
  - health check
  - one-click tester onboarding flow
  - research jobs quick listing
  - direct docs open
- Added install quick command buttons:
  - install
  - run
  - build installer
- Added mobile quick install/access help:
  - add-to-home guidance
  - local UI URL copy helper

## 5) Effective User Testing Flow
1. Create invite
2. Register tester
3. Chat with Eir
4. Submit research question/source
5. Run research jobs
6. Submit session feedback
7. Review stats and iterate

## 6) Install and Run
- Install:
  `.\install.ps1`
- Run:
  `.\run.ps1`
- Build installer:
  `.\install.ps1 -WithBuilder`
  `.\build_installer.ps1`

## 7) API and Console
- API docs: `/docs`
- UI dashboard: `/ui`
- Health: `/health`

## 8) Safety and Governance
- Explicit consent for tester onboarding
- Role-based tester permissions
- Reviewer-controlled approval pipelines
- Local-first data control and transparency

## 9) Next Recommended Steps

### Advanced UI/UX execution priorities
- Finalize UX architecture for key user journeys:
  - invite tester
  - run research jobs
  - submit feedback
  - moderate sources
- Improve dashboard clarity and interaction quality:
  - clearer hierarchy and action grouping
  - loading, empty, success, and error states
  - inline validation and actionable feedback
- Enforce accessibility and responsiveness standards:
  - keyboard navigation + visible focus states
  - semantic landmarks and contrast checks
  - mobile-first usability for quick testing/admin flows
- Validate UI acceptance outcomes:
  - complete invite-to-chat flow from `/ui` without relying on `/docs`
  - keep critical workflows discoverable with low interaction depth

### Windows installer hardening priorities
- Validate full build chain on Windows:
  - `.\install.ps1 -WithBuilder`
  - `.\build_installer.ps1`
  - `iscc .\installer\RoomZero.iss`
- Execute installer QA scenarios:
  - clean-machine install
  - first run (`/health`, `/ui`)
  - uninstall behavior
  - upgrade path behavior
- Improve trust/release readiness:
  - SmartScreen/signing expectations for unsigned builds
  - rollback guidance for install/first-run failures
  - verification evidence (logs/checklists/screenshots)
- Validate installer acceptance outcomes:
  - non-dev user can install and run from docs only
  - build/install flow is reproducible by another team member

### Cross-cutting quality priorities
- Expand endpoint-level automated tests for testers/research/feedback/sources
- Add end-to-end UI smoke tests
- Validate installer artifact generation in CI
- Add optional remote knowledge connectors with strict review gates

## 10) Repository
- GitHub: https://github.com/knoksen/ReDigitalBeing
