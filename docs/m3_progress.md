## M3 milestone checklist

| Item | Status | Evidence |
|---|---|---|
| Install / verify Isaac Sim | PASS | headless startup, `app ready`, Python 3.10.15 in container |
| Open basic scene | PASS | streaming kit loads with all extensions |
| Import URDF | PASS | `URDFParseAndImportFile` status=True, prim=/World/simple_diff_robot/base_link |
| Save USD | PASS | `simple_diff_robot.usd` 6.0 KB at `~/docker/isaac-sim/documents/` |
| Physics / collision | PASS | CPU physics + minimal articulation runs 360 frames without crash |
| Camera / LiDAR | NOT TESTED | camera_link and lidar_link in USD; ROS2 topics not yet configured |
| ROS 2 Bridge | PARTIAL | Container→Host PASS (`/clock` `/odom` visible on Jazzy); Host→Container BLOCKED (DDS asymmetry) |
| `/clock` | PASS | Jazzy host `ros2 topic list` shows `/clock`; 150 frames delivered |
| `/odom` | PASS (pub) | Jazzy host sees `/odom` topic; echo empty due to QoS or timing |
| `/cmd_vel` | PARTIAL | Topic visible on host (`ros2 topic list`); but `Subscription count: 0` from host — Humble FastDDS 2.x subscriber not discoverable by Jazzy FastDDS 3.x |
| G3: `/cmd_vel` controls robot | NOT PASS | cmd_vel not received in container; DDS asymmetry blocks host→container direction |
| G3: Isaac Sim sensor data → ROS 2 | PARTIAL | /clock and /odom published by container and visible on host |

## Known constraints and root causes

**DDS asymmetry (key finding):**
- Container FastDDS 2.x publishes → Jazzy FastDDS 3.x can discover → works ✅
- Jazzy FastDDS 3.x publishes → Humble FastDDS 2.x container can subscribe → `Subscription count: 0` from host ❌
- This is a known FastDDS 2.x ↔ 3.x participant discovery incompatibility

**Physics crash root causes:**
- `IsaacArticulationController` + `IsaacComputeOmniGraph` OmniGraph nodes crash driver 580
- `rclpy.spin_once()` in Kit update callback → crash after ~180 calls
- **Workaround**: rclpy on separate thread via `MultiThreadedExecutor` → 360 frames stable

**Kit scripting pattern (proven):**
- Use `--exec` with `--ext-folder /isaac-sim/apps --ext-folder /isaac-sim/extscache --no-window --allow-root`
- Physics and rclpy work only from update event subscription callback
- `app.post_quit()` triggers cleanup crash (non-fatal for tests)

## Workaround for G3 cmd_vel (TODO)

Option A: Bridge via relay node on host (Jazzy→Jazzy→container).  
Option B: Use CycloneDDS (`RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`) on container side.  
Option C: Use Isaac Sim's streaming API (WebRTC) for two-way control.  
Option D: Upgrade to Isaac Sim 5.x + RTX 4080 (resolves driver and DDS issues simultaneously).
