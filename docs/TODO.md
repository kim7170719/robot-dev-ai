# TODO

## Completed — M11 Auto Debug Agent

- **Purpose:** Diagnose build and ROS graph failures through explicit tools and evidence.
- **Files:** `agent/`; `validator/`
- **Status (2026-10-06):** **G11 PASS.** `BuildCommandCollector.collect()` runs only package-name-validated `colcon build --packages-select` commands without a shell. `AutoDebugAgent.diagnose()` classifies successful builds and has evidence-based, non-mutating diagnoses for missing ROS packages/nodes, topic type mismatches, missing TF edges, inactive controllers, collector timeouts, and a maximum repair-attempt stop condition. `RosRuntimeCollector.collect_snapshot()` parses five allowlisted read-only inspection results, including one-shot `/tf` and `/tf_static` edges. `AutoDebugAgent.diagnose_snapshot()` checks required nodes, topic types, controllers, and TF edges without inferring state from failed collection. Each result carries a serializable failure report and can propose a constrained `package.xml` dependency diff without writing it.
- **Done when:** a failed build or ROS graph can produce an evidence-backed diagnosis and a bounded repair suggestion.

## P1 — important

### M5 Isaac ROS baseline (Gate G5) — done

- **Purpose:** One reproducible NVIDIA-accelerated ROS pipeline, documented.
- **Files:** new `docs/isaac_ros_baseline.md`; likely `docker/` compose or run notes; no ROS distro change
- **Status (2026-10-01):** PASS. The project script `scripts/m5_image_proc_smoke.sh` passed twice: official rosbag → Isaac ROS `ResizeNode` → `/resize/image` (`480×288 rgb8`) in `robot-dev-ai/isaac-ros-image-proc:4.5`. Runbook: `docs/isaac_ros_baseline.md`; decision: ADR 0005. RTX 2080 Ti is Turing and outside Isaac ROS 4.5's x86_64 Ampere+ support matrix.

### Align `docs/environment.md` with driver 580 (done in G4 checkpoint)

- **Purpose:** Audit file still lists 595; Isaac Sim 4.5 needs 580 (ADR 0003).
- **Files:** `docs/environment.md`
- **Done:** `nvidia-smi` reports 580.178.04 and the environment audit matches.

## P2 — later

### Swap synthetic `/scan` for Isaac PhysX or RTX LiDAR

- **Purpose:** G4 used Python raycast (ADR 0004). Real sensor path when VRAM/Kit is stable.
- **Files:** `simulator/worlds/m4_lidar_scan.py`; keep `/scan` `LaserScan` + `lidar_link`
- **Done when:** Isaac publishes `/scan` from a simulator sensor; SLAM/Nav2 still activate; host `scan_sim` unused with `use_isaac_sim:=true`.

### Isaac Sim URDF physics (not kinematic)

- **Purpose:** G3/G4 robot is a kinematic cube; full URDF articulation crashed.
- **Files:** `simulator/worlds/import_urdf.py`, USD under `~/docker/isaac-sim/documents/`
- **Done when:** URDF articulation runs 60+ s without Kit crash and still talks `/cmd_vel` `/odom`.

### M6 proposal docs

- **Purpose:** Research questions and MVP freeze before schema/agent work.
- **Files:** `docs/m6_proposal.md`
- **Status (2026-10-01):** Accepted. MVP scope is frozen.
- **Done when:** problem, gap, architecture, RQs, metrics, baselines, and scope freeze are reviewed and accepted. No Cosmos.

### Schema / agent / registry (M7+)

- **Purpose:** Actual product contributions; empty dirs today (`agent/`, `registry/`, `templates/`, `validator/`).
- **Files:** those trees; Pydantic schemas; SQLite first
- **Status (2026-10-01):** M7 PASS. `registry.models.RobotKnowledgeRegistry` validates hardware, driver, ROS interface, capability, package, and compatibility records; hardware capability selects a LiDAR template through `TemplateExpander`.
- **Done when:** one hardware→capability record can drive a template expand. Not before M5/M6 unless the user reorders.

### M8 Template Engine (Gate G8)

- **Purpose:** Deterministically expand verified templates from a structured specification.
- **Files:** `agent/template_engine/`; `templates/`
- **Status (2026-10-01):** PASS. Registry-authorized templates cover differential drive, LiDAR, camera YAML, Nav2 YAML, Isaac ROS image processing, package metadata, and launch files. A generated `demo_diff_drive` ament_python package passed Jazzy `colcon build`.
- **Done when:** a structured specification deterministically produces a buildable project skeleton without an LLM.

### M10 Compatibility Resolver (Gate G10)

- **Purpose:** Resolve the frozen MVP specification through structured registry rules, not LLM guessing.
- **Files:** `agent/compatibility_resolver/`; `registry/models.py`
- **Status (2026-10-01):** PASS. The resolver verifies capability requirements, Jazzy drivers, target platform, package dependencies, interface IDs, conversion packages, and package GPU requirements. It distinguishes validated, experimental, and blocked results; the M5 Turing image pipeline is explicitly experimental rather than vendor-supported.
- **Done when:** a structured request returns selected packages or an explainable blocked result.
