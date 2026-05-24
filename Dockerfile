# ==========================================
# Stage 1: Build dependencies and package
# ==========================================
FROM python:3.10-slim AS builder

# Set shell and environment variables for build
SHELL ["/bin/bash", "-c"]
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install system compilation packages (e.g. gcc) in case they are needed for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy package dependency configurations
COPY requirements.txt setup.py /build/
COPY src/ /build/src/

# Install dependencies (ignoring local dev editable flag) and install the local 'src' package
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    grep -v "\-e \." requirements.txt > temp_requirements.txt && \
    pip install --no-cache-dir -r temp_requirements.txt && \
    pip install --no-cache-dir .

# ==========================================
# Stage 2: Final minimal production image
# ==========================================
FROM python:3.10-slim AS runner

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

WORKDIR /app

# Create a non-privileged system user for running the service
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /sbin/nologin appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy backend source code and FastAPI app
COPY app/ /app/app/
COPY src/ /app/src/

# Pre-create artifacts and logs directories to ensure correct permissions for non-root user
RUN mkdir -p /app/artifacts /app/logs && \
    chown -R appuser:appgroup /app

# Expose FastAPI default port
EXPOSE 8000

# Switch to non-root user
USER appuser

# Run application using Uvicorn, binding dynamically to $PORT (assigned by Railway)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
