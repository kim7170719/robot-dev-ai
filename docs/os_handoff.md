# Dual-boot OS handoff

After reboot open:

https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-pipeline/docs/os_handoff.md

If that 404s, use develop:

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/os_handoff.md

## Current packet (2026-09-17)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Ubuntu branch | `feature/m1-pipeline` |
| Windows branch | `develop` (G1 merged via PR #4) |
| G0 / G1 | PASS |
| Next | Windows pull `develop`; Ubuntu pipeline PR; no M2/Cosmos |
| Windows todo | `docs/windows_next.md` — **no ROS install** |

### Windows

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git fetch --tags
git status
```

Browser: https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-pipeline/docs/windows_next.md

### Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch feature/m1-pipeline
git pull --ff-only
git status
```
