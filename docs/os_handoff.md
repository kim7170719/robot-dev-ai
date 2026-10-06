# Dual-boot OS handoff

After every reboot, open this file in the browser first:

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/os_handoff.md

## Current packet (2026-10-06)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Ubuntu branch | `feature/m12-full-mvp` |
| Windows branch | `feature/m12-full-mvp` |
| G0–G11 | ALL PASS |
| Tags | `g0-environment-baseline`, `m2-g2-simple-diff-robot`, `m3-g3-isaac-sim` |
| Next milestone | M12 MVP Freeze |
| Windows todo | Fetch `feature/m12-full-mvp`; use Windows only for Git, Cursor, and docs |
| Do not do | ROS on Windows; Isaac Sim on Windows; Cosmos |

G11 completed: M11 provides constrained build collection, read-only ROS node/topic/controller/TF snapshots, evidence-backed diagnosis, bounded repair recommendations, reviewable dependency diffs, and failure reports. See `docs/progress.md` and `docs/AI_HANDOFF.md`.

### After reboot → Windows

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch feature/m12-full-mvp
git pull --ff-only
git status
git log -5 --oneline
```

Confirm M11 files: `agent/auto_debug/`, `tests/test_auto_debug_agent.py`, `tests/test_build_command_collector.py`, and `docs/progress.md`.

### After reboot → Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch feature/m12-full-mvp
git pull --ff-only
git fetch --tags
git status
```

Continue M12 only after reading `docs/AI_HANDOFF.md`.

## Every reboot

Leave: `git status` → commit/push → `scripts/before_reboot.sh` → reboot.  
Arrive: browser URL above → fetch/switch/pull → clean status before edits.

Clones: Ubuntu `~/dev/robot-dev-ai`, Windows `C:\dev\robot-dev-ai`.
