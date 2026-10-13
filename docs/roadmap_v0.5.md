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

Next, add a persistent audit store and sandbox executor behind the trusted-
source and mutation-safety policies. Only then should the Registry GUI expose
a human-confirmed candidate onboarding action that can acquire code.

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
