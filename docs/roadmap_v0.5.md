# Roadmap v0.5 — Registry Management GUI and Trusted Source

**Status:** active foundation (2026-10-12)

**Source:** user-supplied *ROBOT DEV AI Roadmap v0.5 — Composable Architecture
Registry GUI + Trusted Source Onboarding*.

## Boundary

This roadmap builds on the frozen G12.5 v0.4 core and the implemented v0.6
evidence primitives. It does not reinterpret virtual evidence as real-hardware
support. The Registry Management interface is distinct from project Usage Mode:
it shows provenance, license, lifecycle, and source-policy outcomes; it does
not run shell commands, install packages, clone repositories, or operate ROS
hardware from the browser.

## First active slice

1. Versioned source, license, compatibility-claim, component-lifecycle, and
   provenance records.
2. A pure Trusted Source policy: BLOCKED sources stay blocked; every other
   candidate remains metadata-only or sandbox-only until a later human-approved
   acquisition path exists.
3. Read-only management endpoints and a Registry view for inspecting and
   filtering the stored catalog, then reviewing a source's next permitted step.

The initial catalog contains only historical virtual-MVP facts. `tested` means
the listed component has the stored virtual evidence boundary; it is not a
claim of real-world VERIFIED support.

## Deferred v0.5 stages

- Discovery jobs and external metadata retrieval.
- Audit-log-backed CRUD, user identity, reviewable diffs, and persistence.
- Sandbox clone/download, dependency scan, build/test, ROS validation, and
  promotion/deprecation mutations.
- Official ROS package onboarding and Vendor SDK/protocol adapter skeletons.
- Promotion to `verified`, which must require environment, version, hardware,
  evidence, and human approval.

## Safety invariants

- No result from discovery may trigger `curl | sudo`, package installation, or
  arbitrary execution.
- GUI clients use typed Core API endpoints only; source review is an inspection
  result, never an acquisition command.
- Any future mutating stage must preserve actor, time, provenance, reviewed
  diff, confirmation, and evidence, then pass the existing mutation-safety
  gate.

## Next implementation order

The audit-ready preview transaction is now implemented: it produces a stable
identifier, requested-by value, review result, lifecycle diff, and ordered
sandbox plan, while explicitly returning `execution_authorized=false`. The
GUI can preview that plan for a registered component. Explicit confirmation is
append-only audited and only authorizes handoff to a future sandbox runner; it
does not execute code on the host.

The caller-configured transaction and audit JSONL stores now both recover typed
records after an API restart. The remaining boundary is a deliberately limited
sandbox executor: no source acquisition, installation, build, test, or registry
promotion is authorized by persistence or recovery alone.

Transaction persistence and runner preflight are now implemented. A
caller-configured JSONL transaction store restores preview IDs after an API
restart. The GUI exposes a runner status from a read-only preflight: no profile
is `not-configured`; an unavailable configured binary is `blocked`; an
explicit bubblewrap or Docker profile with required isolation settings is only
`available` until the isolated self-test passes. Preflight never starts Docker
or bubblewrap.

Docker is now the validated fallback on this host. It requires an explicit
`ROBOT_DEV_AI_SANDBOX_IMAGE` that is already local and runs the fixed self-test
with `--pull never`, `--network none`, `--read-only`, a noexec tmpfs, dropped
capabilities, no-new-privileges, non-root UID, and PID/memory/CPU limits. The
local `nvidia/cuda:12.6.2-base-ubuntu24.04` self-test passed on 2026-10-13. It
does not establish permission to acquire external source code.

The local source bundle gate is now the prerequisite for future acquisition:
only a regular non-symlink `.tar.gz`, `.tgz`, or `.zip` below a caller-
configured root, within the size limit, whose streamed SHA-256 matches both
the operator-provided expected hash and the server allowlist can be marked
verified. Bundle preview requires the prior sandbox authorization and writes an
audit event, but does not mount, unpack, build, or execute the bundle.

The first fixed dependency scan is now implemented for verified `.tar.gz` and
`.tgz` inputs. Docker bind-mounts exactly one archive as `/bundle/source`
read-only and runs only `tar -tzf`; it returns entry count and top-level names,
without extraction or shell input. The full authorization/hash gate remains
required. A local internal archive scan passed on 2026-10-13 under the existing
no-network/no-pull Docker profile.

Dependency scan results now classify candidate metadata from archive entry
names only: `package.xml`, `package.json`, `pyproject.toml`, and
`requirements.txt` are dependency-manifest candidates; `LICENSE*`, `COPYING*`,
and `NOTICE*` are license candidates. The container still runs only `tar -tzf`:
candidate files are not opened, extracted, parsed, or executed.

For a verified ROS archive, the next bounded step is available at
`POST /api/v1/registry/onboarding/{id}/bundle/ros-manifest`. It requires the
previous passed dependency scan, selects the first scan-listed `package.xml`,
and uses the same no-network/no-pull/read-only Docker profile. A fixed command
streams no more than 128 KiB to an XML parser and returns only the ROS package
name, declared version, plus declared dependency identifiers. It does not write the manifest to
the host, resolve dependency versions, validate licenses, install, build, or
execute the candidate source.

Every artifact stage is bound to the same verified SHA-256 in append-only audit
evidence. A dependency scan or ROS manifest request for a different—even also
allowlisted—archive is rejected until that exact archive has passed its own
preceding gate.

The same bounded path also exposes `bundle/license-metadata`: it selects only
the first scan-listed `LICENSE*`, `COPYING*`, or `NOTICE*`, streams at most
32 KiB in the isolated container, and records an explicitly declared
`SPDX-License-Identifier` when one is present. Its output is source-provided
metadata only, not a license interpretation or authorization to redistribute,
install, build, or execute code.

`GET /api/v1/registry/sandbox/build-readiness` now makes the E2 prerequisite
explicit: only a caller-selected `ROBOT_DEV_AI_SANDBOX_BUILD_IMAGE` already
present in the local Docker image store is `available`. The check never pulls
an image or starts a container; without a ROS Jazzy build image, E2 remains
unproven.

The reproducible image definition is `docker/Dockerfile.sandbox-ros-jazzy-build`.
`docs/sandbox_build_image.md` makes provisioning an explicit operator step;
application code never builds or pulls it.
