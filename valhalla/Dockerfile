# Production Valhalla image with the Berlin + Brandenburg tileset BAKED IN.
#
# The gis-ops entrypoint (`run.sh build_tiles`) builds tiles then serves. With
# serve_tiles=False it builds and EXITS, so we can bake the whole tileset at image
# build time — the running container then just serves, with no OSM download or tile
# build at startup. Heavy first CI build (~15–20 min); cached by buildx afterwards.
#
# Extracts are merged into ONE .osm.pbf first: Valhalla crashes building from
# multiple pbfs (github.com/valhalla/valhalla/issues/3925), and the Potsdam→Berlin
# corridor spans both the Brandenburg and (separately-split) Berlin extracts.
FROM ghcr.io/gis-ops/docker-valhalla/valhalla:latest

# Overridable so the image can be test-built against a tiny region (e.g. Bremen).
ARG PBF1_URL=https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf
ARG PBF2_URL=https://download.geofabrik.de/europe/germany/brandenburg-latest.osm.pbf

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends osmium-tool curl ca-certificates jq \
 && rm -rf /var/lib/apt/lists/*

# download both extracts and merge into a single pbf
RUN curl -fL -o /tmp/a.osm.pbf "$PBF1_URL" \
 && curl -fL -o /tmp/b.osm.pbf "$PBF2_URL" \
 && osmium merge /tmp/a.osm.pbf /tmp/b.osm.pbf -o /custom_files/data.osm.pbf --overwrite \
 && rm -f /tmp/a.osm.pbf /tmp/b.osm.pbf \
 && chown -R 59999:59999 /custom_files

USER 59999
# build tiles + elevation now, then raise the exclude-polygon limit the detour feature needs
RUN serve_tiles=False build_elevation=True build_admins=True /valhalla/scripts/run.sh build_tiles \
 && jq '.service_limits.max_exclude_polygons_length=200000' /custom_files/valhalla.json > /tmp/v.json \
 && mv /tmp/v.json /custom_files/valhalla.json

# runtime: serve the prebuilt tiles, never rebuild or hit the network
ENV serve_tiles=True use_tiles_ignore_pbf=True build_elevation=False build_admins=False force_rebuild=False
EXPOSE 8002
