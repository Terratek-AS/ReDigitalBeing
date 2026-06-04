# M2.1.7 Docker Runtime Packaging for RoomZero Backend

- [x] Inspect backend entrypoint and dependency/runtime files
- [ ] Add `RoomZero/Dockerfile`
- [ ] Add root `docker-compose.yml`
- [ ] Add root `.dockerignore`
- [ ] Add root `.env.example`
- [ ] Update `RoomZero/app/main.py` for env-aware platform DB path (additive, local-safe)
- [ ] Update `RoomZero/README.md` with Docker usage docs
- [ ] Run `docker compose build`
- [ ] Run `docker compose up -d`
- [ ] Verify `GET /health` and `GET /ui`
- [ ] Check `docker compose logs`
- [ ] Run `docker compose down`
- [ ] Run targeted pytest suite
- [ ] Run git safety checks (ensure `RoomZero/data/platform/platform.sqlite` not staged)
- [ ] Commit if validation passes
