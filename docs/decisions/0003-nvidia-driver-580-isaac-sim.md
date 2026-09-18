# 0003: NVIDIA driver 580 for Isaac Sim 4.5

Date: 2026-09-18

## Decision

Downgrade from **nvidia-driver-595** to **nvidia-driver-580** for Isaac Sim 4.5 compatibility.

## Reason

- `nvidia-driver-595`: `librtx.scenedb.plugin.so` segfaults at startup in Isaac Sim 4.5
- `nvidia-driver-580`: Isaac Sim 4.5 headless starts successfully (1781 MiB VRAM, extensions loaded)
- Isaac Sim 4.5 recommended driver is 535.129.03 but 580 also works
- Driver 580 is still compatible with RViz2 (GLX context works)

## Impact

- `__GL_THREADED_OPTIMIZATIONS=0` may no longer be needed for RViz2 (to be re-tested)
- CUDA version: 580 → CUDA 13.0 (was 13.2 with 595)
- Docker GPU pass-through (`--gpus all`) still works

## Packages

- `nvidia-driver-580 580.178.04-0ubuntu0.24.04.1`
- `linux-modules-nvidia-580-generic-7.0` for kernel 7.0.0-31-generic
