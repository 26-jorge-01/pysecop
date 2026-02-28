# Dockerfile (multi-stage)

# ==== Etapa base: depende de pyproject.toml, uv.lock ====
FROM python:3.12-slim AS base

WORKDIR /app

# Paquetes de sistema mínimos + herramientas (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    ca-certificates \
    pciutils \
    && rm -rf /var/lib/apt/lists/*

# Copia sólo definiciones de deps para aprovechar caché
COPY pyproject.toml uv.lock* ./
COPY packages/ ./packages/

# Instala uv + deps (incluye streamlit)
RUN pip install --no-cache-dir uv && \
    uv sync

# Uso de venv local para evitar conflictos con el sistema
ENV PATH="/app/.venv/bin:$PATH"

# Prepara carpeta de datos
RUN mkdir -p /app/data
VOLUME ["/app/data"]

# Copiamos el entrypoint que hará la detección de GPU en runtime
# COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
# RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# ==== Etapa prod: código + defaults ====
FROM base AS prod

WORKDIR /app

# Copia todo el código del monorepo
COPY . .

# Expone puertos de Jupyter, API, SSH y Streamlit
EXPOSE 8888 8000 2222 8501 8001

# EntryPoint que autoconfigura GPU si existe
# ENTRYPOINT ["docker-entrypoint.sh"]

# CMD por defecto (notebook). Tu Makefile podrá sobreescribirlo para Streamlit:
CMD ["uv", "run", "jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]