# Dual-boot OS handoff

After every reboot, open this file in the browser first:

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/os_handoff.md

## Current packet (2026-10-06)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Ubuntu branch | `feature/m12-full-mvp` |
| Last pushed commit | `bc8929c` — M12 freeze + M14 API start |
| Windows branch | `feature/m12-full-mvp` |
| G0–G12 | ALL PASS |
| Tags | `g0-environment-baseline`, `m2-g2-simple-diff-robot`, `m3-g3-isaac-sim` |
| Next milestone | M14 GUI MVP — typed API first; Cosmos O1 deferred |
| Windows todo | Fetch `feature/m12-full-mvp`; use Windows only for Git, Cursor, and docs |
| Do not do | ROS on Windows; Isaac Sim on Windows; Cosmos |

G12 completed: the frozen virtual MVP passed. v0.3 makes M14 GUI MVP the main path. M13 Cosmos is Optional Extension O1 and must not be installed on this RTX 2080 Ti (Turing, 11 GB). See `docs/roadmap_v0.3.md`, `docs/m14_gui_architecture.md`, and `docs/m13_cosmos.md`.

### After reboot → Windows

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch feature/m12-full-mvp
git pull --ff-only
git status
git log -5 --oneline
```

Confirm M12/G12 files plus M14 documents: `agent/mvp_pipeline/`, `agent/auto_debug/repairer.py`, `docs/roadmap_v0.3.md`, and `docs/m14_gui_architecture.md`. Do not pull Cosmos models on Windows.

### After reboot → Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch feature/m12-full-mvp
git pull --ff-only
git fetch --tags
git status
```

Read `docs/AI_HANDOFF.md`, `docs/roadmap_v0.3.md`, and `docs/m14_gui_architecture.md`. Do not attempt Cosmos execution until using supported hardware.

## Every reboot

Leave: `git status` → commit/push → `scripts/before_reboot.sh` → reboot.  
Arrive: browser URL above → fetch/switch/pull → clean status before edits.

Clones: Ubuntu `~/dev/robot-dev-ai`, Windows `C:\dev\robot-dev-ai`.
