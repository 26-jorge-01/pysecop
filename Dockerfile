# Dockerfile (multi-stage)

# ==== Stage 1: Base - dependencies and package core ====
FROM python:3.12-slim AS base

WORKDIR /app

# Minimal system packages + tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    ca-certificates \
    pciutils \
    && rm -rf /var/lib/apt/lists/*

# Copy original source code for development/base stage
# Using COPY . . is more reliable for dev environments as it catches
# newly created files/folders automatically.
COPY . .

# Install the package and its dependencies using pip
RUN pip install --no-cache-dir .

# Prepare data folder
RUN mkdir -p /app/data
VOLUME ["/app/data"]

# ==== Stage 2: Production - complete project ====
FROM base AS prod

# Everything is already copied in base for simplicity and consistency
# but we can add production-specific configurations here if needed.

# Expose API and SSH ports
EXPOSE 8000 2222

# Ensure entrypoint is executable
RUN chmod +x /app/docker-entrypoint.sh

# EntryPoint handles runtime configurations (like GPU detection)
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default CMD: Run tests using pytest
CMD ["pytest"]