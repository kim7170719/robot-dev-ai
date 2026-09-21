## G3 simulation scripts

### Correct kit invocation
```bash
/isaac-sim/kit/kit \
  /isaac-sim/apps/isaacsim.exp.full.streaming.kit \
  --ext-folder /isaac-sim/apps \
  --ext-folder /isaac-sim/extscache \
  --no-window --allow-root \
  --exec /root/script.py
```

### Simulation loop pattern (avoid crash)
```python
# rclpy on separate thread
import threading
rclpy.init()
node = rclpy.create_node('name')
executor = MultiThreadedExecutor()
executor.add_node(node)
threading.Thread(target=executor.spin, daemon=True).start()

# Kit update subscription drives physics
def on_update(e):
    # publish/logic here — do NOT call rclpy.spin_once()
    pass
app.get_update_event_stream().create_subscription_to_pop(on_update, name='sim')
```

### DDS direction confirmed working
- Container → Host: `rmw_fastrtps_cpp`, `/clock` and `/odom` visible on Jazzy
- Host → Container: **BLOCKED** — Humble FastDDS 2.x subscriber not discovered by Jazzy FastDDS 3.x

### G3 status
- G3-a (sensor data → ROS2): PARTIAL PASS (`/clock`, `/odom` pub visible from host)
- G3-b (`/cmd_vel` → robot control): FAIL (DDS asymmetry; Subscription count=0 from host)
