# TODO - Production Readiness & Repository Health (CI/Repo-Hardening PR)

## 0) Execution tracking for approved scope
- [x] Plan approved by maintainer
- [x] Create working branch (`blackboxai/...`)
- [ ] Keep scope isolated from PR #5 installer/runtime startup work
- [ ] Keep release `v1.0.1` untouched

## 1) Repository health (highest priority)
- [x] Add/repair GitHub Actions workflow(s) under `.github/workflows/`
  - [x] CI workflow for RoomZero (lint/test/build checks appropriate for current repo)
  - [x] CodeQL workflow for Python
- [x] Add/repair Dependabot config (`.github/dependabot.yml`)
- [x] Ensure dependency graph can resolve Python dependencies from repo layout
- [x] Validate workflow syntax and branch triggers

## 2) Inspection phase (non-destructive)
- [ ] Inspect packaging/build chain files:
  - [ ] `RoomZero/build_installer.ps1`
  - [ ] `RoomZero/install.ps1`
  - [ ] `RoomZero/RoomZero.spec`
  - [ ] `RoomZero/installer/RoomZero.iss`
- [ ] Inspect verification scripts:
  - [ ] `RoomZero/scripts/verify.ps1`
  - [ ] `RoomZero/scripts/smoke_api.ps1`
- [ ] Inspect key tests and coverage gaps:
  - [ ] `RoomZero/tests/test_memory.py`
  - [ ] `RoomZero/tests/test_safety.py`
  - [ ] `RoomZero/tests/test_llm_intents.py`
  - [ ] `RoomZero/tests/test_research_jobs.py`

## 3) Validation runs requested
- [x] Run: `python -m pytest -q`
- [x] Run: `powershell -ExecutionPolicy Bypass -File RoomZero/scripts/verify.ps1`
- [x] Run packaging checks (builder + installer script validation, no destructive ops)
- [x] Capture factual pass/fail outputs for report

## 4) Documentation/readiness updates (if needed by evidence)
- [x] Update `RoomZero/README.md` for CI/repo-health instructions
- [ ] Add/update release notes section for this PR scope
- [ ] Add architecture/deployment notes tied to CI/CD + packaging validation
- [x] Keep all changes traceable and factual (no placeholders)

## 5) Git/PR workflow requested by maintainer
- [x] Create branch with prefix `blackboxai/`
- [x] Commit only proven CI/config/docs (code only if concrete blocker)
- [x] Push branch
- [x] Open separate PR for repo-health scope
- [ ] Record PR link in final engineering report

## 6) Final deliverables
- [x] Passing tests / validation evidence
- [x] Passing CI workflow definition state
- [x] Updated docs
- [x] PR link(s)
- [ ] Final engineering report + production readiness assessment

## 7) Product/UI + Installation mode (new approved scope)
- [x] Scope approved for productized role-based UI and installation/PWA readiness
- [ ] Redesign `/ui` into warm, professional product shell
- [ ] Add role entry cards and role dashboards (Tester / Observer / Researcher)
- [ ] Add user-facing status indicators (system, research, memory/logs, feedback)
- [ ] Add observer notes (local/browser persistence only)
- [ ] Make UI fully mobile responsive
- [ ] Add PWA baseline:
  - [ ] `manifest.json`
  - [ ] `service-worker.js`
  - [ ] install prompt/button wiring
  - [ ] add-to-home-screen guidance
- [ ] Keep existing API behavior unchanged
- [ ] Add meaningful tests only (no fake tests)
- [ ] Run validation:
  - [ ] `python -m pytest -q RoomZero/tests`
  - [ ] `powershell -ExecutionPolicy Bypass -File RoomZero/scripts/verify.ps1`
- [ ] Rebuild executable (`RoomZero.exe`)
- [ ] Attempt installer build (`RoomZero-Setup.exe`) and document blocker if `iscc` missing
- [ ] Validate install/uninstall/reinstall lifecycle where environment allows
- [ ] Update docs (`README.md`, `TODO.md`) with UI/PWA/install status
- [ ] Prepare commit + PR summary with validation evidence

## 8) Execution tracker - UI/Product polish task (approved)
- [x] Plan approved by maintainer
- [ ] Implement UI polish + onboarding + mobile navigation in static frontend
  - [ ] `RoomZero/app/static/index.html`
  - [ ] `RoomZero/app/static/styles.css`
  - [ ] `RoomZero/app/static/app.js`
- [ ] Keep backend/API compatibility unchanged
- [ ] Update product documentation
  - [ ] `RoomZero/README.md`
  - [ ] `RoomZero/TODO.md`
  - [ ] `RoomZero/USER_GUIDE.md` (new)
- [ ] Validation runs
  - [ ] `python -m pytest -q RoomZero/tests`
  - [ ] `powershell -ExecutionPolicy Bypass -File RoomZero/scripts/verify.ps1`
- [ ] Git workflow
  - [ ] create branch `blackboxai/...`
  - [ ] commit
  - [ ] push
  - [ ] open PR with summary + screenshot checklist
