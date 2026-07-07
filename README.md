# EPS Route-Checker 🐛

Plan and check running/cycling routes around Berlin & Brandenburg that avoid reported
**Eichenprozessionsspinner** (oak processionary moth) trees — whose caterpillar hairs
cause skin, eye and airway irritation.

The whole app is a single static HTML file ([`eps-checker.html`](eps-checker.html)) that:

- pulls crowdsourced EPS reports from the public Supabase behind
  [eichenprozessionsspinner-melden.de](https://eichenprozessionsspinner-melden.de),
- **🔍 GPX prüfen** — upload a track and see the closest approach to any reported tree, and
- **🗺️ Route planen** — click waypoints on the map and get an EPS-avoiding route
  (foot or bike) with elevation, exportable as GPX for Strava/Garmin.

Routing/avoidance is done by a self-hosted [Valhalla](https://github.com/valhalla/valhalla)
instance; without it, the analysis (check) features still work.

## Run locally

```bash
# 1. routing backend (optional, needed for the detour / planning features)
brew install osmium-tool          # one-time
cd valhalla && make check         # safe: verifies Docker + osmium
make data && make up && make config   # WiFi only — downloads ~320 MB, builds tiles (~15 min)
cd ..

# 2. the app (serves static files + proxies /valhalla to :8002)
python3 serve.py                  # http://localhost:8000/eps-checker.html
```

See [`valhalla/README.md`](valhalla/README.md) for the routing backend details.

## Deployment

Pushing to `main` triggers [`.github/workflows/docker.yml`](.github/workflows/docker.yml):

1. builds & pushes two images to GHCR:
   - `eps-route-checker` — nginx serving the app + reverse-proxying `/valhalla`,
   - `eps-route-checker-valhalla` — Valhalla with the Berlin+Brandenburg tileset baked in,
2. redeploys the Portainer stack ([`docker-compose.prod.yml`](docker-compose.prod.yml)),
   served behind Traefik at **https://eps-route-checker.random.martintaraz.de**.

Required repo secrets: `PORTAINER_URL`, `PORTAINER_USERNAME`, `PORTAINER_PASSWORD`,
`PORTAINER_STACK_ID`, `PORTAINER_ENDPOINT_ID`. The Traefik `web` network must already exist.

> Data is crowdsourced and **not official** — "none nearby" means "none reported", not "none present".
