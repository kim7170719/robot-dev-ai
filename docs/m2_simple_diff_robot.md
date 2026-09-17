# M2: simple_diff_robot

Not Isaac Sim (M3). Not Cosmos. Ubuntu only. Do not launch `m1_pipeline` at the same time (`/cmd_vel` type clash).

## Apt (installed 2026-09-17)

- `ros-jazzy-xacro` 2.1.1
- `ros-jazzy-ros2-control` 4.48.0
- `ros-jazzy-ros2-controllers` 4.42.1
- `ros-jazzy-controller-manager` 4.48.0

## Build / launch

```bash
source /opt/ros/jazzy/setup.bash
cd ~/dev/robot-dev-ai/ros_ws
colcon build --packages-select simple_diff_robot
source install/setup.bash
ros2 launch simple_diff_robot robot.launch.py
```

RViz (still needed for full G2):

```bash
ros2 launch simple_diff_robot robot.launch.py use_rviz:=true
```

## Drive (Jazzy uses TwistStamped)

```bash
source /opt/ros/jazzy/setup.bash
source ~/dev/robot-dev-ai/ros_ws/install/setup.bash
ros2 topic pub --qos-reliability best_effort -r 20 /cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.2}}}"
```

Verified 2026-09-17: odom `x` 0.006 → 0.804 and `twist.linear.x` 0.3 while commanding 0.3 m/s. Controllers: `diff_drive_controller` and `joint_state_broadcaster` active.

Gate G2 **RViz** item is still NOT TESTED.
