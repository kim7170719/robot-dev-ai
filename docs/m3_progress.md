## M3 milestone checklist

| Item | Status | Evidence |
|---|---|---|
| Install / verify Isaac Sim | PASS | headless startup, `app ready`, Python 3.10.15 in container |
| Open basic scene | PASS | streaming kit loads with all extensions |
| Import URDF | PASS | `URDFParseAndImportFile` status=True, prim=/World/simple_diff_robot/base_link |
| Save USD | PASS | `simple_diff_robot.usd` 6.0 KB at `~/docker/isaac-sim/documents/` |
| Physics / collision | in progress | USD created; physics scene not yet configured |
| Camera / LiDAR | NOT TESTED | |
| ROS 2 Bridge | PARTIAL — bridge loads (`rclpy loaded`); Humble↔Jazzy DDS not yet confirmed |
| `/cmd_vel`, `/odom`, `/scan`, `/camera` | NOT TESTED | |

## Known constraints

- ROS2 bridge in Isaac Sim 4.5 uses Humble internally (not Jazzy)
- Jazzy ↔ Humble DDS cross-version communication needs to be verified
- RMW: `rmw_fastrtps_cpp` required; Humble FastDDS 2.x vs Jazzy FastDDS 3.x
