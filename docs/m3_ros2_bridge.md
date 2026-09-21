## ROS2 bridge DDS notes

**Confirmed working (2026-09-21):**
- Isaac Sim 4.5 internal Humble `rclpy` publishes to `/clock`
- Jazzy host sees `/clock` via `ros2 topic list` with `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`
- FastDDS 2.x (Humble in container) ↔ FastDDS 3.x (Jazzy host) works on localhost with `--network=host`

**Host side setup:**
```bash
source /opt/ros/jazzy/setup.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
# unset ROS_LOCALHOST_ONLY  (or set it; both worked)
ros2 topic list              # shows /clock while container is running
ros2 topic echo /clock       # may need --qos-reliability best_effort
```

**Container side:**
```
-e "RMW_IMPLEMENTATION=rmw_fastrtps_cpp"
-e "LD_LIBRARY_PATH=/isaac-sim/exts/isaacsim.ros2.bridge/humble/lib"
--network=host
```

**Scripting pattern (via update event subscription):**
```python
from omni.isaac.core.utils.extensions import enable_extension
enable_extension("isaacsim.ros2.bridge")
for _ in range(5): app.update()

import rclpy
rclpy.init()
# create publishers/subscribers here

def on_update(e):
    # called every kit frame
    pub.publish(msg)
    rclpy.spin_once(node, timeout_sec=0.0)

sub = app.get_update_event_stream().create_subscription_to_pop(on_update, name="ros2_bridge")
# do NOT call app.update() in a loop — crashes the streaming kit
```

**Physics crash:**
- `timeline.play()` in `--exec` context crashes the streaming kit (dump file written)
- Do NOT call `app.update()` in a manual loop within `--exec`
- For physics + ROS2 topics (cmd_vel/odom), use the streaming server approach

**Next step for /cmd_vel + /odom:**
- Start streaming server with OmniGraph diff drive configured
- Use WebRTC or Isaac Sim Python extension to set up the articulation
- See `simulator/worlds/import_urdf.py` for URDF import baseline
