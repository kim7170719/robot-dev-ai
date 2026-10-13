# Dual-boot OS handoff

After every reboot, open this file in the browser first:

https://github.com/kim7170719/robot-dev-ai/blob/refactor/composable-architecture-v0.4/docs/os_handoff.md

## Historical packet (2026-10-12, superseded)

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

v0.6 scalable evidence foundation now also keeps unreviewed community reports
outside accepted evidence and exposes a deterministic evidence snapshot through
the API/GUI. Full suite after this work: **94 tests passed**. The v0.6 numeric
research gate remains pending real audit-backed discovery/sandbox records; do
not claim E2/E4/E5 evidence.

Transaction persistence/preflight is complete: callers can configure an
`OnboardingTransactionStore` JSONL path to recover a preview after restart;
the GUI shows a read-only sandbox runner status. Docker/bubblewrap are never
started by that check. Full suite: **102 tests passed**. Actual isolated source
acquisition/execution remains deliberately unimplemented.

The first real bubblewrap self-test is **BLOCKED** here: the fixed no-network,
read-only root, tmpfs-only test failed at loopback setup with `RTM_NEWADDR:
Operation not permitted`. No source was acquired or executed. Treat a detected
binary as `available`, never `ready`; use a namespace-capable host or a
separately reviewed Docker runner before source acquisition.

Docker fallback is now **PASS** with the already-local
`nvidia/cuda:12.6.2-base-ubuntu24.04` image: the fixed test uses `--pull never`,
no network, read-only root, noexec tmpfs, dropped capabilities, non-root user,
and PID/memory/CPU limits. Set `ROBOT_DEV_AI_SANDBOX_RUNNER=docker` and
`ROBOT_DEV_AI_SANDBOX_IMAGE=nvidia/cuda:12.6.2-base-ubuntu24.04` only to expose
this verified self-test. It still does not permit source acquisition. Full
suite: **108 tests passed**.

Local source bundle gate is now PASS: sandbox input must be a user-supplied,
regular non-symlink `.tar.gz`/`.tgz`/`.zip` below a caller-configured root with
an allowlisted SHA-256 matching the operator-supplied expected hash. Verification
only reads and hashes the archive then appends audit evidence—no mount, unpack,
build, clone, download, or execution. Full suite: **112 tests passed**.

Fixed Docker dependency scan is now PASS for verified `.tar.gz`/`.tgz`: it
read-only mounts exactly one archive and runs only `tar -tzf`, reporting entry
count/top-level names. Internal roadmap archive self-test listed one entry;
nothing was extracted or executed. Full suite: **113 tests passed**. ZIP scan
and all build/installation steps remain intentionally absent.

Archive scan now identifies candidate manifest/license paths from entry names
only (`package.xml`, `package.json`, `pyproject.toml`, `requirements.txt`,
`LICENSE*`, `COPYING*`, `NOTICE*`). It never opens/parses/extracts the files;
do not treat candidates as validated dependencies or license claims. Full suite:
**114 tests passed**.

Bounded ROS manifest metadata extraction is now PASS: only after the passed
authorization/hash/scan gates, Docker selects the first listed `package.xml`
from the verified archive, applies the existing no-network/no-pull/read-only
profile, and streams at most 128 KiB into an XML parser. The API returns only
the package name and declared dependency IDs, appends
`manifest-metadata-extracted` audit evidence, and never writes, installs,
builds, or executes candidate source. A live Docker check of the existing
`simple_diff_robot/package.xml` returned its name plus nine declared
dependencies and its source-declared version. XML DTD/entity declarations are rejected before parsing. Full
suite: **120 tests passed**.

Append-only audit recovery is now PASS: a caller-configured audit JSONL store
reloads its typed records on API restart. A recovered transaction therefore
retains its recorded human sandbox authorization, but recovery itself neither
starts a runner nor authorizes source acquisition, installation, build, or
execution. Full suite: **121 tests passed**.

Onboarding gates are now artifact-bound: verification, dependency scan, and
ROS manifest audit records retain the archive SHA-256, and each later endpoint
requires the exact same hash. A different allowlisted archive cannot reuse a
previous artifact's transaction evidence. The full local API flow passed on a
temporary `simple_diff_robot/package.xml` archive. Full suite: **122 tests
passed**.

G12.6 Evidence Explorer now includes a read-only coverage matrix, separate
same-context conflict viewer, and Reference Robot list through
`GET /api/v1/evidence/overview`. The default Reference A remains explicitly
`planned`; it is not real-hardware evidence and does not close the numerical
G12.6 population gate.

Verified source archives can now expose bounded license metadata: the first
scan-listed `LICENSE*`/`COPYING*`/`NOTICE*` is read up to 32 KiB inside the
same isolated Docker profile. Only a literal SPDX header is reported; this is
not a legal license decision. Local Apache license evidence correctly returned
no SPDX declaration. Full suite: **125 tests passed**.

The future E2 build environment is now defined (not provisioned) by
`docker/Dockerfile.sandbox-ros-jazzy-build`; see `docs/sandbox_build_image.md`.
Building it remains an explicit operator action because it may pull the ROS
base image. Application code does not build or pull it.

New onboarding audit records form a SHA-256 hash chain. Reload rejects a
tampered hashed record; preexisting unhashed JSONL remains legacy-readable but
is not hash-verified evidence.

The next v0.5 onboarding preview is also complete: it creates a deterministic
audit transaction and sandbox-step plan with `execution_authorized=false`.
Registry GUI can preview it, never run it. Next is persistent audit storage and
the separately authorized sandbox executor. Full suite at this checkpoint:
**97 tests passed**.

Onboarding audit/runner contract is now in place: a preview is recorded, and
only its in-process transaction ID plus explicit confirmation produces an
append-only `sandbox-runner-authorized` audit record. It is still host-zero-
execution; a true isolated runner and restart-persistent transaction store are
the next scope. Full suite: **99 tests passed**.

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

## Current packet (2026-10-13)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Ubuntu / Windows branch | `refactor/composable-architecture-v0.4` |
| Latest checkpoint | Run `git log -1 --oneline origin/refactor/composable-architecture-v0.4` after fetch; do not rely on a hard-coded SHA in this handoff |
| Gates | G12, G12.5, G12.6 foundation, and G14 pass; evidence remains virtual-only unless explicitly stated |
| v0.5 state | Trusted-source metadata, registry GUI, audit persistence/hash chain, verified local bundle gates, bounded metadata scan, and fixed sandbox build endpoint are implemented |
| v0.6 state | Evidence schema/query/snapshot/review queue and M14B coverage/conflict/reference views are implemented |
| Current E2 state | No `ROBOT_DEV_AI_SANDBOX_BUILD_IMAGE` is configured or present; no approved source archive has run an isolated build; no E2 record exists |
| M15 / Cosmos | M15 waits for physical hardware; Cosmos O1 remains deferred on this RTX 2080 Ti |
| Windows scope | Git, Cursor, and docs only; never install ROS, Isaac Sim, Nav2, or Cosmos |

The next valid v0.5 action needs an operator-reviewed local Jazzy build image
and a separately reviewed, allowlisted source archive. The fixed endpoint
`POST /api/v1/registry/onboarding/{id}/bundle/build` already enforces human
authorization, one exact archive hash, passed scan/ROS-manifest/license gates,
and a no-network/non-root/read-only Docker boundary. Do not claim E2 merely
because the endpoint or Dockerfile exists.

The remaining G12.6 population gate needs authoritative observations: ten
E0/E1 source records, three real isolated-build E2 observations, human-reviewed
community reports for E5, and M15 hardware for E4. Do not fabricate records or
reinterpret E3 simulation results as hardware validation.

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
