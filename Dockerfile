# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python API + static UI
FROM python:3.11-slim AS runtime

# Optional browser target: docker build --build-arg ENABLE_BROWSER=true -t cleancrawl:browser .
ARG ENABLE_BROWSER=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

ENV PORT=8000 \
    ENABLE_BROWSER=false \
    DATABASE_URL=sqlite:///data/cleancrawl.db

RUN mkdir -p /app/data

# Playwright only when explicitly requested (doubles image size)
USER root
RUN if [ "$ENABLE_BROWSER" = "true" ]; then \
      pip install playwright && playwright install --with-deps chromium; \
    fi
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/health || exit 1

CMD uvicorn api.server:app --host 0.0.0.0 --port ${PORT}
