# M2.1.3 TODO (Rename public Pages identity: Terratek -> Knoksen)

- [ ] Update public preview URL references to `https://knoksen.github.io/ReDigitalBeing/` in approved docs/files
- [ ] Update backend CORS allowlist origin in `RoomZero/app/main.py` to `https://knoksen.github.io`
- [ ] Update validation script references in `RoomZero/scripts/m2_1_1_validate.py`
- [ ] Review and update `RoomZero/README.md` and `RoomZero/PRESENTATION.md` only if relevant references exist
- [ ] Confirm `.github/workflows/deploy-pages.yml` does not require changes (only if hardcoded terratek-as exists)
- [ ] Run validation commands:
  - [ ] `git diff --name-only`
  - [ ] `git status --short`
  - [ ] `python -m pytest -q RoomZero/tests/test_memory.py RoomZero/tests/test_safety.py RoomZero/tests/test_llm_intents.py RoomZero/tests/test_research_jobs.py RoomZero/tests/test_m2_platform.py`
- [ ] Run local smoke (if possible):
  - [ ] `cd RoomZero && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
  - [ ] Verify `GET /health`
  - [ ] Verify `GET /ui`
- [ ] Stage only intentional files (exclude runtime/data paths)
- [ ] Commit: `Rename public Pages identity to Knoksen`
- [ ] Push if remote is correct
- [ ] Final report with requested checklist + ownership/deployment-target caveat

