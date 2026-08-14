# Static web app (single HTML file) served by nginx, which also reverse-proxies /api/
# to the share backend and serves index.html for /<uuid> share links (SPA fallback).
FROM nginx:alpine
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY eps-checker.html /usr/share/nginx/html/index.html
# bundled default track (the app fetches it by name on load)
COPY 100Meilen_2026-1.gpx /usr/share/nginx/html/100Meilen_2026-1.gpx
EXPOSE 80
