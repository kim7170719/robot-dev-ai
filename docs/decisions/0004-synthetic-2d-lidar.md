# 0004: Synthetic 2D LiDAR for M4 Nav2 bring-up

Date: 2026-09-21

## Decision

Use a **synthetic 2D LaserScan** (Python raycast of a rectangular room) for M4 SLAM/Nav2 bring-up, not Isaac Sim RTX / PhysX LiDAR.

## Reasoning

- Nav2 failed to activate because `slam_toolbox` had no `/scan`, so `map → odom` never appeared.
- Isaac Sim 4.5 RTX LiDAR on RTX 2080 Ti 11 GB, in the same headless `--exec` path that already crashed on URDF physics and `rclpy.spin_once()`, is a high-risk next step.
- SLAM Toolbox and Nav2 costmaps only need a geometrically consistent `sensor_msgs/LaserScan` and TF. A 2D room raycast is enough to prove that chain.
- The same room model runs on the Jazzy host (`scan_sim.py`, no Docker) and inside Isaac Sim (`m4_lidar_scan.py`, G3 kinematic pattern).

## Room model

- Interior: \(x \in [-4, 4]\,\mathrm{m}\), \(y \in [-3, 3]\,\mathrm{m}\)
- Obstacle: 0.5 m box centered at (2.0, 1.0)
- 360 rays, `range_max` 8.0 m, `frame_id` `lidar_link`

Keep `ros_ws/src/simple_diff_nav/scripts/room_scan.py` and `simulator/worlds/m4_lidar_scan.py` in sync.

## Upgrade path

Replace the synthetic publisher with Isaac Sim PhysX or RTX LiDAR on `/scan` when GPU LiDAR is stable. Host `scan_sim` is then unused; `use_isaac_sim:=true` already skips it.

## References

- `docs/m4_nav2.md`
- `docs/decisions/0002-isaac-sim-version-docker.md`
