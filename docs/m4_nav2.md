# M4: Nav2 on ROS 2 Jazzy

Gate G4: Isaac Sim navigation goal → robot arrives, obstacle avoidance.

Not M5 (Isaac ROS). Not Cosmos.

Synthetic `/scan` (not RTX LiDAR): `docs/decisions/0004-synthetic-2d-lidar.md`.

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
- `scan_sim.py`: synthetic `/scan` from `/odom` (8×6 m room + one box)
- Launch: SLAM + robot (or Isaac Sim) + Nav2

## Step 3: SLAM + Nav2 on the host (no Isaac Sim)

This unblocks the previous failure: global costmap waiting for `base_link → map`.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/dev/robot-dev-ai/ros_ws
colcon build --packages-select simple_diff_robot simple_diff_nav
source install/setup.bash
export ROS_LOCALHOST_ONLY=1
```

Terminal 1:

```bash
ros2 launch simple_diff_nav slam_launch.py
```

Expect `/scan` (`sensor_msgs/LaserScan`, `frame_id=lidar_link`) and after driving, TF `map → odom`.

Drive (Jazzy uses `TwistStamped`):

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/TwistStamped \
  "{header: {stamp: {sec: 0}}, twist: {linear: {x: 0.15}, angular: {z: 0.2}}}"
```

Wait until this prints a transform (not “frame does not exist”). If Nav2 was started earlier, Ctrl+C that launch and start it again; lifecycle_manager does not retry.

```bash
ros2 run tf2_ros tf2_echo map odom
```

Terminal 2:

```bash
ros2 launch simple_diff_nav nav2_launch.py
```

Check:

```bash
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /bt_navigator
# expect: active [3]
```

RViz:

```bash
export __GL_THREADED_OPTIMIZATIONS=0
ros2 launch nav2_bringup rviz_launch.py
```

Fixed Frame: `map`. Add LaserScan `/scan`, Map `/map`.

## Step 4: Isaac Sim `/scan` (G4 prep)

Isaac Sim must provide `/scan`, `/odom`, `/clock` and subscribe to `/cmd_vel` as **`geometry_msgs/Twist`** (Nav2 Jazzy; not TwistStamped). Host publishes TF `odom → base_link` via `odom_to_tf`. CycloneDDS on both sides (G3). Stamps are **wall clock** so host nodes use `use_sim_time:=false`.

Host (keep Isaac Sim running first):

```bash
source /opt/ros/jazzy/setup.bash
source ~/dev/robot-dev-ai/ros_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI="<CycloneDDS><Domain><Discovery><Peers><Peer Address='127.0.0.1'/></Peers></Discovery></Domain></CycloneDDS>"
unset ROS_LOCALHOST_ONLY

ros2 launch simple_diff_nav slam_launch.py use_isaac_sim:=true use_sim_time:=false
# wait until: ros2 run tf2_ros tf2_echo map odom
ros2 launch simple_diff_nav nav2_launch.py use_sim_time:=false
```

Container — **`--entrypoint /isaac-sim/kit/kit`** is required or `--exec` never runs:

```bash
env -i HOME=$HOME USER=$USER PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
docker run --name isaac-m4-g4 --rm --gpus all --network=host \
  -e "ACCEPT_EULA=Y" -e "PRIVACY_CONSENT=Y" \
  -e "PYTHONUNBUFFERED=1" \
  -e "OMNI_KIT_ALLOW_ROOT=1" \
  -e "RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" \
  -e "LD_LIBRARY_PATH=/isaac-sim/exts/isaacsim.ros2.bridge/humble/lib" \
  -e "CYCLONEDDS_URI=<CycloneDDS><Domain><Discovery><Peers><Peer Address='127.0.0.1'/></Peers></Discovery></Domain></CycloneDDS>" \
  -v ~/docker/isaac-sim/cache/kit:/isaac-sim/kit/cache:rw \
  -v ~/docker/isaac-sim/cache/ov:/root/.cache/ov:rw \
  -v ~/docker/isaac-sim/cache/pip:/root/.cache/pip:rw \
  -v ~/docker/isaac-sim/cache/glcache:/root/.cache/mesa_shader_cache:rw \
  -v ~/docker/isaac-sim/cache/computecache:/root/.nv/ComputeCache:rw \
  -v ~/docker/isaac-sim/logs:/root/.nvidia-omniverse/logs:rw \
  -v ~/docker/isaac-sim/data:/root/.local/share/ov/data:rw \
  -v ~/docker/isaac-sim/documents:/root/Documents:rw \
  -v ~/dev/robot-dev-ai/simulator/worlds:/root/worlds:ro \
  --entrypoint /isaac-sim/kit/kit \
  nvcr.io/nvidia/isaac-sim:4.5.0 \
    /isaac-sim/apps/isaacsim.exp.full.streaming.kit \
    --ext-folder /isaac-sim/apps \
    --ext-folder /isaac-sim/extscache \
    --no-window --allow-root \
    --exec /root/worlds/m4_lidar_scan.py
```

Verify on the host:

```bash
ros2 topic hz /scan
ros2 topic echo /scan --once
```

CLI goal (Jazzy Nav2):

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

## Host bring-up (2026-09-21)

- [x] `slam_toolbox` builds a map (`/map`, TF `map → odom`)
- [x] Nav2 lifecycle `active` (`controller_server`, `planner_server`, `bt_navigator`)
- [x] RViz navigate-to-pose on host (synthetic `/scan` + ros2_control)

## Gate G4 acceptance

- [x] Isaac Sim publishes `/scan` `/odom` `/clock`; host TF `odom → base_link`
- [x] `slam_toolbox` builds a map while robot navigates in Isaac Sim
- [x] Nav2 sends `/cmd_vel` (`Twist`) to Isaac Sim
- [x] Host RViz navigate-to-pose (synthetic scan); Isaac Sim goals via CLI
- [x] Navigate-to-pose goal reached in Isaac Sim (`SUCCEEDED`, odom 3.09 → 0.96)
- [x] Obstacle avoidance: goal (2.0, 2.2) around box at (2.0, 1.0) `SUCCEEDED` (odom 1.87, 2.25)

Evidence: `experiments/raw/M4-G4.md`.
