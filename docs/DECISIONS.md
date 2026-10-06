# Decisions (summary)

Numbered ADRs live in `docs/decisions/`. This page is the index for agents. Add a new `NNNN-*.md` when a stack or architecture choice changes.

## Accepted

| ID | Decision | Why | Revisit |
|---|---|---|---|
| 0000 | Ubuntu 24.04, ROS 2 Jazzy only, Python 3.12, Isaac Sim, diff-drive MVP | Guide v0.2 freeze | Only with a new ADR |
| 0001 | RViz: `__GL_THREADED_OPTIMIZATIONS=0` | NVIDIA open-module GLX / Ogre crash | If driver/GL stack changes |
| 0002 | Isaac Sim **4.5 Docker**, not 5.x/6.0 | RTX 2080 Ti 11 GB < 16 GB 5.x minimum | If GPU ≥16 GB |
| 0003 | Host NVIDIA driver **580** (not 595) | 595 segfaults `librtx.scenedb` in Isaac 4.5 | If moving to Isaac 5.x |
| 0004 | Synthetic 2D `/scan` (room raycast), not RTX LiDAR | Unblocks SLAM/Nav2; RTX LiDAR crash risk on 11 GB | When PhysX/RTX lidar is stable |
| 0005 | Isaac ROS 4.5 project-owned Docker image + image-proc binary baseline | Isolates CUDA dependencies and gives a repeatable first accelerated pipeline | If a supported GPU or official deployment path changes |
| 0006 | Cosmos is an optional scenario-proposal extension | Turing host cannot run the supported path; it must not block productization | Supported hardware plus a measurable O1 hypothesis |
| 0007 | GUI accesses core only through a typed API | Preserve constrained execution and keep frontend free of ROS/shell logic | If a reviewed deployment boundary replaces FastAPI |
| — | CycloneDDS + unicast `127.0.0.1` for Humble container ↔ Jazzy host | FastDDS 2.x/3.x is one-way | If both sides share one RMW version |
| — | Isaac G4 stamps = **wall clock**; `use_sim_time:=false` | Humble `/clock` type-hash / TF_OLD_DATA | If DDS type matching is fixed |
| — | Nav2 `/cmd_vel` = **Twist**; host ros2_control = **TwistStamped** | Jazzy Nav2 vs Jazzy diff_drive | Keep both mappings documented |
| — | Kit scripts: `--entrypoint /isaac-sim/kit/kit` + `--exec`; rclpy on a thread; keep update subscription | `--exec` otherwise never runs; `spin_once` in the Kit loop crashes | Isaac 5.x APIs |
| — | Dual clone + GitHub only; never share a working tree across OS | Dual-boot | — |

## Rejected

- Isaac Sim 5.x/6.0 on this GPU
- FastDDS as the Humble↔Jazzy bridge
- Native Isaac Sim on Ubuntu 24.04 (use Docker)
- Multiple ROS distros in MVP
- Windows as official ROS/Isaac host
- Cosmos instead of Isaac physics (not before M13)
- Extra robot morphologies in MVP
- Training a foundation model in this repo

## Still open

- When to replace synthetic lidar
- Whether to retry full URDF physics vs stay kinematic for research demos
