# Valhalla routing backend (for detour suggestions)

The EPS Route-Checker uses a **local, self-hosted Valhalla** instance to compute
elevation-aware detours around reported infected trees. It's optional: without it,
the app still loads GPX tracks and reports closest-approach distances — only the
**"Umweg vorschlagen"** (suggest detour) button is disabled.

## ⚠️ Metered-connection warning

Bringing Valhalla up downloads a lot of data **once**:

| What | Size | When |
|------|------|------|
| Valhalla Docker image | ~hundreds of MB | first `make up` |
| Brandenburg OSM extract | ~250 MB | `make data` |
| Berlin OSM extract | ~70 MB | `make data` |

**Do not run `make data` or the first `make up` on a mobile / metered plan.**
`make check` is always safe — it uses no network.

## Usage

```bash
brew install osmium-tool   # one-time: needed to merge the two extracts
cd valhalla
make check     # safe: verifies Docker + osmium, prints what would be downloaded
# --- switch to unmetered WiFi before the next two steps ---
make data      # download Berlin + Brandenburg extracts (~320 MB) and merge into one file
make up        # pull image + build tiles (first run ~15 min), serve on :8002
make logs      # watch tile build progress
make status    # confirm it's live
make config    # once, after the build: raise the exclude-polygon limit (see below)
```

> **`make config`** raises Valhalla's `max_exclude_polygons_length` from the default
> 10 km to 200 km. The detour feature excludes a safe-zone around every reported tree
> along the route, whose combined circumference easily exceeds the default cap; without
> this the router rejects the request. The change is written into `valhalla.json` and
> persists across restarts, so it's a one-time step after the first tile build.

> **Why merge?** Valhalla crashes when building tiles from multiple `.osm.pbf`
> files ([issue #3925](https://github.com/valhalla/valhalla/issues/3925)). The
> Potsdam→Berlin corridor spans both the Brandenburg and (separately-split) Berlin
> extracts, so `make data` merges them into a single `bb-merged.osm.pbf` with
> `osmium merge` before tiling.

Once `make status` shows a JSON body, reload `eps-checker.html` — the detour
button becomes active (it probes `http://localhost:8002/status` on load).

## Endpoints used by the frontend

- `POST /route` — detour geometry with top-level `exclude_polygons` (tree buffers)
  and `costing: pedestrian | bicycle`.
- `POST /height` — elevation samples for a route shape → ascent/descent for ranking.

`build_elevation=True` (set in the Makefile) enables the Skadi `/height` service.

## Teardown

```bash
make down      # stop & remove the container (keeps downloaded tiles)
make clean     # also delete downloaded extracts/tiles
```
