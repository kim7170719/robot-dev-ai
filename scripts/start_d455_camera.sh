#!/usr/bin/env bash
set -euo pipefail

source /opt/ros/jazzy/setup.bash

# Publish colour at the fixed, GUI-authorized topic: /webcam/color/image_raw.
exec ros2 launch realsense2_camera rs_launch.py \
  camera_namespace:=/ \
  camera_name:=webcam \
  enable_depth:=false \
  enable_color:=true
