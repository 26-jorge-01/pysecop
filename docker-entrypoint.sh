#!/usr/bin/env bash
set -e

# Support for multi-environment GPU detection
# Ensure this script has POSIX line endings (LF) for Linux compatibility

echo "[INFO] Initializing container..."

GPU_MARKER="/app/.gpu-setup-done"

# Check for NVIDIA support within the container (host + --gpus all)
if command -v nvidia-smi >/dev/null 2>&1; then
    echo "[INFO] NVIDIA GPU detected inside container (nvidia-smi available)."

    if [ ! -f "$GPU_MARKER" ]; then
        echo "[INFO] First time GPU setup: installing CUDA toolkit and GPU-enabled ML stack..."

        # Install minimal CUDA toolkit (requires root/sudo within container)
        apt-get update && \
        apt-get install -y --no-install-recommends \
            nvidia-cuda-toolkit && \
            rm -rf /var/lib/apt/lists/*

        # Use 'pip' for standard GPU dependency installs
        echo "[INFO] Installing PyTorch with GPU support via pip..."
        pip install --no-cache-dir \
            torch \
            torchvision \
            torchaudio

        touch "$GPU_MARKER"
        echo "[INFO] GPU configuration completed."
    else
        echo "[INFO] GPU already configured. Skipping re-installation."
    fi
else
    echo "[INFO] No GPU detected (nvidia-smi not found). Running in CPU mode."
fi

echo "[INFO] Launching command: $*"
# Use 'exec' to ensure signals (SIGTERM, etc.) are handled by the process
exec "$@"
