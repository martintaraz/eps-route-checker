# Static web app (single HTML file) served by nginx, which also reverse-proxies
# /valhalla/ to the routing backend so the browser talks to it same-origin.
FROM nginx:alpine
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY eps-checker.html /usr/share/nginx/html/index.html
# bundled demo track (the app fetches it by name on load)
COPY ["HPI - Teltow - Brandenburg Gate .gpx", "/usr/share/nginx/html/HPI - Teltow - Brandenburg Gate .gpx"]
EXPOSE 80
