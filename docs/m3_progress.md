## M3 milestone checklist

| Item | Status | Evidence |
|---|---|---|
| Install / verify Isaac Sim | PASS | headless startup, `app ready`, Python 3.10.15 in container |
| Open basic scene | NOT TESTED | |
| Import URDF | NOT TESTED | |
| Save USD | NOT TESTED | |
| Physics / collision | NOT TESTED | |
| Camera / LiDAR | NOT TESTED | |
| ROS 2 Bridge | PARTIAL — bridge loads (`rclpy loaded`); Humble↔Jazzy DDS cross-version not yet confirmed |
| `/cmd_vel`, `/odom`, `/scan`, `/camera` | NOT TESTED | |

## Known constraints

- ROS2 bridge in Isaac Sim 4.5 uses Humble internally (not Jazzy)
- Jazzy ↔ Humble DDS cross-version communication needs to be verified
- RMW: `rmw_fastrtps_cpp` required; Humble FastDDS 2.x vs Jazzy FastDDS 3.x
