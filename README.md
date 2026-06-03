# ReDigitalBeing / RoomZero

RoomZero is the canonical backend “simulation room brain” of the ReDigitalBeing project.

- **RoomZero/FastAPI is the official system of record** for intelligence behavior, memory flows, research workflows, invitations, users, audit logs, and simulation operations.
- The GitHub Pages site is a **public static chamber console shell**. It only becomes functional when connected to a reachable RoomZero backend API.

Repository: https://github.com/Terratek-AS/ReDigitalBeing

## Current Status

- M1, M1.5, and M2 foundations are implemented in the RoomZero backend and UI.
- Public GitHub Pages preview exists:
  - https://terratek-as.github.io/ReDigitalBeing
- Root documentation is now established here for project orientation and backend integration guidance.
- M2.1 focuses on making the static frontend safely configurable for a public backend deployment.

## GitHub Pages Preview

Preview URL:  
https://terratek-as.github.io/ReDigitalBeing

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
