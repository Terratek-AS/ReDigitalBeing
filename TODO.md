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

## M2.1.1 Manual Validation Result (Executed)

- [x] Test local `/ui` in regular browser context (HTTP runtime validation)
  - Result: `http://127.0.0.1:8000/ui` returned **200**
  - Supporting check: `/health` returned **200** with `{"status":"ok","name":"Eir","safe_mode":true}`
  - Note: interactive browser-console capture was blocked in this environment because browser automation is disabled.

- [x] Test GitHub Pages runtime: `https://terratek-as.github.io/ReDigitalBeing`
  - Result: base URL and expected static assets returned **404** during validation:
    - `/ReDigitalBeing/` → 404
    - `/ReDigitalBeing/index.html` → 404
    - `/ReDigitalBeing/config.js` → 404
    - `/ReDigitalBeing/app.js` → 404
    - `/ReDigitalBeing/manifest.json` → 404
  - Conclusion: GitHub Pages runtime is currently not reachable at the tested path.

- [x] Test CORS using simple standalone script file
  - Script used: `RoomZero/scripts/m2_1_1_validate.py`
  - Preflight (`OPTIONS /health`) results:
    - Allowed origins tested:
      - `http://127.0.0.1:8000` → 200
      - `http://localhost:8000` → 200
      - `https://terratek-as.github.io` → 200
    - Disallowed origins tested:
      - `https://evil.example.com` → 400
      - `https://randomdomain.com` → 400
  - `GET /health` returned 200 for all tested origins; browser-enforced CORS depends on presence/validation of CORS headers in browser runtime.
  - Header observation in this CLI check: `Access-Control-Allow-Origin` was not surfaced by `urllib` response handling in this run.

- [x] Document validation results (including console errors if any)
  - Console error capture status: not available due to disabled browser automation.
  - Command/runtime issues observed during validation:
    - Port 8000 bind conflict (`WinError 10048`) indicates another local process already using the port.
    - Inline multi-line Python command attempts failed due to shell quoting; resolved by using standalone script file.

- [x] Include final git status

## M2.1.2 GitHub Pages Deployment Repair

- [x] Root cause identified
  - Pages workflow packaged UI into `out/static/*` and used a redirecting root `index.html`.
  - Expected runtime requires app shell and assets directly at artifact root for repo subpath URL:
    - `/ReDigitalBeing/index.html`
    - `/ReDigitalBeing/app.js`
    - `/ReDigitalBeing/config.js`
    - `/ReDigitalBeing/manifest.json`

- [x] Workflow repair applied (minimal)
  - Updated `.github/workflows/deploy-pages.yml`:
    - removed nested `out/static/` packaging
    - removed redirect shim `out/index.html`
    - now copies `RoomZero/app/static/*` directly into `out/`

- [x] Local artifact structure validation
  - Validation script: `RoomZero/scripts/m2_1_2_validate_artifact.py`
  - Command: `python RoomZero/scripts/m2_1_2_validate_artifact.py`
  - Result:
    - `index.html OK`
    - `app.js OK`
    - `config.js OK`
    - `manifest.json OK`
    - `styles.css OK`
    - `service-worker.js OK`

- [ ] Push + live Pages verification pending
  - After push/workflow run, verify:
    - `https://terratek-as.github.io/ReDigitalBeing/`
    - `https://terratek-as.github.io/ReDigitalBeing/index.html`
    - `https://terratek-as.github.io/ReDigitalBeing/app.js`
    - `https://terratek-as.github.io/ReDigitalBeing/config.js`
    - `https://terratek-as.github.io/ReDigitalBeing/manifest.json`
