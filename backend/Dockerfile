# ==========================================
# CareerLoom Backend Service Dockerfile
# Python 3.12 Slim ASGI Application
# ==========================================

FROM python:3.12-slim AS builder

WORKDIR /app

# Install build essentials if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime image
FROM python:3.12-slim

WORKDIR /app

# Create non-root system user for security
RUN groupadd -r careerloom && useradd -r -g careerloom -d /app careerloom

# Copy installed wheels from builder
COPY --from=builder /root/.local /home/careerloom/.local
ENV PATH=/home/careerloom/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Copy backend application source code
COPY backend /app/backend
COPY scripts /app/scripts

# Create data directory with proper permissions
RUN mkdir -p /app/backend/data && chown -R careerloom:careerloom /app

USER careerloom

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/jobs/stats')" || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
