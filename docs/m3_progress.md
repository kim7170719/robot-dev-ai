## M3 milestone checklist

| Item | Status | Evidence |
|---|---|---|
| Install / verify Isaac Sim | PASS | headless startup, `app ready`, Python 3.10.15 in container |
| Open basic scene | PASS | streaming kit loads with all extensions |
| Import URDF | PASS | `URDFParseAndImportFile` status=True, prim=/World/simple_diff_robot/base_link |
| Save USD | PASS | `simple_diff_robot.usd` 6.0 KB at `~/docker/isaac-sim/documents/` |
| Physics / collision | PASS | CPU physics + minimal articulation runs 360 frames without crash |
| Camera / LiDAR | NOT TESTED | camera_link and lidar_link in USD; ROS2 topics not yet configured |
| ROS 2 Bridge | PASS | CycloneDDS unicast peer `127.0.0.1`; Humble↔Jazzy bidirectional |
| `/clock` | PASS | Jazzy host `ros2 topic list` shows `/clock` |
| `/odom` | PASS | odom.x increments: 0 → 0.38 → 0.67 → ... while commanding vx=0.3 |
| `/cmd_vel` | PASS | `Subscription count: 1`; `vx=0.30` received in container continuously |
| G3: `/cmd_vel` controls robot | PASS | cmd_vel received + odom.x moving |
| G3: Isaac Sim sensor data → ROS 2 | PASS | `/clock` and `/odom` published and visible on Jazzy host |

## Known constraints and solutions

**DDS solution (key finding):**
- FastDDS 2.x (Humble in container) ↔ FastDDS 3.x (Jazzy host): asymmetric, does NOT work
- **CycloneDDS 0.10.4 (container) ↔ 0.10.5 (Jazzy host): WORKS** with unicast peer config
- Required: `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` AND `CYCLONEDDS_URI=<CycloneDDS><Domain><Discovery><Peers><Peer Address='127.0.0.1'/></Peers></Discovery></Domain></CycloneDDS>` on BOTH sides

**Host setup:**
```bash
source /opt/ros/jazzy/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI="<CycloneDDS><Domain><Discovery><Peers><Peer Address='127.0.0.1'/></Peers></Discovery></Domain></CycloneDDS>"
```

**Container setup:**
```
-e "RMW_IMPLEMENTATION=rmw_cyclonedds_cpp"
-e "LD_LIBRARY_PATH=/isaac-sim/exts/isaacsim.ros2.bridge/humble/lib"
-e "CYCLONEDDS_URI=<CycloneDDS><Domain><Discovery><Peers><Peer Address='127.0.0.1'/></Peers></Discovery></Domain></CycloneDDS>"
```
