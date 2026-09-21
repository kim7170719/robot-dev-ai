# M4: Nav2 on ROS 2 Jazzy

Gate G4: Isaac Sim navigation goal → robot arrives, obstacle avoidance.

Not M5 (Isaac ROS). Not Cosmos.

## Step 1: Install Nav2 + SLAM (needs sudo)

```bash
sudo apt install -y \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox
```

Verify:

```bash
source /opt/ros/jazzy/setup.bash
ros2 pkg list | grep -E 'nav2_bringup|slam_toolbox'
```

## Step 2: Workspace Nav2 package

M4 adds `simple_diff_nav` to `ros_ws/src/`:
- Custom Nav2 param YAML for `simple_diff_robot`
- SLAM Toolbox config
- Launch file: SLAM + Nav2 + RViz

## Step 3: Run SLAM + Nav2 (without Isaac Sim first)

```bash
source /opt/ros/jazzy/setup.bash
cd ~/dev/robot-dev-ai/ros_ws
colcon build --packages-select simple_diff_robot simple_diff_nav
source install/setup.bash

# Terminal 1: SLAM
ros2 launch simple_diff_nav slam_launch.py

# Terminal 2: Nav2
ros2 launch simple_diff_nav nav2_launch.py

# Terminal 3: RViz
export __GL_THREADED_OPTIMIZATIONS=0
ros2 launch nav2_bringup rviz_launch.py
```

## Step 4: Connect Isaac Sim (G4)

Isaac Sim must provide:
- `/scan` (LiDAR scan, `sensor_msgs/LaserScan`)
- `/odom` (odometry)
- TF: `odom` → `base_link`

Isaac Sim subscribes to:
- `/cmd_vel` (Nav2 velocity commands)

Use CycloneDDS on both sides (confirmed working in G3).

## Gate G4 acceptance

- [ ] `slam_toolbox` builds a map while robot navigates
- [ ] Nav2 sends `/cmd_vel` to move robot
- [ ] RViz shows robot, costmap, planned path
- [ ] Navigate-to-pose goal reached in Isaac Sim
- [ ] Obstacle avoidance active
