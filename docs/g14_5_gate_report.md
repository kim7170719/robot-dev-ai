# G14.5 component library gate report

**Updated:** 2026-10-14  
**Branch:** `feature/g14.5-component-library-bootstrap`  
**Scope:** P0 data/catalog, deterministic planning, typed read-only API, and
Registry GUI inspection. This report does not claim external source execution,
hardware operation, or E4 evidence.

## Result

**G14.5-P planning gate: PASS.** The P0 component library can produce a
deterministic Reference Robot A architecture and component composition while
preserving missing evidence, blocked hardware readiness, and source-review
boundaries.

**E2 build sub-gate: PENDING EXTERNAL PREREQUISITES.** The sandbox endpoint and
fixed build command already exist, but no approved archive, SHA-256 allowlist,
or local ROS Jazzy build image is configured. No E2 result is claimed here.

## Acceptance matrix

| Test | Evidence | Result |
|---|---|---|
| T1 known software composition | `tests/test_g145_gate.py::test_t1_known_software_composition_is_deterministic` | PASS |
| T2 host + MCU architecture | `tests/test_g145_gate.py::test_t2_host_mcu_architecture_assigns_linux_and_realtime_work` | PASS |
| T3 full Reference Robot A | `tests/test_g145_gate.py::test_t3_full_reference_robot_has_reviewable_outputs` | PASS |
| T4 no full-robot template | `tests/test_g145_gate.py::test_t4_dynamic_component_templates_work_without_a_full_robot_template` | PASS |
| T5 unknown component | `tests/test_g145_gate.py::test_t5_unknown_component_is_blocked_not_invented` | PASS |
| T6 MCU constraint | `tests/test_g145_component_library.py::test_seed_manifest_preserves_mcu_only_navigation_conflict` | PASS |
| T7 evidence filtering | `tests/test_g145_gate.py::test_t7_manifest_does_not_promote_documented_or_simulated_records_to_real` and `test_t7_evidence_gaps_keep_unready_seed_artifacts_visible` | PASS |
| T8 M14 compatibility | complete regression suite, including `tests/test_project_api.py` | PASS |

## Deliverables

- `data/registry/seed_manifest.yaml`: 11 P0 artifact records, all source and
  evidence boundaries explicit.
- `registry/g145.py`: schema, manifest loader, and compiler to the frozen v0.4
  resolver registry.
- `data/reference_robot_a/`: declared specification and expected plans.
- `agent/component_library/`: deterministic Reference Robot A planner.
- `GET /api/v1/component-library` and
  `GET /api/v1/component-library/reference-robot-a/plan`: typed read-only
  inspection surfaces.
- Registry GUI: searchable P0 artifact metadata and Reference Robot A plan
  inspection.

## Remaining external gates

- Human review of external source metadata before acquisition.
- Approved local archives, SHA-256 allowlist, and a local ROS Jazzy image for
  actual E2 sandbox builds.
- M15 hardware observations for E4.
- Independent human-reviewed reports for E5.
