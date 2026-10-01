# AI handoff (live)

Updated: 2026-10-01. Next editor should refresh this file after the next real task.

## Where we are

**G0–G4 PASS** on Ubuntu. MVP Phase A (M1–M4) is done in substance. Next milestone is **M5 Isaac ROS** (not started).

G4 was merged into `develop` through PR [#10](https://github.com/kim7170719/robot-dev-ai/pull/10). Create a new feature branch for M5; do not develop directly on `develop`.

## Done

| Gate | What | Evidence |
|---|---|---|
| G0 | Repo, GitHub, dual-OS clone sync | tag `g0-environment-baseline` on `main` |
| G1 | ROS 2 Jazzy, own package, launch, topic/service/action | `docs/m1_g1.md` |
| G2 | `simple_diff_robot` URDF + ros2_control + RViz | `/cmd_vel` TwistStamped moves `/odom` |
| G3 | Isaac Sim 4.5 Docker, Humble↔Jazzy via CycloneDDS | `/cmd_vel` → `/odom`; tag `m3-g3-isaac-sim` |
| G4 | Nav2 + SLAM, host RViz goal, Isaac Sim goals | `experiments/raw/M4-G4.md` |

Isaac Sim G4 CLI results (2026-09-21):

- `navigate_to_pose` `(1.0, 0.0)` SUCCEEDED (odom 3.09 → 0.96)
- `navigate_to_pose` `(2.0, 2.2)` around box at `(2.0, 1.0)` SUCCEEDED (odom 1.87, 2.25)

## In progress

- M5 Isaac ROS baseline is ready to begin on a new `feature/m5-*` branch

## Not done

- M5 Isaac ROS container + one reproducible pipeline (`docs/isaac_ros_baseline.md`)
- M6+ research core (schema, agent, registry, validator)
- Real-hardware / Jetson
- Isaac Sim RTX/PhysX LiDAR (synthetic 2D scan is the G4 path)
- Full URDF physics in Isaac Sim (crashes; G3/G4 use kinematic cube + raycast)
- Cosmos (forbidden as Isaac physics replacement; not before M13)

## Recently touched files (G4 checkpoint)

- `ros_ws/src/simple_diff_nav/` — `scan_sim.py`, `odom_to_tf.py`, `room_scan.py`, slam/nav2 launch+params, tests
- `simulator/worlds/m4_lidar_scan.py` — Isaac Sim `/scan` `/odom` `/clock`, Twist `/cmd_vel`
- `docs/m4_nav2.md`, `docs/progress.md`, `docs/decisions/0004-synthetic-2d-lidar.md`
- `experiments/raw/M4-G4.md`

G4 integration: PR [#10](https://github.com/kim7170719/robot-dev-ai/pull/10) merged to `develop` as `73d2aba`.

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
| Branch | Start M5 from a new `feature/m5-*` branch based on `develop` |
| `develop` | `73d2aba` — G4 merged |
| `main` | `c771bf1` — do not develop here |
| Working tree | Clean after merging G4 and this handoff update |

## Suggested next step

1. Start M5: Isaac ROS container + `docs/isaac_ros_baseline.md` (Gate G5).
