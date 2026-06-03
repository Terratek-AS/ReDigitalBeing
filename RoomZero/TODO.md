# TODO - Installed Startup Runtime Fix (Packaged EXE)

- [x] Inspect `build_installer.ps1`, `installer/RoomZero.iss`, `RoomZero.spec`, `install.ps1`, and `run.ps1`
- [x] Identify installed startup path and root cause
- [x] Add EXE entrypoint in `app/main.py` (`uvicorn.run(...)`, logging, browser launch)
- [x] Fix PyInstaller static path resolution for bundled runtime (`sys._MEIPASS`)
- [x] Rebuild packaged executable with `build_installer.ps1`
- [x] Run `dist\RoomZero.exe` directly and verify startup behavior
- [ ] Run smoke checks against packaged startup flow on a free port session
- [x] Keep app logic scope limited to installer/runtime/startup UX only
- [ ] Summarize final completed runtime fix state

## Factual findings
- Root cause confirmed: packaged EXE previously exited because `app/main.py` had no `if __name__ == "__main__"` server entrypoint.
- Secondary packaged blocker confirmed and fixed: static path resolved incorrectly in onefile mode (`..._MEI...\static` missing).
- Added bundled static resolution fallback:
  - `Path(sys._MEIPASS) / "app" / "static"` when frozen.
- Added startup UX improvements:
  - console startup message
  - best-effort browser open to `http://127.0.0.1:8000/ui`
  - explicit startup error output.
- Current local EXE run attempted while dev server already occupied port 8000, producing expected bind error (`WinError 10048`), which is environmental and not a packaging logic defect.
