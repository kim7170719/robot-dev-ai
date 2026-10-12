# Project context

Read this with `CURSOR_PROJECT_GUIDE.md` before starting a task. Change only the current milestone.

## Goal

Build an open-source, model-agnostic, hardware-aware AI robot development platform. Natural-language robot requirements are turned into a structured spec, then into ROS 2 packages via templates, then built, diagnosed, validated in Isaac Sim, and later deployed to Jetson.

## Contributions

1. Robot Integration Schema: Hardware → Driver → ROS Interface → Capability
2. AI Integration Agent: parse requirements, select packages/templates, generate config, diagnose
3. Simulation Validation Pipeline: Build → Launch → ROS Graph / TF / Navigation → Isaac Sim
4. Community Experience Registry: verified configs, failures, and fixes for later reuse

## Reference stack

| Layer | Baseline |
|---|---|
| OS | Ubuntu 24.04 LTS |
| Helper OS | Windows 10 |
| ROS | ROS 2 Jazzy |
| Python | System Python 3.12 series |
| Simulator | Isaac Sim |
| NVIDIA ROS | Isaac ROS |
| Navigation | Nav2 |
| Control | ros2_control |
| Agent backend | Python + FastAPI |
| Schema | Pydantic + YAML / JSON |
| Registry | SQLite first |
| First robot | Differential drive |

Do not change ROS distribution, system Python, or core frameworks without a written decision in `docs/decisions/`.

## Architecture layers in this repo

- `api/`: typed Robot Dev AI presentation boundary (M14)
- `gui/`: web presentation layer (M14)
- `ros_ws/`: ROS 2 workspace
- `agent/`: AI orchestration (planner, tools, prompts, schemas)
- `registry/`: hardware / package / capability / compatibility knowledge
- `templates/`: reusable ROS project fragments
- `simulator/`: Isaac Sim worlds, scenarios, evaluator
- `validator/`: build / ROS graph / TF / topics / navigation checks
- `experiments/`: raw logs and later analysis

## Current phase

G0–G12 virtual MVP and G14 GUI are preserved evidence. The active milestone is
G12.5: a controlled v0.4 refactor that adds architecture-aware, capability-
aware, composable integration before resumed real-hardware work. M15 physical
preflight is paused, not passed or discarded. Cosmos remains Optional Extension
O1. See `docs/roadmap_v0.4.md` and `docs/architecture_v0.4.md`.
