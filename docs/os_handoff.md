# Dual-boot OS handoff

Browser: https://github.com/kim7170719/robot-dev-ai/blob/feature/m2-simple-diff-robot/docs/os_handoff.md

## Current packet (2026-09-17)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Ubuntu branch | `feature/m2-simple-diff-robot` |
| Windows branch | `develop` (PR #4 and #5 merged) |
| G0 / G1 | PASS |
| G2 | odom drive PASS; RViz NOT TESTED |
| Windows todo | pull `develop`; **no ROS** |
| Do not do | Cosmos; Isaac (M3); ROS on Windows |

### Windows

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git status
```

Checklist: https://github.com/kim7170719/robot-dev-ai/blob/feature/m2-simple-diff-robot/docs/windows_next.md

### Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch feature/m2-simple-diff-robot
git pull --ff-only
```

Then `docs/m2_simple_diff_robot.md` (sudo apt + launch).
