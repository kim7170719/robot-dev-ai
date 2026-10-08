# Dual-boot OS handoff

After every reboot, open this file in the browser first:

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/os_handoff.md

## Current packet (2026-10-08)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Ubuntu branch | `feature/gui-mvp` |
| Last pushed series | M14 GSAP choreography and hard-surface humanoid redesign; inspect `git log -3 --oneline` after pull |
| Windows branch | `feature/gui-mvp` after fetching this branch |
| G0–G12, G14 | ALL PASS |
| Tags | `g0-environment-baseline`, `m2-g2-simple-diff-robot`, `m3-g3-isaac-sim` |
| Next milestone | M15 Jetson + real-robot bring-up; Cosmos O1 remains deferred |
| Windows todo | Fetch `feature/gui-mvp`; use Windows only for Git, Cursor, and docs |
| Do not do | ROS on Windows; Isaac Sim on Windows; Cosmos |

G12 and G14 completed: the frozen virtual MVP and its typed five-view GUI passed. M14 was subsequently redesigned as a precision product surface; its implemented rules are in `PRODUCT.md` and `DESIGN.md`. Root URL `/` now opens one original local WebGL humanoid built from native Three.js geometry, with rounded white shell panels, graphite recesses, external shoulder yokes, and segmented nested limbs that avoid arm-to-torso intersections through its ready, scan, wave, acknowledgement, mobility, and stance sequence. A local GSAP 3.12.5 timeline provides a single short entry sequence and is disabled for reduced motion; robot motion also pauses outside landing and in hidden tabs. It never cycles images or loads an external robot model, and is presentation art rather than a simulator viewport. Three.js and GSAP notices are in `docs/THIRD_PARTY_NOTICES.md`. Overview uses the matching deep-ink control surface, while the other task views remain readable and light. The workspace uses a five-stage top navigation instead of a left rail, with a Chinese/English switch and plain-language operator copy for the primary flow. It remains presentation-only: API/ROS safety boundaries did not change. Dashboard Sensor Workbench offers fixed read-only sources: Isaac `/camera/image_raw` and RealSense D455 `/webcam/color/image_raw`; D455 device nodes are visible but the Jazzy driver still awaits privileged installation. It is not a viewport or a controller. M4 runtime was recovered on Ubuntu: run only one Nav2 launch after SLAM map/TF is ready; the fixed `(1.0, 0.0)` virtual navigation goal now returns `SUCCEEDED`. M13 Cosmos is Optional Extension O1 and must not be installed on this RTX 2080 Ti (Turing, 11 GB). See `docs/roadmap_v0.3.md`, `docs/m14_gui_architecture.md`, `docs/m14_demo.md`, and `docs/m13_cosmos.md`.

### After reboot → Windows

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch feature/gui-mvp
git pull --ff-only
git status
git log -5 --oneline
```

Confirm M12/G12 files plus M14 documents: `agent/mvp_pipeline/`, `agent/auto_debug/repairer.py`, `docs/roadmap_v0.3.md`, and `docs/m14_gui_architecture.md`. Do not pull Cosmos models on Windows.

### After reboot → Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch feature/gui-mvp
git pull --ff-only
git fetch --tags
git status
```

Read `docs/AI_HANDOFF.md`, `docs/roadmap_v0.3.md`, and `docs/m14_gui_architecture.md`. Do not attempt Cosmos execution until using supported hardware.

## Every reboot

Leave: `git status` → commit/push → `scripts/before_reboot.sh` → reboot.  
Arrive: browser URL above → fetch/switch/pull → clean status before edits.

Clones: Ubuntu `~/dev/robot-dev-ai`, Windows `C:\dev\robot-dev-ai`.
