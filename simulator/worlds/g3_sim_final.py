"""
M3 G3 FINAL: Physics + ROS2 with rclpy on a separate thread.
Avoids crash from spin_once() in update callback.
"""
import os, threading
print("[G3F] Script started", flush=True)

import omni.kit.app, omni.usd, omni.timeline
from omni.isaac.core.utils.extensions import enable_extension

app = omni.kit.app.get_app()
enable_extension("isaacsim.ros2.bridge")
for _ in range(3):
    app.update()
print("[G3F] Extensions ready", flush=True)

from pxr import UsdPhysics, PhysxSchema, UsdGeom, Gf
stage = omni.usd.get_context().get_stage()

scene = UsdPhysics.Scene.Define(stage, "/physicsScene")
scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0, 0, -1))
scene.CreateGravityMagnitudeAttr().Set(9.81)
physx = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/physicsScene"))
physx.CreateEnableGPUDynamicsAttr(False)

base = UsdGeom.Cube.Define(stage, "/robot/base_link")
UsdGeom.Xformable(base).AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.15))
UsdPhysics.RigidBodyAPI.Apply(stage.GetPrimAtPath("/robot/base_link"))
UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath("/robot/base_link"))
print("[G3F] Robot created", flush=True)

# === ROS2 on separate thread ===
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped
from builtin_interfaces.msg import Time
from rosgraph_msgs.msg import Clock

rclpy.init()
node = rclpy.create_node('g3_final')

clock_pub = node.create_publisher(Clock, 'clock', 10)
odom_pub  = node.create_publisher(Odometry, 'odom', 10)

cmd_received = [None]
def on_cmd(msg):
    vx = msg.twist.linear.x if hasattr(msg, 'twist') else msg.linear.x
    wz = msg.twist.angular.z if hasattr(msg, 'twist') else msg.angular.z
    cmd_received[0] = (vx, wz)
    print(f"[G3F] /cmd_vel received: vx={vx:.2f} wz={wz:.2f}", flush=True)

node.create_subscription(TwistStamped, 'cmd_vel', on_cmd, 10)

# Run executor in daemon thread
executor = MultiThreadedExecutor()
executor.add_node(node)
ros_thread = threading.Thread(target=executor.spin, daemon=True)
ros_thread.start()
print("[G3F] rclpy executor on thread. Topics: /clock /odom /cmd_vel", flush=True)

state = {'frame': 0, 'x': 0.0, 'vx': 0.0, 'sim_t': 0.0}

def on_update(e):
    state['frame'] += 1
    n = state['frame']

    if n == 10:
        print("[G3F] Starting physics...", flush=True)
        omni.timeline.get_timeline_interface().play()
        print("[G3F] PHYSICS PLAYING. Topics on host: /clock /cmd_vel /odom", flush=True)
        print("[G3F] Send: ros2 topic pub -r 20 /cmd_vel geometry_msgs/msg/TwistStamped '{twist:{linear:{x:0.3}}}'", flush=True)

    if n >= 10:
        if cmd_received[0]:
            state['vx'] = cmd_received[0][0]
        state['x']     += state['vx'] * 0.016
        state['sim_t'] += 0.016

        t  = int(state['sim_t'])
        ns = int((state['sim_t'] - t) * 1e9)

        c = Clock()
        c.clock = Time(sec=t, nanosec=ns)
        clock_pub.publish(c)

        od = Odometry()
        od.header.stamp = Time(sec=t, nanosec=ns)
        od.header.frame_id = 'odom'
        od.child_frame_id  = 'base_link'
        od.pose.pose.position.x    = state['x']
        od.twist.twist.linear.x    = state['vx']
        odom_pub.publish(od)

    if n % 60 == 0 and n >= 10:
        print(f"[G3F] frame={n} odom.x={state['x']:.4f} vx={state['vx']:.2f}", flush=True)

    if n == 360:
        omni.timeline.get_timeline_interface().stop()
        print(f"[G3F] FINAL odom.x={state['x']:.4f} cmd={cmd_received[0]}", flush=True)
        print("=== G3F COMPLETE ===", flush=True)
        os.makedirs("/root/Documents", exist_ok=True)
        with open("/root/Documents/m3_status.txt", "w") as f:
            f.write(f"odom_final_x={state['x']:.4f}\ncmd_received={cmd_received[0]}\n=== G3F COMPLETE ===\n")

sub = app.get_update_event_stream().create_subscription_to_pop(on_update, name="g3f")
print("[G3F] Subscription registered. Waiting for physics...", flush=True)
