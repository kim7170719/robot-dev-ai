# M1 pipeline

`sensor_node` publishes `/range`. `planner_node` uses parameter `stop_distance` and publishes `/cmd_vel`. `controller_node` broadcasts TF `odom` → `base_link`.

Not M2. Not Cosmos. RViz2 is optional GUI.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/dev/robot-dev-ai/ros_ws
colcon build --packages-select m1_baseline
source install/setup.bash
ros2 launch m1_baseline m1_pipeline.launch.py
```

Second terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/dev/robot-dev-ai/ros_ws/install/setup.bash
ros2 node list
ros2 param get /planner_node stop_distance
ros2 topic echo /cmd_vel --once
ros2 run tf2_ros tf2_echo odom base_link
```
