# Valhalla routing backend for the EPS Route-Checker
#
# ⚠️  METERED-CONNECTION WARNING
# `make data` and the first `make up` download hundreds of MB (OSM extracts +
# the Valhalla Docker image). DO NOT run them on a mobile / metered plan.
# `make check` is safe: it only inspects your setup and prints sizes.

IMAGE      := ghcr.io/gis-ops/docker-valhalla/valhalla:latest
PORT       := 8002
DATA_DIR   := custom_files
CONTAINER  := eps-valhalla

# Geofabrik extracts — the HPI→Brandenburg-Gate corridor spans both Brandenburg
# and the separately-split Berlin extract, so we need both.
BB_URL     := https://download.geofabrik.de/europe/germany/brandenburg-latest.osm.pbf
BE_URL     := https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf

.PHONY: check data up status logs down clean

## check — safe, no network: verify Docker + report what WOULD be downloaded
check:
	@echo "== EPS Valhalla setup check =="
	@command -v docker >/dev/null 2>&1 && echo "✓ docker found: $$(docker --version)" \
		|| { echo "✗ docker NOT found — install Docker Desktop first"; exit 1; }
	@echo ""
	@echo "The following are downloaded by 'make data' / first 'make up':"
	@printf "  • Docker image : %s  (~hundreds of MB)\n" "$(IMAGE)"
	@printf "  • Brandenburg  : %s  (~250 MB)\n" "$(BB_URL)"
	@printf "  • Berlin       : %s  (~70 MB)\n" "$(BE_URL)"
	@echo ""
	@command -v osmium >/dev/null 2>&1 && echo "✓ osmium found (needed to merge extracts)" \
		|| echo "⚠️  osmium NOT found — run 'brew install osmium-tool' before 'make data'"
	@if [ -f "$(DATA_DIR)/bb-merged.osm.pbf" ]; then \
		echo "✓ merged extract already present in $(DATA_DIR)/ — no download needed"; \
	else \
		echo "⚠️  extract NOT present. Run 'make data' ONLY on unmetered WiFi."; \
	fi

## data — DOWNLOADS extracts (~320 MB) and MERGES them into one file. WiFi only!
# Valhalla crashes on multi-.osm.pbf builds (issue #3925), so we merge Berlin +
# Brandenburg into a single bb-merged.osm.pbf with osmium before tiling.
data:
	@echo "⚠️  This downloads ~320 MB of OSM data. Ctrl-C now if you are on mobile."
	@sleep 4
	@command -v osmium >/dev/null 2>&1 || { echo "✗ osmium not found — run 'brew install osmium-tool' first"; exit 1; }
	@mkdir -p $(DATA_DIR)
	curl -L --fail -o $(DATA_DIR)/brandenburg-latest.osm.pbf $(BB_URL)
	curl -L --fail -o $(DATA_DIR)/berlin-latest.osm.pbf $(BE_URL)
	@echo "merging into a single extract (avoids multi-pbf build crash)…"
	osmium merge $(DATA_DIR)/berlin-latest.osm.pbf $(DATA_DIR)/brandenburg-latest.osm.pbf -o $(DATA_DIR)/bb-merged.osm.pbf --overwrite
	rm -f $(DATA_DIR)/berlin-latest.osm.pbf $(DATA_DIR)/brandenburg-latest.osm.pbf
	@echo "✓ merged extract ready at $(DATA_DIR)/bb-merged.osm.pbf"

## up — build tiles (first run, ~15 min) and serve on :$(PORT). Pulls image if missing (WiFi only first time).
up:
	@[ -f "$(DATA_DIR)/bb-merged.osm.pbf" ] || { echo "✗ no extract — run 'make data' first (on WiFi)"; exit 1; }
	docker run -d --name $(CONTAINER) -p $(PORT):8002 \
		-v $(PWD)/$(DATA_DIR):/custom_files \
		-e serve_tiles=True -e build_elevation=True -e build_admins=True \
		$(IMAGE)
	@echo "Valhalla starting. First run builds tiles (~15 min). Watch: make logs"

## config — raise the exclude-polygon limit so detours can avoid many trees at once.
# Valhalla caps total exclude_polygons circumference at 10 km by default, which is too small
# when we exclude a safe-zone around every reported tree along a route. Run ONCE after the
# first `make up` tile build finishes (valhalla.json must exist), then it persists.
config:
	@[ -f "$(DATA_DIR)/valhalla.json" ] || { echo "✗ valhalla.json not built yet — wait for the 'make up' tile build to finish, then retry"; exit 1; }
	python3 -c "import json;f='$(DATA_DIR)/valhalla.json';d=json.load(open(f));d.setdefault('service_limits',{})['max_exclude_polygons_length']=200000;json.dump(d,open(f,'w'),indent=2);print('max_exclude_polygons_length -> 200000')"
	-docker restart $(CONTAINER)
	@echo "✓ limit raised and container restarted (give it a few seconds)"

## status — is it live?
status:
	@curl -s http://localhost:$(PORT)/status | head -c 400 || echo "not reachable"
	@echo ""

logs:
	docker logs -f $(CONTAINER)

down:
	-docker rm -f $(CONTAINER)

## clean — remove container AND downloaded tiles/extracts
clean: down
	rm -rf $(DATA_DIR)
