# Deploy RoomZero Backend (M2.1)

RoomZero/FastAPI is the canonical backend (“simulation room brain”) for ReDigitalBeing.
The GitHub Pages frontend is a static shell and must connect to a reachable RoomZero backend API.

Recommended public backend URL placeholder:

- `https://roomzero-api.yourdomain.com`

---

## 1) Deployment targets overview

### Option A: VPS (systemd + uvicorn/gunicorn) — recommended baseline

Pros:
- Full control
- Predictable networking and storage
- Good fit for SQLite prototype phase

Cons:
- You manage OS patching, SSL, backups, process health

### Option B: Docker (single host or container platform)

Pros:
- Portable, reproducible runtime
- Easier migration between hosts/providers

Cons:
- Needs container ops basics
- Persistent volume setup required for data files

### Option C: Managed PaaS (Render / Fly.io / Railway style)

Pros:
- Fast setup
- Built-in deployment pipelines
- Auto TLS and health checks

Cons:
- SQLite persistence constraints depending on platform
- Possible cold starts / ephemeral filesystem defaults

---

## 2) Required environment and runtime notes

RoomZero can run without LLM key in local fallback mode.  
Optional variables:

- `OPENAI_API_KEY` (optional)
- `OPENAI_MODEL` (optional, default from app config)

Data storage:
- Current project uses local-first files and SQLite under `RoomZero/data/`
- Ensure persistent disk volume for production use
- Back up `RoomZero/data/` regularly

---

## 3) Health check endpoint

Use:

- `GET /health`

Expected:
- JSON response with system status and safe mode state

Example:

```bash
curl https://roomzero-api.yourdomain.com/health
```

---

## 4) CORS behavior (M2.1)

Configured allowlist currently includes:

- `http://127.0.0.1:8000`
- `http://localhost:8000`
- `https://terratek-as.github.io`

This supports:
- local UI and API on localhost
- GitHub Pages hosted shell at the Terratek org domain

### Tighten later (recommended)

For stricter production policy:
- keep only exact frontend origins in `allow_origins`
- remove localhost entries in hardened production environment if not needed
- avoid wildcard origins

---

## 5) VPS deployment example (systemd + uvicorn)

Assume app copied to `/opt/roomzero/ReDigitalBeing` and virtual env at `/opt/roomzero/venv`.

### Install dependencies

```bash
cd /opt/roomzero/ReDigitalBeing/RoomZero
python3 -m venv /opt/roomzero/venv
source /opt/roomzero/venv/bin/activate
pip install -r requirements.txt
```

### Test run

```bash
cd /opt/roomzero/ReDigitalBeing/RoomZero
/opt/roomzero/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### systemd unit example

`/etc/systemd/system/roomzero.service`:

```ini
[Unit]
Description=RoomZero FastAPI
After=network.target

[Service]
Type=simple
User=roomzero
WorkingDirectory=/opt/roomzero/ReDigitalBeing/RoomZero
Environment=PYTHONUNBUFFERED=1
# Optional:
# Environment=OPENAI_API_KEY=...
# Environment=OPENAI_MODEL=gpt-4o-mini
ExecStart=/opt/roomzero/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable roomzero
sudo systemctl start roomzero
sudo systemctl status roomzero
```

Add reverse proxy (nginx/caddy) for TLS and public domain routing.

---

## 6) Docker option (feasible baseline)

Example minimal `Dockerfile` strategy:
- base image: python slim
- copy `RoomZero/`
- install `requirements.txt`
- expose 8000
- start uvicorn `app.main:app`

Important:
- mount persistent volume for `RoomZero/data/`
- set environment variables via secret manager or runtime config

Example run pattern:

```bash
docker run -d \
  --name roomzero-api \
  -p 8000:8000 \
  -v /srv/roomzero-data:/app/RoomZero/data \
  -e OPENAI_API_KEY=... \
  roomzero-api:latest
```

---

## 7) PaaS notes (Render/Fly/Railway)

- Start command:
  - `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Ensure platform routes public HTTPS domain to service
- Configure health check path `/health`
- Verify persistent storage behavior:
  - if ephemeral disk only, move persistence to managed database/object storage before production scale

---

## 8) Connect GitHub Pages frontend to backend

In static UI config (`RoomZero/app/static/config.js`), set:

```js
window.ROOMZERO_CONFIG = {
  API_BASE_URL: "https://roomzero-api.yourdomain.com",
};
```

Then redeploy Pages static assets.

The frontend will route API calls to configured backend URL.

---

## 9) Post-deploy smoke checks

- `GET /health` returns `status: ok`
- `GET /ui` loads locally (for local backend mode)
- GitHub Pages shell loads and can call API endpoints via configured base URL
- CORS allows requests from approved frontend origin
