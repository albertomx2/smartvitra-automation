FROM node:22-slim AS frontend-builder

WORKDIR /build/frontend

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci

COPY frontend/ ./

RUN npm run build


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        ffmpeg \
        libreoffice-impress \
        poppler-utils \
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install \
    --no-cache-dir \
    --upgrade pip \
    && pip install \
    --no-cache-dir \
    -r requirements.txt

COPY backend ./backend
COPY alembic ./alembic
COPY alembic.ini ./

COPY assets ./assets
COPY experiments ./experiments

COPY --from=frontend-builder \
    /build/frontend/dist \
    ./frontend/dist

EXPOSE 8080

CMD ["sh", "-c", "exec uvicorn backend.api.app:app --host 0.0.0.0 --port ${PORT}"]
