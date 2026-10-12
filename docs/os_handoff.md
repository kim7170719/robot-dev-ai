# Dual-boot OS handoff

After every reboot, open this file in the browser first:

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/os_handoff.md

## Current packet (2026-10-12)

v0.5 Trusted Source / Registry Management first slice is ready on
`refactor/composable-architecture-v0.4`: `registry/v05.py` keeps source,
license, compatibility claim, lifecycle, and provenance metadata, while
`agent/trusted_source/` only classifies policy and never fetches or executes
artifacts. The GUI Registry view is read-only (`/api/v1/registry/management`
and source review); it cannot discover, install, build, validate, promote, or
edit external sources. Before this handoff: **94 tests passed**, `node --check
gui/app.js`, TestClient GUI/catalog/review smoke, and `git diff --check` all
passed. Next, implement an audit-backed onboarding transaction and sandbox
executor before enabling source discovery or Registry CRUD.

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Ubuntu branch | `refactor/composable-architecture-v0.4` |
| Last pushed series | v0.5 read-only trusted-source/Registry foundation; M15 preflight remains paused |
| Windows branch | `refactor/composable-architecture-v0.4` after fetching this branch |
| G0–G12, G14 | ALL PASS |
| Tags | `g0-environment-baseline`, `m2-g2-simple-diff-robot`, `m3-g3-isaac-sim` |
| Next milestone | Audit-backed onboarding transaction + sandbox executor; M15 remains paused; Cosmos O1 remains deferred |
| Windows todo | Fetch `refactor/composable-architecture-v0.4`; use Windows only for Git, Cursor, and docs |
| Do not do | ROS on Windows; Isaac Sim on Windows; Cosmos |

G12 and G14 completed: the frozen virtual MVP and its typed five-view GUI passed. M14's landing page uses the locally stored, user-supplied rigged GLB model with local Three.js interaction and bundled animation clips; it is presentation art, not a simulator viewport or a physical controller. v0.4 now inserts G12.5 before M15: the core must gain versioned architecture/capability/composition/adapter/readiness/safety/evidence models before heterogeneous real-hardware execution resumes. M15's Jetson Orin Nano + differential-drive + D455 preflight is retained but paused; do not claim real-robot success or enable motors. M13 Cosmos remains Optional Extension O1 and must not be installed on this RTX 2080 Ti (Turing, 11 GB). See `docs/roadmap_v0.4.md`, `docs/architecture_v0.4.md`, `docs/decisions/0008-composable-architecture-before-real-hardware.md`, and `docs/m15_hardware_integration.md`.

### After reboot → Windows

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch refactor/composable-architecture-v0.4
git pull --ff-only
git status
git log -5 --oneline
```

Confirm the v0.4 baseline: `docs/roadmap_v0.4.md`, `docs/architecture_v0.4.md`, and `docs/decisions/0008-composable-architecture-before-real-hardware.md`. Do not pull Cosmos models on Windows.

### After reboot → Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch refactor/composable-architecture-v0.4
git pull --ff-only
git fetch --tags
git status
```

Read `docs/AI_HANDOFF.md`, `docs/roadmap_v0.4.md`, and `docs/architecture_v0.4.md`. Do not attempt Cosmos execution until using supported hardware.

## Every reboot

Leave: `git status` → commit/push → `scripts/before_reboot.sh` → reboot.  
Arrive: browser URL above → fetch/switch/pull → clean status before edits.

Clones: Ubuntu `~/dev/robot-dev-ai`, Windows `C:\dev\robot-dev-ai`.
