# RoomZero Build TODO

- [x] Create initial scaffold root and README
- [x] Create requirements.txt
- [x] Write full README.md
- [x] Write .env.example
- [x] Write .gitignore
- [x] Write install.ps1
- [x] Write run.ps1
- [x] Write app/config.py
- [x] Write app/models.py
- [x] Write app/persona.py
- [x] Write app/memory.py
- [x] Write app/state.py
- [x] Write app/safety.py
- [x] Write app/llm.py
- [x] Write app/logger.py
- [x] Write app/main.py
- [x] Write app/cli.py
- [x] Write data/persona/eir.json
- [x] Write data/state/eir_state.json
- [x] Write data/memory/episodic.json
- [x] Write data/memory/semantic.json
- [x] Write data/memory/procedural.json
- [x] Write data/logs/conversations.json
- [x] Write tests/test_memory.py
- [x] Write tests/test_safety.py

## Task 13 — Local intelligence and conversational identity
- [x] Add rule-based local intent engine in app/llm.py
- [x] Keep generate_reply backward compatible and update callers only if needed
- [x] Filter memory intent output to approved memories only
- [x] Improve Eir-specific default fallback tone
- [x] Add intent tests in tests/test_llm_intents.py
- [ ] Run pytest and verify all tests pass
- [ ] Provide changed files and CLI interaction examples

## Task 14 — Add RoomZero Research Network and Tester Invitation System
- [x] Update app/config.py with testers/research/feedback/sources directories and file constants
- [x] Extend app/models.py with tester, research, feedback, source, and endpoint request/response models
- [x] Create app/testers.py with invite, registration, role-permission, and tester management functions
- [x] Create app/research.py with question queue, status lifecycle, answering, approval, and knowledge base functions
- [x] Create app/feedback.py with feedback submission, listing, summarization, and stats
- [x] Create app/sources.py with source queue, approval flow, and reliability scoring
- [x] Create new data JSON files under data/testers, data/research, data/feedback, data/sources
- [x] Update app/main.py with tester/research/feedback/source endpoints and chat pipeline extension for optional tester_id
- [ ] Update app/cli.py with admin commands for invite/research/knowledge/feedback/sources moderation
- [ ] Add tests/test_testers.py
- [ ] Add tests/test_research.py
- [ ] Add tests/test_feedback.py
- [ ] Add tests/test_sources.py
- [ ] Update README.md with RoomZero Research Network section and workflows
- [ ] Run pytest and keep existing tests passing while adding new test coverage
- [ ] Provide changed files, new endpoints, example commands, and example API payloads

## Task 15 — Add Continuous Research Update Loop
- [x] Extend app/models.py with research job models/status/request schemas
- [x] Create app/research_jobs.py with manual/local job lifecycle and placeholder question generation
- [x] Add research jobs endpoints in app/main.py
- [x] Add research jobs CLI commands in app/cli.py
- [ ] Add tests for research jobs flow
- [ ] Update README.md with continuous research update loop details
- [ ] Run pytest
- [ ] Provide changed files and usage examples

## Task 16 — Advanced UI/UX for user testing dashboard
### A) UX architecture and navigation
- [ ] Define primary user journeys (invite tester, run research jobs, submit feedback, approve sources)
- [ ] Reorganize dashboard information hierarchy to reduce action depth
- [ ] Add persistent top navigation and contextual action zones
- [ ] Add clear section headers, helper text, and progressive disclosure for advanced actions

### B) Visual design system
- [ ] Introduce consistent spacing, typography scale, and component sizing tokens
- [ ] Standardize button hierarchy (primary/secondary/tertiary/destructive)
- [ ] Add status color semantics for success/warning/error/info with readable contrast
- [ ] Refine card/table/form components for visual consistency and scanability

### C) Interaction quality
- [ ] Add loading states (skeletons/spinners) for async operations
- [ ] Add empty states with next-step guidance for first-time users
- [ ] Add inline validation and actionable error messages on forms
- [ ] Add success confirmations/toasts for completed actions
- [ ] Add keyboard-friendly interactions for frequent actions

### D) Accessibility and responsiveness
- [ ] Ensure keyboard navigation and visible focus states across interactive elements
- [ ] Improve semantic HTML/ARIA landmarks in app/static/index.html
- [ ] Validate WCAG-oriented color contrast for text and controls
- [ ] Optimize layouts for desktop/tablet/mobile breakpoints
- [ ] Ensure touch-friendly hit targets for mobile testing operations

### E) Functional wiring and testability
- [ ] Wire all dashboard controls to existing tester/research/jobs/feedback/source endpoints
- [ ] Add global API error boundary/handler in frontend logic
- [ ] Add lightweight frontend smoke test checklist for critical user flows
- [ ] Update README with advanced UI/UX usage and flow walkthrough

### F) Acceptance criteria (UI/UX)
- [ ] Invite-to-chat flow can be completed end-to-end from `/ui` without API docs
- [ ] Research job create/list/run flow is discoverable in <= 3 interactions per task
- [ ] Feedback and source moderation actions provide clear state/result feedback
- [ ] Mobile view remains usable for quick admin/testing actions
- [ ] Existing backend tests continue passing after UI changes (`pytest`)

## Task 17 — Windows installer hardening and verification
### A) Build pipeline
- [x] Create build_installer.ps1 to package RoomZero app for Windows
- [x] Create installer/RoomZero.iss Inno Setup script for Setup.exe generation
- [x] Update install.ps1 for installer-friendly bootstrap/use
- [x] Update README.md with Windows installer build/install instructions
- [ ] Run full build chain: `.\install.ps1 -WithBuilder` -> `.\build_installer.ps1` -> `iscc .\installer\RoomZero.iss`

### B) Installer QA on Windows
- [ ] Verify artifact output exists at expected paths (`dist\RoomZero\` and `dist\installer\RoomZero-Setup.exe`)
- [ ] Validate clean-machine installation flow (no pre-existing venv or Python assumptions)
- [ ] Verify Start Menu/Desktop shortcuts and uninstall entry creation
- [ ] Validate first-run behavior post-install (app starts, `/health` responds, `/ui` loads)
- [ ] Validate uninstall flow removes app files and leaves user data policy as documented
- [ ] Test upgrade path (install older build -> install newer build -> verify settings/data expectations)

### C) Security, trust, and documentation
- [ ] Document SmartScreen/signing expectations for unsigned internal builds
- [ ] Add release notes template for installer changes and known issues
- [ ] Add rollback/recovery instructions for failed install or failed first run
- [ ] Align README + PRESENTATION install wording with verified installer behavior

### D) Acceptance criteria (Windows install)
- [ ] A non-dev Windows user can install, launch, and access `/ui` with setup docs only
- [ ] Installer/uninstaller flows execute without manual file surgery
- [ ] Build and installer steps are reproducible by another team member on Windows
- [ ] Final installer verification evidence captured (logs/screenshots/checklist)

## Task 18 — Delivery polish: UX quick links + presentation + publish
- [ ] Add quick-action buttons/links in UI for efficient user testing flows
- [ ] Add install quick links (Windows install/run/build installer/doc links) in UI
- [ ] Add mobile quick install/help section in UI
- [ ] Update README with quick testing/install/mobile guidance
- [ ] Create PRESENTATION.md
- [ ] Run pytest and verify all tests pass
- [ ] Commit, push branch `blackboxai/...`, and open PR to `knoksen/ReDigitalBeing`
