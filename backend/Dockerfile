# Backend — FastAPI + SQLite
# Build context is the repo root (needs both backend/ and content/).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Working dir holds the importable `app` package: /app/backend/app/...
WORKDIR /app/backend

# Install deps first for layer caching.
COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# App code and content. config.py resolves CONTENT_DIR to /app/content and
# DB_PATH (overridable via env) for the SQLite progress file.
COPY backend/ ./
COPY content/ /app/content/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
