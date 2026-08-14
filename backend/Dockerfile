# Minimal dependency-free share backend (stores/serves shared GPX by UUID).
FROM python:3.12-alpine
WORKDIR /app
COPY app.py .
ENV DATA_DIR=/data PORT=8080
VOLUME /data
EXPOSE 8080
CMD ["python", "app.py"]
