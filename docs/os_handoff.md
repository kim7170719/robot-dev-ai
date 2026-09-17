# Dual-boot OS handoff

Ubuntu and Windows do not share a Cursor chat. Reboot is normal. **GitHub is the handoff.**

After every reboot, open this file in the browser first:

https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-ros-baseline/docs/os_handoff.md

Until the M1 PR merges, **do not** trust the `develop` copy of this file.

## Current packet (2026-09-17)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Safe to reboot? | Yes after this packet is pushed |
| Ubuntu branch | `feature/m1-ros-baseline` |
| Windows branch | `develop` until M1 PR merges |
| G0 | PASS — `g0-environment-baseline` |
| G1 | PASS — `ros2 launch m1_baseline m1_graph.launch.py` + CLI service/action |
| Next OS | Either; Windows has a read-only Git round. Ubuntu can keep M1 extras. |
| Windows todo | `docs/windows_next.md` — fetch `develop` + tags; **no ROS** |
| Do not do | ROS / Isaac / Cosmos on Windows; Cosmos on Ubuntu; develop on `main` |

### After reboot → Windows

Follow https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-ros-baseline/docs/windows_next.md

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git fetch --tags
git status
```

### After reboot → Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch feature/m1-ros-baseline
git pull --ff-only
git status
```

G1 commands: `docs/m1_g1.md`.

## Every reboot

Leave: status → commit → push → `scripts/before_reboot.*` → reboot.  
Arrive: browser packet → fetch/switch/pull → clean status before edits.
