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

Add a persistent audit-backed onboarding transaction before enabling source
discovery or CRUD. Then add a sandbox executor behind the trusted-source and
mutation-safety policies. Only after that should the Registry GUI expose an
explicit human-confirmed candidate onboarding action.
