# 0002: Isaac Sim version and installation method

Date: 2026-09-18

## Decision

Use **Isaac Sim 4.5 via Docker (NVIDIA official container)** for M3, not the latest 5.x/6.0.

## Reasoning

| Version | Min GPU | Min VRAM | Ubuntu 24.04 | Host GPU |
|---|---|---|---|---|
| Isaac Sim 6.0 / 5.1 | RTX 4080 | 16 GB | ✅ | ❌ RTX 2080 Ti = 11 GB |
| Isaac Sim 4.5 | RTX 3070 | 8 GB | ⚠️ (22.04 officially) | ✅ 11 GB > 8 GB |

RTX 2080 Ti has 11 GB VRAM which exceeds the 4.5 minimum (8 GB). Isaac Sim 4.5 does not officially list Ubuntu 24.04, but Docker bypasses the host OS requirement.

Docker is already in the project stack (see reference stack in `CURSOR_PROJECT_GUIDE.md`).

## Method

NVIDIA Isaac Sim 4.5 Docker container via NVIDIA Container Toolkit.

```
docker pull nvcr.io/nvidia/isaac-sim:4.5.0
```

## Constraints

- Simple scenes and sensor setups should fit in 11 GB VRAM.
- Complex multi-camera / high-resolution scenes may hit VRAM limits.
- For the MVP (differential-drive robot + LiDAR + camera), 11 GB is expected to be sufficient.

## Upgrade path

If VRAM proves insufficient, upgrade to RTX 4080/5080 (16+ GB) and move to Isaac Sim 5.x/6.0 at that time.

## References

- https://docs.isaacsim.omniverse.nvidia.com/4.5.0/installation/requirements.html
- https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html
