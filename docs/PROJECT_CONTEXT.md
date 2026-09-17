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

- `ros_ws/`: ROS 2 workspace
- `agent/`: AI orchestration (planner, tools, prompts, schemas)
- `registry/`: hardware / package / capability / compatibility knowledge
- `templates/`: reusable ROS project fragments
- `simulator/`: Isaac Sim worlds, scenarios, evaluator
- `validator/`: build / ROS graph / TF / topics / navigation checks
- `experiments/`: raw logs and later analysis

## Current phase

M0 Environment Audit. After Gate 0, the next issue is M1-01: install and verify ROS 2 Jazzy. Do not start Cosmos before M13.
