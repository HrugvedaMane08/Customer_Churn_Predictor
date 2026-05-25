# ==========================================
# Stage 1: Build the static Next.js frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend

# Copy frontend package configuration
COPY frontend/package*.json ./

# Install npm dependencies
RUN npm ci

# Copy the rest of the frontend source code
COPY frontend/ ./

# Disable Next.js telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# Compile and statically export Next.js frontend (generates /frontend/out)
RUN npm run build

# ==========================================
# Stage 2: Build python backend dependencies and package
# ==========================================
FROM python:3.10-slim AS backend-builder
WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system compilation tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy files needed for dependencies installation
COPY requirements.txt setup.py /build/
COPY src/ /build/src/

# Install python dependencies and local packaging
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    grep -v "\-e \." requirements.txt > temp_requirements.txt && \
    pip install --no-cache-dir -r temp_requirements.txt && \
    pip install --no-cache-dir .

# ==========================================
# Stage 3: Final minimal production image
# ==========================================
FROM python:3.10-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

WORKDIR /app

# Create a non-privileged system user for running the service
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /sbin/nologin appuser

# Copy virtual environment from builder stage
COPY --from=backend-builder /opt/venv /opt/venv

# Copy backend source code and FastAPI app
COPY app/ /app/app/
COPY src/ /app/src/

# Copy statically compiled frontend from Stage 1 into the static root path
COPY --from=frontend-builder /frontend/out/ /app/frontend/out/

# Pre-create artifacts and logs directories to ensure correct permissions for non-root user
RUN mkdir -p /app/artifacts /app/logs && \
    chown -R appuser:appgroup /app

# Expose default port
EXPOSE 8000

# Switch to non-root user
USER appuser

# Start FastAPI server on port $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
