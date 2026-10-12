# Dual-boot OS handoff

After every reboot, open this file in the browser first:

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/os_handoff.md

## Current packet (2026-10-12)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Ubuntu branch | `feature/m15-hardware-integration` |
| Last pushed series | M14 closure: rigged interactive local GLB landing model; M15 hardware-integration preflight documentation |
| Windows branch | `feature/m15-hardware-integration` after fetching this branch |
| G0–G12, G14 | ALL PASS |
| Tags | `g0-environment-baseline`, `m2-g2-simple-diff-robot`, `m3-g3-isaac-sim` |
| Next milestone | M15 Jetson + real-robot bring-up (preflight active; G15 not passed); Cosmos O1 remains deferred |
| Windows todo | Fetch `feature/m15-hardware-integration`; use Windows only for Git, Cursor, and docs |
| Do not do | ROS on Windows; Isaac Sim on Windows; Cosmos |

G12 and G14 completed: the frozen virtual MVP and its typed five-view GUI passed. M14's landing page now uses the locally stored, user-supplied rigged GLB model with local Three.js interaction and bundled animation clips; it is presentation art, not a simulator viewport or a physical controller. The five-stage top navigation, bilingual/plain-language operator copy, and typed API safety boundary remain intact. Dashboard Sensor Workbench offers fixed read-only Isaac and RealSense D455 sources; `bash scripts/start_d455_camera.sh` provides the verified low-latency 640×480 / 30 FPS D455 colour stream. RGBD remains opt-in via `ROBOT_DEV_AI_D455_RGBD=1`; the observed USB 2.1 link requires direct USB 3.x before sustained RGBD workloads. M15 now starts with the documented Jetson Orin Nano + differential-drive + D455 hardware preflight. Do not claim real-robot success or enable motors until the physical LiDAR, encoders, independent emergency stop, power path, controller interface, and staged evidence in `docs/m15_hardware_integration.md` are complete. M13 Cosmos remains Optional Extension O1 and must not be installed on this RTX 2080 Ti (Turing, 11 GB). See `docs/roadmap_v0.3.md`, `docs/m14_gui_architecture.md`, `docs/m14_demo.md`, `docs/m15_hardware_integration.md`, and `docs/m13_cosmos.md`.

### After reboot → Windows

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch feature/m15-hardware-integration
git pull --ff-only
git status
git log -5 --oneline
```

Confirm M12/G12 files plus M14 documents: `agent/mvp_pipeline/`, `agent/auto_debug/repairer.py`, `docs/roadmap_v0.3.md`, and `docs/m14_gui_architecture.md`. Do not pull Cosmos models on Windows.

### After reboot → Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch feature/m15-hardware-integration
git pull --ff-only
git fetch --tags
git status
```

Read `docs/AI_HANDOFF.md`, `docs/roadmap_v0.3.md`, and `docs/m14_gui_architecture.md`. Do not attempt Cosmos execution until using supported hardware.

## Every reboot

Leave: `git status` → commit/push → `scripts/before_reboot.sh` → reboot.  
Arrive: browser URL above → fetch/switch/pull → clean status before edits.

Clones: Ubuntu `~/dev/robot-dev-ai`, Windows `C:\dev\robot-dev-ai`.
