#!/usr/bin/env bash
set -euo pipefail

readonly IMAGE='robot-dev-ai/isaac-ros-image-proc:4.5'
readonly WORKSPACE='/home/yu/workspaces/isaac_ros-dev'
readonly ASSET_DIR="${WORKSPACE}/isaac_ros_assets/isaac_ros_image_proc/quickstart"
readonly ASSET_URL='https://api.ngc.nvidia.com/v2/resources/nvidia/isaac/isaac_ros_image_proc_assets/versions/4.0.0/files/quickstart.tar.gz'

if ! docker image inspect "${IMAGE}" >/dev/null; then
  echo "Missing image: ${IMAGE}. Build it from docker/Dockerfile.isaac-ros-image-proc." >&2
  exit 1
fi

mkdir -p "${WORKSPACE}/isaac_ros_assets"

if [[ ! -f "${ASSET_DIR}/quickstart_0.db3" ]]; then
  docker run --rm --gpus all \
    -e ISAAC_ROS_WS=/workspaces/isaac_ros-dev \
    -v "${WORKSPACE}:/workspaces/isaac_ros-dev" \
    "${IMAGE}" bash -lc \
    "curl -fL --retry 3 -o /tmp/quickstart.tar.gz '${ASSET_URL}' &&
     tar -xzf /tmp/quickstart.tar.gz -C \\"\${ISAAC_ROS_WS}/isaac_ros_assets\\""
fi

docker run --rm --gpus all --network host \
  -e ISAAC_ROS_WS=/workspaces/isaac_ros-dev \
  -v "${WORKSPACE}:/workspaces/isaac_ros-dev" \
  "${IMAGE}" bash -lc '
    source /opt/ros/jazzy/setup.bash
    set -euo pipefail
    ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=resize >/tmp/resize-launch.log 2>&1 &
    launch_pid=$!
    sleep 10
    ros2 bag play --loop "$ISAAC_ROS_WS/isaac_ros_assets/isaac_ros_image_proc/quickstart" \
      --remap /hawk_0_left_rgb_image:=/image_raw /hawk_0_left_rgb_camera_info:=/camera_info >/tmp/resize-bag.log 2>&1 &
    bag_pid=$!
    if timeout 25 ros2 topic echo --once /resize/image >/tmp/resize-output.log 2>&1; then
      result=PASS
    else
      result=FAIL
    fi
    kill "$bag_pid" "$launch_pid" 2>/dev/null || true
    wait "$bag_pid" 2>/dev/null || true
    wait "$launch_pid" 2>/dev/null || true
    echo "RESULT=$result"
    sed -n "1,20p" /tmp/resize-output.log
    tail -n 40 /tmp/resize-launch.log
    test "$result" = PASS
  '
