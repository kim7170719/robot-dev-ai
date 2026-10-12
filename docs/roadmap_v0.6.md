# Roadmap v0.6 — Scalable Evidence Registry

**Status:** accepted future sequencing (2026-10-12)

**Source:** user-supplied *ROBOT DEV AI Roadmap v0.6 — Composable Architecture
and Scalable Evidence Registry*.

**Supersedes:** future sequencing in `docs/roadmap_v0.4.md`. It preserves
historical G0–G12/G14 evidence and the active G12.5 implementation work.

## Decision and boundary

G12.5 remains the immediate prerequisite. Its completed Tasks 1–6 are retained;
Task 7 is Hardware Readiness, Task 8 is Safety/Transaction, Task 9 is
regression/acceptance, and Task 10 freezes the core schema. M14 remains a
completed v0.3 presentation surface until that freeze.

After G12.5, introduce **G12.6 Scalable Evidence Registry** before new registry
management GUI work or real-robot claims. G12.6 makes limited-hardware research
honest and reusable: broad component knowledge can be documented and tested in
software/simulation without being represented as physically verified.

```text
G0–G12 virtual MVP (PASS) → G12.5 composable core (active)
→ G12.6 scalable evidence registry → M14B registry-aware GUI
→ M15 reference real robot → M16 sim-to-real / benchmark
→ M17 thesis → M18 release
```

Cosmos remains optional and never validates physics, ROS, or real hardware.

## Evidence model

| Level | Meaning | Does not claim |
|---|---|---|
| E0 DISCOVERED | Traceable source was found | Compatibility or build success |
| E1 DOCUMENTED | Interface, version, dependency, license, and capability facts are captured | Executable software |
| E2 BUILD_VERIFIED | Build/dependency validation passed in a recorded environment | Simulation or real-hardware operation |
| E3 SIM_VERIFIED | A recorded simulator/runtime scenario passed | Real-hardware support |
| E4 REAL_VERIFIED | A named hardware/environment produced reproducible real evidence | General support for all environments |
| E5 COMMUNITY_VERIFIED | Multiple independent, reviewable reports agree | Unconditional compatibility |

Evidence level is independent of source trust. Registry records must preserve
environment-specific PASS and FAIL evidence rather than collapsing them into a
global boolean. New community evidence is pending review and cannot overwrite
historical records or promote an entry by itself.

## G12.6 deliverables

1. Evidence level, source trust, coverage, conflict, community-submission, and
   immutable snapshot schemas.
2. Migration of existing registry facts without inventing evidence levels.
3. E1/E2 metadata and sandbox build pipeline; E3 contract for the existing
   differential-drive Isaac stack.
4. Context-aware evidence queries and immutable snapshots for M16 benchmark
   isolation.
5. Later, registry-aware Evidence Explorer, Coverage Matrix, Conflict Viewer,
   Reference Robots, and snapshot views in M14B.

## G12.6 gate intent

- At least ten components have complete E0/E1 provenance, license, and version
  records.
- At least three components have E2 evidence from recorded sandbox builds.
- One differential-drive composition has E3 simulation evidence.
- M15 later supplies the first E4 reference-robot record; it is not currently
  claimed.
- Contradictory evidence remains separately queryable by environment.
- E4/E5 promotion requires complete evidence and human review.

## Guardrails

- No unknown source is installed with elevated privileges.
- No external package, SDK, firmware, or source code is executed outside a
  sandbox and explicit policy/approval path.
- Registry snapshots identify benchmark inputs to prevent leakage.
- The existing Jetson/ESP32/D455/LiDAR target remains a planned Reference A,
  not a verified configuration.

See `docs/architecture_v0.4.md` for the current G12.5 structure and
`docs/decisions/0009-scalable-evidence-registry-after-composable-core.md` for
the sequencing decision.
