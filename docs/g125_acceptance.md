# G12.5 acceptance evidence

**Status:** PASS (2026-10-12)

G12.5 refactors the core into architecture-aware, composable, and safety-gated
integration. This gate is software and virtual-MVP evidence only; it does not
claim Jetson, controller, sensor, or physical-robot readiness.

| Criterion | Evidence | Result |
|---|---|---|
| A. v0.3 complete template has no regression | `tests/test_template_expander.py` exercises the registry-authorized v0.3 expansion and safe output writer. | PASS |
| B. Known components produce a project | `tests/test_mvp_pipeline.py::test_run_prepares_a_validated_diff_drive_navigation_mvp` renders differential drive, LiDAR, camera, and Nav2 into one package root. Existing M8 Jazzy build evidence remains recorded in `docs/AI_HANDOFF.md`. | PASS |
| C. Host + MCU responsibilities | `tests/test_architecture_resolver.py::test_resolve_assigns_navigation_to_linux_host_and_motor_control_to_mcu`. | PASS |
| D. MCU-only Nav2 is blocked | `tests/test_architecture_resolver.py::test_resolve_blocks_mcu_only_navigation_request`. | PASS |
| E. Unknown-device fallback | `tests/test_unknown_component.py` returns provisional plus human approval for documented hardware and blocked for undocumented hardware. | PASS |
| F. Diff, confirmation, evidence, rollback semantics | `tests/test_mutation_safety.py`, `tests/test_constrained_repairer.py`, and workspace confirmation tests in `tests/test_project_api.py` require readiness/confirmation and retain reviewed diffs/rollback-safe scope. | PASS |
| G. v0.3 evidence remains readable | `tests/test_v04_schema_migration.py` validates `migrate_v03_registry()` without inventing verification. | PASS |
| H. Regression suite remains green | Targeted acceptance suite plus the complete **89-test** suite passed on 2026-10-12. | PASS |

The frozen presentation contract is `GET /api/v1/core/schema`. M14B consumes
the frozen core and v0.6 evidence read model without browser ROS/shell/control
authority.
