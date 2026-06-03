# RoomZero

## First Page — Release Overview

**RoomZero** is a local-first research platform for building persistent digital-being simulations with strong safety controls and transparent workflows.

This release introduces the first digital being, **Eir**, with:
- persistent memory layers
- persona continuity and emotional state modeling
- FastAPI + CLI interfaces for testing and operations
- structured research/testing pipelines
- safety boundaries and ethical constraints by default

Repository: https://github.com/Terratek-AS/ReDigitalBeing

## Project Description

RoomZero is a research prototype for a persistent digital being simulation system.  
Phase 1 creates the first digital being, **Eir**, with local-first memory, persona continuity, emotional state simulation, CLI/API interfaces, and safety boundaries.

## Important Ethical Warning

RoomZero does **not** claim true biological consciousness or scientifically proven sentience.  
Eir is a software simulation designed for research into:
- memory persistence
- personality continuity
- stateful interaction
- safe and controllable behavior

Use responsibly, especially when handling personal or sensitive data.

## Features (Phase 1)

- FastAPI backend
- CLI chat mode
- Persistent persona, memory, and emotional state
- Conversation logging
- Safety filtering and boundaries
- Local fallback response mode
- Optional OpenAI API mode using `.env`
- Modular architecture for future upgrades (vector DB/graph memory)

## Project Structure

```text
RoomZero/
  README.md
  requirements.txt
  .env.example
  .gitignore
  install.ps1
  run.ps1
  app/
    main.py
    cli.py
    config.py
    models.py
    persona.py
    memory.py
    state.py
    safety.py
    llm.py
    logger.py
  data/
    persona/eir.json
    state/eir_state.json
    memory/episodic.json
    memory/semantic.json
    memory/procedural.json
    logs/conversations.json
  tests/
    test_memory.py
    test_safety.py
```

## Install (Windows PowerShell)

From the `RoomZero` directory:

```powershell
.\install.ps1
```

Manual equivalent:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run FastAPI Server

```powershell
.\run.ps1
```

Manual equivalent:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then open:
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Build Windows Installer

### 1) Prepare environment

```powershell
.\install.ps1 -WithBuilder
```

### 2) Build packaged executable

```powershell
.\build_installer.ps1
```

This generates:

- `dist\RoomZero.exe`

### 3) Build Setup installer (.exe)

Install [Inno Setup](https://jrsoftware.org/isinfo.php), then run:

```powershell
iscc .\installer\RoomZero.iss
```

This generates:

- `dist\installer\RoomZero-Setup.exe`

You can distribute `RoomZero-Setup.exe` as the Windows installer.

## Run CLI Chat

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.cli
```

## CI and validation

The repository includes GitHub Actions workflows at `.github/workflows/ci.yml` and `.github/workflows/codeql.yml`.

The CI workflow is configured for pushes to `main`, `develop`, and `blackboxai/**` branches.

Validation tests for RoomZero are:
- `python -m pytest -q`
- `powershell -ExecutionPolicy Bypass -File .\scripts\verify.ps1`
- `powershell -ExecutionPolicy Bypass -File .\build_installer.ps1`

Dependabot configuration lives in `.github/dependabot.yml`.

## OpenAI API Key (Optional)

1. Copy `.env.example` to `.env`
2. Add your key:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

If no key is present, RoomZero uses local fallback responses.

## API Endpoints

Core:
- `GET /health`
- `GET /persona`
- `GET /state`
- `POST /chat`
- `POST /memory`
- `GET /memory/recent`
- `GET /logs/recent`
- `POST /admin/shutdown-safe-mode`

Research Network + Testing:
- Testers:
  - `POST /testers/invite`
  - `POST /testers/register`
  - `GET /testers`
  - `GET /testers/{tester_id}`
  - `POST /testers/{tester_id}/deactivate`
- Research Questions:
  - `POST /research/questions`
  - `GET /research/questions`
  - `GET /research/questions/{question_id}`
  - `POST /research/questions/{question_id}/answer`
  - `POST /research/questions/{question_id}/approve`
  - `POST /research/questions/{question_id}/reject`
  - `GET /research/knowledge`
  - `GET /research/knowledge/search`
- Sources:
  - `POST /sources/submit`
  - `GET /sources/queue`
  - `POST /sources/{source_id}/approve`
  - `POST /sources/{source_id}/reject`
  - `GET /sources/approved`
- Feedback:
  - `POST /feedback/session`
  - `GET /feedback`
  - `GET /feedback/stats`
- Continuous Research Jobs (manual/local mode):
  - `POST /research/jobs`
  - `GET /research/jobs`
  - `POST /research/jobs/{job_id}/run`
  - `POST /research/jobs/{job_id}/pause`
  - `POST /research/jobs/{job_id}/activate`

## Behavior Rules in Chat Flow

When a user message arrives:
1. Load persona (Eir)
2. Load recent memories
3. Load emotional state
4. Apply safety checks
5. Build system context
6. Use OpenAI mode if configured, else local fallback mode
7. Log conversation
8. Update emotional state slightly
9. Store new memory **only** when user explicitly says “remember” or `/memory` is called

## RoomZero Research Network

RoomZero now supports an invite-based research and beta-testing layer for Eir while keeping core persona, personal memory, and approved knowledge protected.

### Invite-based testing

Roles:
- observer: chat
- tester: chat, submit_feedback
- researcher: chat, submit_feedback, submit_research_question, submit_source
- reviewer: researcher permissions + review_research + approve_sources
- admin: full permissions

Testers are managed via invite codes and consent-based registration. Tester messages can be tracked without automatically writing into personal memory.

### Research question workflow

1. Submit research question (`submitted`)
2. Review and answer (`under_review` / `answered`)
3. Approve to move summary/answer into approved knowledge (`approved`)
4. Or reject/archive (`rejected` / `archived`)

Unreviewed questions and answers stay in queue and are not treated as approved knowledge.

### Source approval workflow

1. Submit source into queue (`submitted`)
2. Reviewer evaluates reliability and relevance
3. Approve into approved sources (`approved`) or reject (`rejected`)
4. Optional `needs_review` status for triage

Reliability score guidance:
- peer-reviewed papers: 9–10
- official docs: 8–10
- university/research institutions: 8–10
- reputable technical articles: 6–8
- blogs/opinions: 3–6
- unknown sources: 1–4

### Feedback workflow

Session feedback captures realism/coherence/memory/emotional presence/ethical safety/usefulness/uncanny/trust scores plus free text and suggestions. Stats endpoints summarize aggregate signals for iterative model behavior improvements.

### Continuous Research Update Loop (manual/local mode)

Research jobs can be created and run locally to generate structured placeholder tasks/questions for reviewers, without fabricating external findings.

Current mode:
- no external API calls yet
- generates safe placeholder research questions
- updates job run timestamps/status lifecycle

Planned connectors:
- arXiv, PubMed, Semantic Scholar, GitHub, official docs, RSS, and curated manual source lists

### Privacy and safety defaults

- local-first JSON storage
- no direct tester edits to core persona/memory/approved knowledge
- reviewer-controlled promotion into approved knowledge
- explicit consent required for tester registration and sensitive memory flows

## Roadmap

### Phase 1B
- richer emotional modeling
- confidence/relevance scoring improvements
- better semantic extraction and tagging
- memory decay + reinforcement mechanics
- optional ChromaDB/Qdrant adapters

### Phase 1C
- voice pipeline (STT/TTS)
- Unreal Engine bridge
- sensor/event input adapters
- multi-agent room simulation primitives

## Execution Plan Snapshot (Windows Install + Advanced UI/UX)

This snapshot mirrors the actionable checklist in `TODO.md` for delivery readiness.

### Advanced UI/UX workstreams
- UX architecture and navigation
  - define primary user journeys
  - reduce action depth for tester/research/feedback/source tasks
  - improve section hierarchy and contextual actions
- Visual design system consistency
  - standard spacing/typography/component hierarchy
  - semantic status colors and clear button hierarchy
- Interaction quality
  - loading, empty, success, and error states
  - inline validation and clearer user feedback loops
- Accessibility and responsiveness
  - keyboard/focus behavior, semantic landmarks, contrast checks
  - mobile-first usability for quick admin/testing actions
- Functional wiring and acceptance
  - ensure dashboard controls map cleanly to existing API endpoints
  - verify critical flows can be completed from `/ui` without relying on `/docs`

### Windows installer hardening workstreams
- Build chain verification
  - run and validate full chain:
    - `.\install.ps1 -WithBuilder`
    - `.\build_installer.ps1`
    - `iscc .\installer\RoomZero.iss`
- Installer QA on Windows
  - clean-machine install validation
  - first-run checks (`/health`, `/ui`)
  - uninstall and upgrade-path behavior checks
- Trust and release readiness
  - SmartScreen/signing expectations for unsigned builds
  - rollback guidance and release-note discipline
- Acceptance criteria
  - non-dev installability from docs
  - reproducible build/install flow by another team member
  - checklist/log evidence for final verification

## Safety and Data Defaults

- Local data storage by default (JSON files under `data/`)
- No hardcoded secrets
- Human override is respected
- Eir avoids claims of proven consciousness
- Sensitive memory should require explicit user consent
