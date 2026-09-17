# M2: simple_diff_robot

Not Isaac Sim (M3). Not Cosmos. Ubuntu only.

## Apt (Jazzy)

This machine did not have ros2_control installed when the package was added. On Ubuntu:

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-xacro \
  ros-jazzy-controller-manager
```

## Build / launch

```bash
source /opt/ros/jazzy/setup.bash
cd ~/dev/robot-dev-ai/ros_ws
colcon build --packages-select simple_diff_robot
source install/setup.bash
ros2 launch simple_diff_robot robot.launch.py
```

RViz (G2 display):

```bash
ros2 launch simple_diff_robot robot.launch.py use_rviz:=true
```

## Drive

```bash
source /opt/ros/jazzy/setup.bash
source ~/dev/robot-dev-ai/ros_ws/install/setup.bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.0}}" -r 10
ros2 topic echo /odom --once
ros2 topic echo /tf --once
```

Expect `/cmd_vel` and `/odom`. Mock hardware integrates wheel velocity so odom.pose should change.

Gate G2 is PASS only after RViz shows the robot/TF and a `/cmd_vel` command changes odom / chassis motion.
