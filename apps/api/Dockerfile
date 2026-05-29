FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OCI_SENTINEL_DB_PATH=/app/data/oci-sentinelmesh.db
ENV OCI_SENTINEL_PERSISTENCE_ENABLED=true

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY apps ./apps
COPY packages ./packages

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
