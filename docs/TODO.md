# TODO

## P0 — M5 Isaac ROS baseline

## P1 — important

### M5 Isaac ROS baseline (Gate G5)

- **Purpose:** One reproducible NVIDIA-accelerated ROS pipeline, documented.
- **Files:** new `docs/isaac_ros_baseline.md`; likely `docker/` compose or run notes; no ROS distro change
- **Done when:** Isaac ROS container runs on this host; at least one image / detection / VSLAM baseline is repeatable; G5 checklist in `CURSOR_PROJECT_GUIDE.md` §M5 is evidenced. Do not claim G5 without that run.

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
- **Files:** new docs under `docs/` per `CURSOR_PROJECT_GUIDE.md` M6
- **Done when:** problem, gap, architecture, RQs, metrics, baselines written. No Cosmos.

### Schema / agent / registry (M7+)

- **Purpose:** Actual product contributions; empty dirs today (`agent/`, `registry/`, `templates/`, `validator/`).
- **Files:** those trees; Pydantic schemas; SQLite first
- **Done when:** one hardware→capability record can drive a template expand. Not before M5/M6 unless the user reorders.
