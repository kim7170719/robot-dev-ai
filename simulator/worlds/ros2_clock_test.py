"""
M3-03c: /clock publisher via Kit update event subscription.
No app.update() loop — Kit drives itself, script just subscribes.
"""
import sys, os, time

print("[M3-03c] Script started", flush=True)

import omni.kit.app
app = omni.kit.app.get_app()
print(f"[M3-03c] App: {app.get_build_version()}", flush=True)

from omni.isaac.core.utils.extensions import enable_extension
enable_extension("isaacsim.ros2.bridge")
for _ in range(5):
    app.update()
print("[M3-03c] bridge enabled", flush=True)

import rclpy
rclpy.init()
node = rclpy.create_node('isaac_clock')
from rosgraph_msgs.msg import Clock
from builtin_interfaces.msg import Time
pub = node.create_publisher(Clock, 'clock', 10)
print("[M3-03c] /clock publisher ready", flush=True)
print("[M3-03c] host: source /opt/ros/jazzy/setup.bash && export RMW_IMPLEMENTATION=rmw_fastrtps_cpp && ros2 topic list", flush=True)

counter = [0]
MAX_FRAMES = 150   # ~15 seconds at 10 Hz

def on_update(e):
    if counter[0] >= MAX_FRAMES:
        return
    msg = Clock()
    msg.clock = Time(sec=counter[0] // 10, nanosec=(counter[0] % 10) * 100_000_000)
    pub.publish(msg)
    rclpy.spin_once(node, timeout_sec=0.0)
    counter[0] += 1
    if counter[0] % 30 == 0:
        print(f"[M3-03c] published {counter[0]} frames", flush=True)
    if counter[0] == MAX_FRAMES:
        print("=== M3-03c COMPLETE ===", flush=True)
        node.destroy_node()
        rclpy.shutdown()
        os.makedirs("/root/Documents", exist_ok=True)
        with open("/root/Documents/m3_status.txt", "w") as f:
            f.write(f"clock_frames={MAX_FRAMES}\n=== M3-03c COMPLETE ===\n")
        app.post_quit()

sub = app.get_update_event_stream().create_subscription_to_pop(on_update, name="m3_clock")
print("[M3-03c] update subscription registered", flush=True)
