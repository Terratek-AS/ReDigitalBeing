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

## Task 16 — Add smooth UI/UX for user testing
- [ ] Add frontend files under app/static (index.html, styles.css, app.js)
- [ ] Add FastAPI routes/static mounting for /ui and /static
- [ ] Wire dashboard actions to existing tester/research/jobs/feedback/source endpoints
- [ ] Update README with UI usage section
- [ ] Run pytest and verify existing tests remain passing
- [ ] Provide UI walkthrough and example flows

## Task 17 — Create Windows installer
- [x] Create build_installer.ps1 to package RoomZero app for Windows
- [x] Create installer/RoomZero.iss Inno Setup script for Setup.exe generation
- [x] Update install.ps1 for installer-friendly bootstrap/use
- [x] Update README.md with Windows installer build/install instructions
- [ ] Build and verify installer artifact generation

## Task 18 — Delivery polish: UX quick links + presentation + publish
- [ ] Add quick-action buttons/links in UI for efficient user testing flows
- [ ] Add install quick links (Windows install/run/build installer/doc links) in UI
- [ ] Add mobile quick install/help section in UI
- [ ] Update README with quick testing/install/mobile guidance
- [ ] Create PRESENTATION.md
- [ ] Run pytest and verify all tests pass
- [ ] Commit, push branch `blackboxai/...`, and open PR to `knoksen/ReDigitalBeing`
