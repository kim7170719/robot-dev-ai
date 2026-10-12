#!/usr/bin/env bash
source /opt/ros/jazzy/setup.bash
set -eo pipefail

# Publish only the newest colour frame at the fixed GUI-authorized topic.
# Set ROBOT_DEV_AI_D455_RGBD=1 only when a depth stream is also required.
launch_arguments=(
  camera_namespace:=/ \
  camera_name:=webcam \
  enable_color:=true \
  rgb_camera.color_profile:=640x480x30
)

if [[ "${ROBOT_DEV_AI_D455_RGBD:-0}" == "1" ]]; then
  launch_arguments+=(
    enable_depth:=true \
    depth_module.depth_profile:=640x480x30
  )
else
  launch_arguments+=(enable_depth:=false)
fi

ros2 launch realsense2_camera rs_launch.py "${launch_arguments[@]}" &
driver_pid=$!

cleanup() {
  kill "$driver_pid" 2>/dev/null || true
  wait "$driver_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# These are runtime node parameters, not rs_launch.py launch arguments.
# Depth one ensures a slow browser never accumulates old camera frames.
for _ in {1..30}; do
  if ros2 param get /webcam rgb_camera.frames_queue_size >/dev/null 2>&1; then
    for parameter in \
      rgb_camera.frames_queue_size \
      depth_module.frames_queue_size \
      align_depth.frames_queue_size; do
      ros2 param set /webcam "$parameter" 1 >/dev/null
    done
    break
  fi
  sleep 0.2
done

wait "$driver_pid"
