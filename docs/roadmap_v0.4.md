# Roadmap v0.4 — Composable, architecture-aware integration

**Status:** active execution baseline (2026-10-12)

**Source:** user-supplied *Robot Dev AI / RoboWeave Roadmap v0.4 — Composable &
Architecture-Aware Refactor*

**Supersedes:** the future sequencing in `docs/roadmap_v0.3.md`; it does not
rewrite historical G0–G12, G14, or M13 evidence.

## Why this changes the plan

The virtual MVP can parse a differential-drive request, resolve a known
registry, render templates, build, diagnose, and validate in Isaac Sim. Its
known limitation is generalization: it does not yet make a first-class,
evidence-backed decision when a robot must be assembled from known components,
includes an MCU, has a non-ROS device, lacks a driver, has insufficient
compute, or is unknown.

v0.4 therefore adds a single, controlled core refactor before new core GUI
schema work or real-robot integration. It retains the completed M14 UI as a
presentation artifact; the UI must not be treated as v0.4-schema complete
until the core freeze below succeeds.

## Main path

```text
G0–G12 virtual MVP (PASS) → G12.5 composable architecture refactor
→ M14B schema-aligned GUI → M15 heterogeneous real-robot bring-up
→ M16 sim-to-real benchmark → M17 thesis freeze → M18 release
```

M13/Cosmos remains Optional Extension O1. It never blocks this path and is not
a physics or real-robot validation authority.

## G12.5 scope

| Workstream | Deliverable | Gate intent |
|---|---|---|
| Schema + migration | Architecture plan, composition plan, capability/constraint, verification state, resource profile, and v0.3 migration | Old evidence remains readable |
| Architecture Resolver | Explainable compute/control topology selection | Detect MCU-only/Nav2 conflict; allocate Host/MCU duties |
| Capability Registry | Hardware, software, firmware, transport, resource, limitation, and provenance fields | Explain why a component is runnable, degraded, blocked, or unknown |
| Composition Planner | Deterministic component graph | Compose known components without a complete robot template |
| Composable templates + adapters | Component templates and stable adapter contracts | Preserve current template compatibility; start with serial, micro-ROS, and ros2_control boundaries |
| Readiness + safety | Structured readiness evidence; mutation transaction/approval/rollback | No high-risk action proceeds without explicit human approval |
| Validation evidence | PASS, FAIL, BLOCKED, NOT_TESTED, UNSUPPORTED, DEGRADED plus coverage/confidence | Separate evidence state from binary outcome |

## G12.5 acceptance criteria

1. A complete supported template has no regression from v0.3 behavior.
2. A robot with no full template but known components produces a deterministic,
   buildable composition plan/project.
3. A Linux Host + ESP32/STM32 request produces explicit host/MCU
   responsibilities.
4. An MCU-only request requiring Nav2/perception is blocked as an architecture
   conflict, not emitted as an executable project.
5. Documented unknown hardware enters provisional-profile/adapter/human-approval
   flow; undocumented unknown hardware is `BLOCKED`.
6. Generation and repair mutations provide diff, confirmation, evidence, and
   rollback semantics.
7. v0.3 registry/project evidence is readable through a versioned migration.
8. The existing automated suite remains green and new v0.4 architecture,
   composition, adapter, unknown-device, and migration tests pass.

## Explicitly out of scope

- Universal robot-morphology support; differential drive remains the reference.
- Unsupervised firmware generation/flashing or unknown-protocol reverse
  engineering.
- Treating experimental hardware as verified hardware.
- New GUI visual work, 3D viewport work, SaaS/multi-user work, or Cosmos as a
  core dependency before G12.5.

## Current status

- G0–G12: **PASS** — preserved as virtual-only evidence.
- G14: **PASS** — preserved as the existing typed-API GUI; its v0.4 schema
  alignment is deferred to M14B.
- M15 physical preflight: **PAUSED, not discarded** — it resumes after G12.5;
  its safety and readiness items become inputs to the new readiness/safety
  model.
- G12.5: **STARTED (architecture/document baseline only)** — no v0.4 runtime
  code or real-hardware claim yet.

## Implementation order

1. Schema v0.4 and v0.3 migration.
2. Architecture Resolver.
3. Registry capability/constraint upgrade.
4. Composition Planner.
5. Template componentization with backward compatibility.
6. Adapter contracts and limited initial adapters.
7. Hardware Readiness and safety transaction model.
8. Regression/acceptance tests.
9. Freeze Core API schema, then update M14B UI.

See `docs/architecture_v0.4.md` for boundaries and `docs/decisions/0008-*` for
the recorded architectural decision.
