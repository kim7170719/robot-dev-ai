## M3 milestone checklist

| Item | Status | Evidence |
|---|---|---|
| Install / verify Isaac Sim | PASS | headless startup, `app ready`, Python 3.10.15 in container |
| Open basic scene | PASS | streaming kit loads with all extensions |
| Import URDF | PASS | `URDFParseAndImportFile` status=True, prim=/World/simple_diff_robot/base_link |
| Save USD | PASS | `simple_diff_robot.usd` 6.0 KB at `~/docker/isaac-sim/documents/` |
| Physics / collision | in progress | USD created; physics scene not yet configured |
| Camera / LiDAR | NOT TESTED | |
| ROS 2 Bridge | PASS — `rclpy` in container publishes `/clock`; Jazzy host `ros2 topic list` sees `/clock`; 150 frames delivered |
| `/cmd_vel`, `/odom`, `/scan`, `/camera` | NOT TESTED — need physics scene + diff drive OmniGraph (crash on timeline.play(); workaround needed) |

## Known constraints

- Isaac Sim 4.5 ROS2 bridge uses Humble internally (not Jazzy) — **DDS communication with Jazzy host CONFIRMED**
- `rmw_fastrtps_cpp` on both sides; Humble FastDDS 2.x ↔ Jazzy FastDDS 3.x works via localhost
- Calling `timeline.play()` or `app.update()` loop in `--exec` context crashes physics scene; need to use update event subscription
- Physics + cmd_vel/odom test requires separate approach (running streaming server + OmniGraph diff drive)
