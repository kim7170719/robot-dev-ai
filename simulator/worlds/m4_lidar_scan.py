"""
M4 LiDAR: kinematic robot + synthetic 2D /scan (same room as scan_sim.py).

G3 pattern: rclpy on a thread; timeline.play() from update callback.
Do not call rclpy.spin_once() here. Do not auto-stop; Nav2 needs a live sim.

Room: x=±4 m, y=±3 m, obstacle at (2.0, 1.0) size 0.5×0.5.
Keep raycast in sync with ros_ws/src/simple_diff_nav/scripts/room_scan.py.
"""
import math
import os
import threading
import time as pytime

print("[M4L] Script started", flush=True)

import omni.kit.app
import omni.timeline
import omni.usd
from omni.isaac.core.utils.extensions import enable_extension

app = omni.kit.app.get_app()
enable_extension("isaacsim.ros2.bridge")
for _ in range(3):
    app.update()
print("[M4L] Extensions ready", flush=True)

from pxr import Gf, PhysxSchema, UsdGeom, UsdPhysics

stage = omni.usd.get_context().get_stage()
scene = UsdPhysics.Scene.Define(stage, "/physicsScene")
scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0, 0, -1))
scene.CreateGravityMagnitudeAttr().Set(9.81)
physx = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/physicsScene"))
physx.CreateEnableGPUDynamicsAttr(False)


def _wall(path, x, y, sx, sy):
    p = UsdGeom.Cube.Define(stage, path)
    xf = UsdGeom.Xformable(p)
    xf.AddTranslateOp().Set(Gf.Vec3d(x, y, 0.5))
    xf.AddScaleOp().Set(Gf.Vec3f(sx, sy, 1.0))
    UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath(path))


_wall("/world/wall_e", 4.1, 0.0, 0.1, 3.1)
_wall("/world/wall_w", -4.1, 0.0, 0.1, 3.1)
_wall("/world/wall_n", 0.0, 3.1, 4.1, 0.1)
_wall("/world/wall_s", 0.0, -3.1, 4.1, 0.1)
obs = UsdGeom.Cube.Define(stage, "/world/obstacle")
UsdGeom.Xformable(obs).AddTranslateOp().Set(Gf.Vec3d(2.0, 1.0, 0.25))
UsdGeom.Xformable(obs).AddScaleOp().Set(Gf.Vec3f(0.25, 0.25, 0.25))
UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath("/world/obstacle"))

base = UsdGeom.Cube.Define(stage, "/robot/base_link")
UsdGeom.Xformable(base).AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.15))
UsdPhysics.RigidBodyAPI.Apply(stage.GetPrimAtPath("/robot/base_link"))
UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath("/robot/base_link"))
print("[M4L] Room + robot created", flush=True)

ROOM_X = 4.0
ROOM_Y = 3.0
OBS = (2.0, 1.0, 0.5, 0.5)
RANGE_MIN = 0.05
RANGE_MAX = 8.0
N_RAYS = 360
DT = 0.016


def _ray_walls(px, py, dx, dy):
    hit = RANGE_MAX
    if dx > 1e-12:
        t = (ROOM_X - px) / dx
        y = py + t * dy
        if t > 1e-6 and -ROOM_Y <= y <= ROOM_Y:
            hit = min(hit, t)
    if dx < -1e-12:
        t = (-ROOM_X - px) / dx
        y = py + t * dy
        if t > 1e-6 and -ROOM_Y <= y <= ROOM_Y:
            hit = min(hit, t)
    if dy > 1e-12:
        t = (ROOM_Y - py) / dy
        x = px + t * dx
        if t > 1e-6 and -ROOM_X <= x <= ROOM_X:
            hit = min(hit, t)
    if dy < -1e-12:
        t = (-ROOM_Y - py) / dy
        x = px + t * dx
        if t > 1e-6 and -ROOM_X <= x <= ROOM_X:
            hit = min(hit, t)
    return hit


def _ray_aabb(px, py, dx, dy, xmin, xmax, ymin, ymax):
    tmin = 0.0
    tmax = RANGE_MAX
    for origin, direction, lo, hi in (
        (px, dx, xmin, xmax),
        (py, dy, ymin, ymax),
    ):
        if abs(direction) < 1e-12:
            if origin < lo or origin > hi:
                return None
            continue
        t1 = (lo - origin) / direction
        t2 = (hi - origin) / direction
        tmin = max(tmin, min(t1, t2))
        tmax = min(tmax, max(t1, t2))
        if tmin > tmax:
            return None
    if tmax < 0.0:
        return None
    t = tmin if tmin > 1e-6 else tmax
    if t <= 1e-6 or t > RANGE_MAX:
        return None
    return t


def ranges_from_pose(x, y, yaw):
    cx, cy, w, h = OBS
    xmin, xmax = cx - w / 2.0, cx + w / 2.0
    ymin, ymax = cy - h / 2.0, cy + h / 2.0
    out = []
    for i in range(N_RAYS):
        angle = -math.pi + (2.0 * math.pi * i) / N_RAYS
        world = yaw + angle
        dx = math.cos(world)
        dy = math.sin(world)
        hit = _ray_walls(x, y, dx, dy)
        box = _ray_aabb(x, y, dx, dy, xmin, xmax, ymin, ymax)
        if box is not None:
            hit = min(hit, box)
        if hit < RANGE_MIN:
            hit = RANGE_MIN
        if hit >= RANGE_MAX:
            hit = RANGE_MAX
        out.append(hit)
    return out


import rclpy
from builtin_interfaces.msg import Time
from geometry_msgs.msg import Quaternion, Twist
from nav_msgs.msg import Odometry
from rclpy.executors import MultiThreadedExecutor
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import CameraInfo, Image

rclpy.init()
node = rclpy.create_node("m4_lidar")
clock_pub = node.create_publisher(Clock, "clock", 10)
odom_pub = node.create_publisher(Odometry, "odom", 10)
scan_pub = node.create_publisher(LaserScan, "scan", 10)
camera_pub = node.create_publisher(Image, "camera/image_raw", 10)
camera_info_pub = node.create_publisher(CameraInfo, "camera/camera_info", 10)

cmd = [0.0, 0.0]
cmd_stamp = [0.0]


def on_cmd(msg):
    cmd[0] = msg.linear.x
    cmd[1] = msg.angular.z
    cmd_stamp[0] = pytime.time()


node.create_subscription(Twist, "cmd_vel", on_cmd, 10)
executor = MultiThreadedExecutor()
executor.add_node(node)
threading.Thread(target=executor.spin, daemon=True).start()
print("[M4L] rclpy thread. Topics: /clock /odom /scan /cmd_vel", flush=True)
print("[M4L] Camera topics: /camera/image_raw /camera/camera_info", flush=True)

state = {"frame": 0, "x": 0.0, "y": 0.0, "yaw": 0.0, "sim_t": 0.0}


def _quat(yaw):
    q = Quaternion()
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


def on_update(_e):
    state["frame"] += 1
    n = state["frame"]
    if n == 10:
        omni.timeline.get_timeline_interface().play()
        print("[M4L] PHYSICS PLAYING. Host: /clock /odom /scan  Sub: /cmd_vel", flush=True)

    if n < 10:
        return

    vx, wz = cmd
    if pytime.time() - cmd_stamp[0] > 0.5:
        vx, wz = 0.0, 0.0
        cmd[0], cmd[1] = 0.0, 0.0
    state["x"] += vx * math.cos(state["yaw"]) * DT
    state["y"] += vx * math.sin(state["yaw"]) * DT
    state["yaw"] += wz * DT
    state["sim_t"] += DT
    now = pytime.time()
    t = int(now)
    ns = int((now - t) * 1e9)
    stamp = Time(sec=t, nanosec=ns)

    c = Clock()
    c.clock = stamp
    clock_pub.publish(c)

    od = Odometry()
    od.header.stamp = stamp
    od.header.frame_id = "odom"
    od.child_frame_id = "base_link"
    od.pose.pose.position.x = state["x"]
    od.pose.pose.position.y = state["y"]
    od.pose.pose.position.z = 0.15
    od.pose.pose.orientation = _quat(state["yaw"])
    od.twist.twist.linear.x = vx
    od.twist.twist.angular.z = wz
    odom_pub.publish(od)

    xf = UsdGeom.Xformable(stage.GetPrimAtPath("/robot/base_link"))
    ops = xf.GetOrderedXformOps()
    if ops:
        ops[0].Set(Gf.Vec3d(state["x"], state["y"], 0.15))

    if n % 6 == 0:
        scan = LaserScan()
        scan.header.stamp = stamp
        scan.header.frame_id = "lidar_link"
        scan.angle_min = -math.pi
        scan.angle_max = math.pi - (2.0 * math.pi / N_RAYS)
        scan.angle_increment = 2.0 * math.pi / N_RAYS
        scan.scan_time = 0.1
        scan.range_min = RANGE_MIN
        scan.range_max = RANGE_MAX
        scan.ranges = ranges_from_pose(state["x"], state["y"], state["yaw"])
        scan_pub.publish(scan)

        image = Image()
        image.header.stamp = stamp
        image.header.frame_id = "camera_link"
        image.height = 48
        image.width = 64
        image.encoding = "rgb8"
        image.is_bigendian = 0
        image.step = image.width * 3
        red = int(max(0.0, min(255.0, (state["x"] + 4.0) * 31.0)))
        green = int(max(0.0, min(255.0, (state["y"] + 3.0) * 42.0)))
        image.data = bytes([red, green, 96]) * (image.width * image.height)
        camera_pub.publish(image)

        camera_info = CameraInfo()
        camera_info.header = image.header
        camera_info.height = image.height
        camera_info.width = image.width
        camera_info.distortion_model = "plumb_bob"
        camera_info.k = [48.0, 0.0, 32.0, 0.0, 48.0, 24.0, 0.0, 0.0, 1.0]
        camera_info.p = [48.0, 0.0, 32.0, 0.0, 0.0, 48.0, 24.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        camera_info_pub.publish(camera_info)

    if n % 60 == 0:
        print(
            f"[M4L] frame={n} x={state['x']:.3f} y={state['y']:.3f} yaw={state['yaw']:.2f} cmd=({vx:.2f},{wz:.2f})",
            flush=True,
        )


# Keep the subscription alive after --exec returns (otherwise GC drops the callback).
UPDATE_SUB = app.get_update_event_stream().create_subscription_to_pop(on_update, name="m4l")
print("[M4L] Subscription registered.", flush=True)
