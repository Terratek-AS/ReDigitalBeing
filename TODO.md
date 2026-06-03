# M2.1 TODO (Public backend integration + root documentation)

- [x] Add root `README.md` with canonical backend and roadmap sections
- [x] Add `RoomZero/app/static/config.js` with default local API base
- [x] Add `RoomZero/app/static/config.example.js` with production placeholder
- [x] Update `RoomZero/app/static/app.js` to use configurable `API_BASE_URL`
- [x] Update `RoomZero/app/static/index.html` to load `config.js` before `app.js` and improve links for Pages context
- [x] Add CORS middleware in `RoomZero/app/main.py` for approved origins
- [x] Add/update `RoomZero/DEPLOY_BACKEND.md` deployment documentation
- [x] Review `.github/workflows/deploy-pages.yml` and apply minimal update only if required
- [x] Run tests:
  - [x] `python -m pytest -q RoomZero/tests/test_memory.py RoomZero/tests/test_safety.py RoomZero/tests/test_llm_intents.py RoomZero/tests/test_research_jobs.py`
  - [x] `python -m pytest -q RoomZero/tests/test_m2_platform.py`
  - [x] Combined rerun: `python -m pytest -q RoomZero/tests/test_memory.py RoomZero/tests/test_safety.py RoomZero/tests/test_llm_intents.py RoomZero/tests/test_research_jobs.py RoomZero/tests/test_m2_platform.py` (20 passed)
- [x] Run verification script:
  - [x] `powershell -ExecutionPolicy Bypass -File RoomZero/scripts/verify.ps1`
- [x] Run startup smoke test:
  - [x] `cd RoomZero && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
  - [x] Verify `/health`
  - [x] Verify `/ui`
  - [x] Verify frontend reads `API_BASE_URL` from `config.js` (static code path + asset checks)
- [x] Confirm Pages shell remains deployable
- [x] Final report with: files changed, README status, backend config method, CORS behavior, deployment docs, test results, blocked/skipped checks, limitations, recommended M3 plan

## M2.1 Post-Commit Manual Validation Required

- Full frontend browser/E2E verification on `/ui` remains required because browser automation was disabled in this environment.
- Live GitHub Pages runtime/console verification remains required because browser automation was disabled in this environment.
- Explicit CORS origin matrix remains required; prior inline shell attempts were blocked by PowerShell/cmd quoting/parsing issues.
- No known application regression was found in automated backend/API validation.
- Current automated validation result: **20 passed** (combined pytest run).
