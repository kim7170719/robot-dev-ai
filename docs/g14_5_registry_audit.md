# G14.5 component-library registry audit

**Date:** 2026-10-14  
**Scope:** read-only audit before G14.5 implementation. No source was fetched,
no component was imported, and no evidence level was changed.

## Decision

G14.5 should extend the existing versioned registry rather than replace it.
The current core already provides the resolver, composition, adapter, trusted
source, and evidence seams needed for a narrow seed library. It does **not**
yet contain a durable component artifact catalog, seed manifest, Reference
Robot A specification, or G14.5 acceptance suite.

The smallest safe next increment is therefore a data-backed artifact layer and
a P0-only seed manifest. It must preserve the frozen v0.4 API and M14 GUI
read-model contracts.

## Current inventory

| Area | Existing implementation | G14.5 reuse | Gap |
|---|---|---|---|
| v0.3 registry | `registry/models.py` | hardware, drivers, interfaces, capabilities, packages, compatibility, conversions | no generic artifact/source/evidence linkage per component |
| v0.4 composable core | `registry/v04.py` | hardware/software profiles, adapter contracts, constraints, architecture and composition plans | composition accepts only capability → template mapping; no data catalog or validation recipes |
| v0.5 trusted sources | `registry/v05.py`, `agent/source_onboarding/` | source, license, lifecycle, provenance, audit-bound local bundle gates | management data is currently an in-memory default document with two components |
| v0.6 evidence | `registry/v06.py`, `agent/evidence_registry/` | E0–E5 contextual evidence, conflicts, review queue, snapshots | default document has only `generic-diff-base-e3`; no G14.5 seed evidence entries |
| architecture resolution | `agent/architecture_resolver/` | host/MCU topology, Nav2-on-Linux rule, MCU-only Nav2 conflict | no Jetson/ESP32 seed profiles or transport selection policy |
| composition | `agent/composition_planner/` | deterministic capability → template plan, explicit missing-template block | no component-graph dependencies, adapter selections, or fallback composition bindings |
| adapter resolution | `agent/adapter_resolver/` | declared device/transport/software checks | only `serial`, `micro-ros`, and `ros2-control` adapter kinds; no Twist normalization kind |
| templates | `templates/` and `agent/template_engine/` | differential-drive, LiDAR, camera, Nav2, Isaac ROS image-processing rendering | no dedicated `ros2_control`, controller, transport, or component-template manifests |
| presentation | `/api/v1/registry/management`, `/api/v1/evidence/*`, Registry/Evidence GUI views | read-only source, lifecycle, license, evidence, and snapshot display | GUI does not expose capabilities, interfaces, transports, constraints, or limitations per seed artifact |

## Existing baseline facts

- The default M14 Registry Management document exposes only
  `generic-diff-base` and `generic-diff-driver`, both attributed to the project
  source. It is not a component library.
- The default evidence document retains one virtual-only E3 PASS record:
  `generic-diff-base-e3` in Ubuntu 24.04 / ROS Jazzy / amd64.
- Existing templates cover differential drive, LiDAR, camera, Nav2, and Isaac
  ROS image processing. This is a useful starting point, but template presence
  is not source, build, simulation, or hardware evidence by itself.
- Current resolver tests already prove two required G14.5 behaviors: a Linux
  host receives Nav2 responsibility while an MCU receives motor/encoder work,
  and an MCU-only navigation request is blocked.
- `data/registry/`, `reference_robot_a/`, and a persisted seed manifest do not
  yet exist.

## Schema fit and required normalization

The G14.5 handoff correctly distinguishes artifacts. The existing models only
partially represent that distinction. A compatible addition should introduce a
new data-backed component artifact record rather than overload
`Capability.template_id` or `ManagedComponent`.

Minimum artifact kinds required by the handoff:

```text
hardware_profile | software_package | driver_sdk | protocol | adapter
component_template | simulation_adapter | validation_recipe | evidence_record
```

Each stored component should retain, at minimum, its source/license,
capabilities, interfaces, transports, requirements, constraints, limitations,
target evidence level, and provenance. The artifact record must link into the
existing v0.3/v0.4 IDs instead of duplicating resolver facts.

The first normalization must not:

- alter existing v0.4 `RegistryDocumentV04` semantics;
- re-label E1/E2 as E4;
- add unreviewed external metadata as a verified fact; or
- change M14 browser authority beyond its typed read-only API boundary.

## G14.5 seed assessment

The handoff names 17 candidates, exceeding its stated 10–15 target. The
recommended initial P0 manifest is intentionally narrower:

| ID | Artifact role | Initial evidence ceiling | Existing local relation |
|---|---|---:|---|
| `differential-drive` | component template/base | E3 historical composition only | existing template and virtual MVP |
| `jetson-generic` | hardware profile | E1 | no local E4 fact |
| `esp32` | hardware profile | E1 | no local hardware fact |
| `serial-bridge` | adapter | E1, E2 only after approved build | adapter seam exists |
| `ros2-control` | software/package + template binding | E1, E2 only after approved build | adapter kind exists |
| `diff-drive-controller` | software/package + template binding | E1, E2 only after approved build | controller template exists, not artifact metadata |
| `ld06` | hardware profile/driver | E1 | no local E2/E4 fact |
| `realsense-d455` | hardware profile/driver | E1 plus separate historical host observation if migrated | D455 UI/runtime integration exists, not G14.5 component evidence |
| `nav2` | software package/template | E3 historical virtual composition | existing Nav2 template and G12 virtual result |
| `isaac-sim` | simulation adapter | E3 historical virtual composition | existing G12/M14 simulation stack |
| `twist-twiststamped` | adapter | E1, E2 only after approved build | known interface mismatch documented |

`micro-ros`, `can-bridge`, `stm32-generic`, `dynamixel-ax12-class`,
`generic-pwm-motor`, and `x86-linux` should start as P1 or generic variants
after P0 graph tests pass. This keeps G14.5 narrow and avoids inventing facts
about hardware that is not present.

## Acceptance-test readiness

| Handoff test | Current position | Required G14.5 work |
|---|---|---|
| T1 known software composition | partial: templates and virtual Nav2/Isaac path exist | data-backed component dependencies and deterministic composition output |
| T2 host + MCU architecture | foundation PASS in G12.5 | use Jetson/ESP32 seed profiles and transport evidence in a G14.5 fixture |
| T3 full Reference Robot A | absent | reference spec, plans, drivers/adapters/checklist output |
| T4 no full robot template | partial: component planner composes templates | fixture proving dynamic composition of all known seed components |
| T5 missing component | foundation exists in unknown-component resolver | bind it to source-discovery/blocked presentation without fetching |
| T6 MCU-only Nav2 | foundation PASS in G12.5 | retain regression under G14.5 fixture |
| T7 evidence filtering | v0.6 foundation exists | seed-level assertions that E0/E1 never appear as E4 |
| T8 M14 compatibility | unproven for seed migration | API/GUI regression tests against default M14 flow |

## External boundaries

- No G14.5 E2 build may be claimed until an operator supplies an approved local
  archive, allowlisted SHA-256, and local ROS Jazzy build image.
- No E4 claim may be created until M15 records actual hardware/environment
  observations.
- Source discovery may record only reviewed metadata. The audit does not
  authorize mass crawling, cloning, package installation, or arbitrary source
  execution.
- E5 remains unavailable without independent human-reviewed community reports.

## Recommended implementation order

1. Add `data/registry/seed_manifest.yaml` containing only P0 identifiers,
   target evidence ceilings, and explicit `pending-source-review` entries.
2. Add typed artifact schema plus loader/validation that links to the frozen
   v0.3/v0.4 registry without changing legacy contracts.
3. Add local, project-owned P0 entries only where provenance is already known;
   retain external candidates as E0/E1 placeholders until reviewed.
4. Bind the seed fixture to existing differential-drive/Nav2/LiDAR/camera
   templates and current adapter contracts.
5. Add T1–T8 fixture tests, Reference Robot A expected plans, and the gate
   report. Run E2 only when its preconditions exist.
6. Extend the existing read-only Registry view through typed API fields after
   the schema and fixtures are stable.

## Branch note

The handoff proposes branching directly from `develop`. Repository rules say
not to develop on `develop`; G14.5 should use a dedicated `feature/` branch
from the agreed integration baseline after the current branch is reviewed or
merged. This audit was performed on `refactor/composable-architecture-v0.4`.
