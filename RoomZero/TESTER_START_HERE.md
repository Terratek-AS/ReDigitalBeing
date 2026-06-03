# TESTER_START_HERE

## 1) Open RoomZero

### Local (recommended for full API testing)
1. Open PowerShell in `RoomZero/`
2. Run:
   ```powershell
   .\install.ps1
   .\run.ps1
   ```
3. Open:
   - UI: `http://127.0.0.1:8000/ui`
   - Health: `http://127.0.0.1:8000/health`
   - API docs: `http://127.0.0.1:8000/docs`

### GitHub Pages (UI shell preview)
- URL: `https://terratek-as.github.io/ReDigitalBeing`
- Note: Pages provides frontend shell visibility. Full research/chat actions still depend on backend API availability.

---

## 2) Install RoomZero to Android Home Screen (PWA)

1. Open RoomZero in **Chrome on Android**.
2. Tap **Install RoomZero** if visible in the top area.
3. If not shown, open Chrome menu and tap **Add to Home screen**.
4. Confirm install and launch RoomZero from your phone home screen.

Expected result:
- RoomZero opens like an app in standalone mode.
- Basic shell loads even with unstable connectivity (offline fallback page is provided).

---

## 3) Submit research questions

In the **Researcher Dashboard**:
1. Enter a question.
2. Choose a category.
3. Set `submitted_by` (or keep default).
4. Tap **Submit**.

You can then use:
- **Refresh** to list current queued questions.
- Additional researcher tools for jobs and source queue actions.

---

## 4) Report bugs

When reporting a bug, include:
- Device + OS (e.g., Android 14, Pixel 7)
- Browser version (Chrome/Samsung Internet/Edge)
- URL used (`/ui` local or GitHub Pages URL)
- Exact steps to reproduce
- Expected vs actual behavior
- Screenshot/video if possible
- Console errors (if available)

Recommended bug format:
```text
Title:
Environment:
Steps:
Expected:
Actual:
Logs/Screenshots:
```

---

## 5) Current MVP limitations

- PWA install is the stable mobile MVP for this milestone.
- Full functionality requires backend API endpoints to be reachable.
- GitHub Pages deploy currently hosts frontend shell, not full backend runtime.
- Android APK is intentionally deferred pending a safe wrapper architecture decision (Capacitor/Tauri/etc.) and API-hosting strategy.
