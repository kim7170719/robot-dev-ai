# AI handoff (live)

Updated: 2026-10-01. Next editor should refresh this file after the next real task.

## Where we are

**G0–G10 PASS** on Ubuntu. MVP research core has started. The next milestone is **M11 Auto Debug Agent**.

G4 was merged into `develop` through PR [#10](https://github.com/kim7170719/robot-dev-ai/pull/10). Create a new feature branch for M5; do not develop directly on `develop`.

## Done

| Gate | What | Evidence |
|---|---|---|
| G0 | Repo, GitHub, dual-OS clone sync | tag `g0-environment-baseline` on `main` |
| G1 | ROS 2 Jazzy, own package, launch, topic/service/action | `docs/m1_g1.md` |
| G2 | `simple_diff_robot` URDF + ros2_control + RViz | `/cmd_vel` TwistStamped moves `/odom` |
| G3 | Isaac Sim 4.5 Docker, Humble↔Jazzy via CycloneDDS | `/cmd_vel` → `/odom`; tag `m3-g3-isaac-sim` |
| G4 | Nav2 + SLAM, host RViz goal, Isaac Sim goals | `experiments/raw/M4-G4.md` |
| G5 | Isaac ROS GPU image-pipeline baseline | `docs/isaac_ros_baseline.md`; `scripts/m5_image_proc_smoke.sh` |
| G6 | Proposal and MVP scope freeze | `docs/m6_proposal.md`; user accepted scope |
| G7 | Hardware capability drives template expansion | `registry/models.py`; registry + template tests |
| G8 | Structured spec produces a buildable ROS skeleton | `TemplateExpander`; generated `demo_diff_drive` passed Jazzy `colcon build` |
| G9 | Natural language produces a validated robot specification | Gemini Free Tier request → differential drive, LiDAR, RGB camera, Nav2, Isaac Sim spec |
| G10 | Structured rules resolve compatible packages or explicit blocks | 9 resolver tests: capability, Jazzy, platform, GPU support, message conversion, dependency |

Isaac Sim G4 CLI results (2026-09-21):

- `navigate_to_pose` `(1.0, 0.0)` SUCCEEDED (odom 3.09 → 0.96)
- `navigate_to_pose` `(2.0, 2.2)` around box at `(2.0, 1.0)` SUCCEEDED (odom 1.87, 2.25)

## In progress

- M11 Auto Debug Agent: build/launch missing-package/node, topic type, TF, controller, collector-timeout diagnoses, successful-build classification, a three-attempt repair limit, read-only command collection, serializable failure reports, and constrained manifest diff proposals are implemented; patch application remains

## M5 evidence

- Reproducible image: `docker/Dockerfile.isaac-ros-image-proc`; local tag `robot-dev-ai/isaac-ros-image-proc:4.5`
- The project smoke-test script passed twice on 2026-10-01: official NGC 4.0.0 quickstart rosbag → `nvidia::isaac_ros::image_proc::ResizeNode` → `/resize/image` (`480×288`, `rgb8`)
- Host GPU is RTX 2080 Ti (Turing, compute capability 7.5). Isaac ROS 4.5 officially requires Ampere+ on x86_64, so G5 is a reproducible but unsupported-platform experimental result.

## Not done

- M11+ debugging and validation agents
- Real-hardware / Jetson
- Isaac Sim RTX/PhysX LiDAR (synthetic 2D scan is the G4 path)
- Full URDF physics in Isaac Sim (crashes; G3/G4 use kinematic cube + raycast)
- Cosmos (forbidden as Isaac physics replacement; not before M13)

## Recently touched files (M10 checkpoint)

- `agent/requirement_agent/`, `agent/schemas/` — M9 parser, specification schema, provenance, ambiguity handling, Gemini adapter, and structured-output retry
- `agent/compatibility_resolver/`, `registry/models.py` — M10 rule resolver, target-platform constraints, interface dependencies, and conversion records
- `agent/auto_debug/` — M11 non-mutating diagnoses from build, topic, TF, and controller evidence
- `agent/template_engine/` — deterministic registry-authorized expansion and safe output writing
- `templates/` — differential-drive, LiDAR, camera, Nav2, and Isaac ROS project fragments
- `tests/test_template_expander.py` — expansion, refusal, materialization, and fragment tests

M8 build evidence: temporary generated `demo_diff_drive` passed `colcon build --packages-select demo_diff_drive` on 2026-10-01.

M10 boundary: static rules distinguish validated, experimental, and blocked configurations. Build, ROS graph, Isaac Sim, Jetson, and real-hardware evidence remain M11+ responsibilities.

M11 live evidence: `ros2 node list` and `ros2 topic list -t` returned successfully; `ros2 control list_controllers` timed out at 10 seconds. The node snapshot contained only `/tm_smooth_controller`, so M11 diagnosed missing `/controller_manager`; no host process was mutated.

M11 build evidence: `colcon build --packages-select simple_diff_robot simple_diff_nav` exited 0 on 2026-10-01, and `AutoDebugAgent` classified its evidence as `build-succeeded`.

## Known issues / debt

- **Humble CycloneDDS ↔ Jazzy**: `/clock` publisher type hash can show `INVALID`; wall-clock stamps + `use_sim_time:=false` is the working G4 pattern
- **`/cmd_vel` types**: ros2_control (host G2) wants **TwistStamped**; Nav2 Jazzy collision_monitor publishes **Twist**. Isaac G4 script subscribes to Twist
- **collision_monitor** must use `base_link` (not TurtleBot `base_footprint`) or it zeros `/cmd_vel`
- **Kit `--exec`**: container must use `--entrypoint /isaac-sim/kit/kit` or the script never runs
- Keep `UPDATE_SUB` (or equivalent) so the Kit update callback is not garbage-collected
- Isaac `m4_lidar_scan.py` and `room_scan.py` must stay geometrically in sync (8×6 m room, box at 2,1)
- `docs/environment.md` is aligned with the verified 580.178.04 driver (ADR 0003)
- G4 `cmd_vel` timeout (0.5 s) is in the script on disk; running containers may be older

## Environment (Ubuntu)

| Item | Value |
|---|---|
| OS | Ubuntu 24.04 LTS |
| GPU | RTX 2080 Ti 11 GB |
| Driver for Isaac | 580.178.04 (not 595) |
| ROS | Jazzy at `/opt/ros/jazzy` |
| Isaac Sim | Docker `nvcr.io/nvidia/isaac-sim:4.5.0`, Humble rclpy inside |
| DDS | `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` + unicast peer `127.0.0.1` both sides |
| RViz | `__GL_THREADED_OPTIMIZATIONS=0` |

FastDDS Humble 2.x ↔ Jazzy 3.x is one-way; do not go back to FastDDS for host↔container.

## Windows / Ubuntu

- Two clones; GitHub only sync. No shared working tree
- Windows: docs/Git only. Do not install ROS / Isaac / Nav2 / Cosmos
- Before reboot: commit, push, update `docs/os_handoff.md`
- After reboot: open the GitHub `os_handoff.md` URL, not the previous chat

## Git

| Field | Value |
|---|---|
| Branch | `feature/m5-isaac-ros` |
| `develop` | `d3fdd40` — M5 handoff merged |
| `main` | `c771bf1` — do not develop here |
| Working tree | Clean after merging G4 and this handoff update |

## Suggested next step

1. Start M6 Proposal documentation; do not begin schema or agent implementation before the MVP scope is frozen.
