# EPS Route-Checker 🐛

Check a running/cycling GPX track around Berlin & Brandenburg against reported
**Eichenprozessionsspinner** (oak processionary moth) trees — whose caterpillar hairs
cause skin, eye and airway irritation — and share the result by link.

The frontend is a single static HTML file ([`eps-checker.html`](eps-checker.html)) that:

- pulls crowdsourced EPS reports from the public Supabase behind
  [eichenprozessionsspinner-melden.de](https://eichenprozessionsspinner-melden.de),
- loads a GPX track (bundled default: the Berlin **100 Meilen** ultra) and shows the closest
  approach to any reported tree, plus an adjustable **Warnradius**,
- draws **only the trees near the track** (orange nearby, red inside the warn radius) — no
  region-wide clutter, and
- **🔗 shares** a track + its findings via a short link `…/‹uuid›` backed by a tiny service.

## Architecture

- **web** ([`Dockerfile`](Dockerfile), [`docker/nginx.conf`](docker/nginx.conf)) — nginx serving
  the app, reverse-proxying `/api` to the backend, and serving `index.html` for `/‹uuid›` links.
- **backend** ([`backend/`](backend)) — dependency-free Python service storing shared GPX by
  UUID (`POST /api/routes`, `GET /api/routes/‹uuid›`) on a mounted volume.

## Run locally

```bash
# 1. share backend (stores shared GPX under ./data)
DATA_DIR=./data python3 backend/app.py        # :8080

# 2. the app (serves static files + proxies /api + /‹uuid› fallback)
python3 serve.py                              # http://localhost:8000/eps-checker.html
```

## Deployment

Pushing to `main` triggers [`.github/workflows/docker.yml`](.github/workflows/docker.yml):

1. builds & pushes two images to GHCR:
   - `eps-route-checker` — nginx serving the app + `/api` proxy + `/‹uuid›` fallback,
   - `eps-route-checker-backend` — the share service,
2. redeploys the Portainer stack ([`docker-compose.prod.yml`](docker-compose.prod.yml)),
   served behind Traefik at **https://eps-route-checker.random.martintaraz.de**.

Required repo secrets: `PORTAINER_URL`, `PORTAINER_USERNAME`, `PORTAINER_PASSWORD`,
`PORTAINER_STACK_ID`, `PORTAINER_ENDPOINT_ID`. The Traefik `web` network must already exist.

> Data is crowdsourced and **not official** — "none nearby" means "none reported", not "none present".
