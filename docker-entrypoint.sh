#!/usr/bin/env bash
set -e

echo "[INFO] Iniciando contenedor…"

GPU_MARKER="/app/.gpu-setup-done"

# Si hay soporte NVIDIA dentro del contenedor (host + --gpus all)
if command -v nvidia-smi >/dev/null 2>&1; then
    echo "[INFO] GPU NVIDIA detectada dentro del contenedor (nvidia-smi disponible)."

    if [ ! -f "$GPU_MARKER" ]; then
        echo "[INFO] Primera vez con GPU: instalando CUDA toolkit y stack ML con soporte GPU…"

        # Instalamos CUDA toolkit básico desde repos del sistema (no drivers del host).
        # OJO: esto es pesado; se hace una sola vez por imagen.
        apt-get update && \
        apt-get install -y --no-install-recommends \
            nvidia-cuda-toolkit && \
        rm -rf /var/lib/apt/lists/*

        # En este punto PATH ya apunta al venv (.venv/bin)
        # Instalamos librerías ML con soporte GPU cuando sea posible.
        # Ajusta según tu stack real.
        pip install --no-cache-dir \
            torch \
            torchvision \
            torchaudio

        # Si quieres, puedes añadir aquí tensorflow-gpu u otros, pero
        # cuidado con versiones / compatibilidad.

        touch "$GPU_MARKER"
        echo "[INFO] Configuración GPU completada."
    else
        echo "[INFO] Configuración GPU ya realizada previamente. No se reinstala nada."
    fi
else
    echo "[INFO] No se detectó GPU (nvidia-smi no disponible). Ejecutando en modo CPU."
fi

echo "[INFO] Lanzando comando: $*"
exec "$@"
