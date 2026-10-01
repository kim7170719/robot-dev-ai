# Dual-boot OS handoff

After every reboot, open this file in the browser first:

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/os_handoff.md

## Current packet (2026-10-01)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Ubuntu branch | `develop` (create `feature/m5-*` before M5 edits) |
| Windows branch | `develop` |
| G0 / G1 / G2 / G3 / G4 | ALL PASS |
| Tags | `g0-environment-baseline`, `m2-g2-simple-diff-robot`, `m3-g3-isaac-sim` |
| Next milestone | M5 Isaac ROS (Ubuntu only) |
| Windows todo | Fetch the G4 checkpoint; do not install ROS, Isaac, Nav2, or Isaac ROS |
| Do not do | ROS on Windows; Isaac Sim on Windows; Cosmos |

G4 completed: Nav2 + SLAM Toolbox navigation in Isaac Sim, including obstacle avoidance, with a synthetic 2D `/scan`. See `docs/m4_nav2.md` and `experiments/raw/M4-G4.md`.

### After reboot → Windows

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch feature/m4-nav2
git pull --ff-only
git fetch --tags
git status
git log -5 --oneline
git tag -l "g*" "m*"
```

Confirm G4 files: `docs/m4_nav2.md`, `experiments/raw/M4-G4.md`, and `ros_ws/src/simple_diff_nav/`.
Read: https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/windows_next.md

### After reboot → Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git fetch --tags
git status
```

Then create a `feature/m5-*` branch before beginning M5.

## Every reboot

Leave: `git status` → commit/push → `scripts/before_reboot.sh` → reboot.  
Arrive: browser URL above → fetch/switch/pull → clean status before edits.

Clones: Ubuntu `~/dev/robot-dev-ai`, Windows `C:\dev\robot-dev-ai`.
