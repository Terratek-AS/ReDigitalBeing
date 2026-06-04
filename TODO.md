# M2.1.7 Docker Runtime Packaging for RoomZero Backend

- [x] Inspect backend entrypoint and dependency/runtime files
- [x] Add `RoomZero/Dockerfile`
- [x] Add root `docker-compose.yml`
- [x] Add root `.dockerignore`
- [x] Add root `.env.example`
- [x] Update `RoomZero/app/main.py` for env-aware platform DB path (additive, local-safe)
- [x] Update `RoomZero/README.md` with Docker usage docs
- [ ] Run `docker compose build`
- [ ] Run `docker compose up -d`
- [ ] Verify `GET /health` and `GET /ui`
- [ ] Check `docker compose logs`
- [ ] Run `docker compose down`
- [x] Run targeted pytest suite
- [x] Run git safety checks (ensure `RoomZero/data/platform/platform.sqlite` not staged)
- [ ] Commit if validation passes

> Note: Docker daemon was unavailable in this environment, so build/run was not executed here. `docker compose config` was validated successfully.
