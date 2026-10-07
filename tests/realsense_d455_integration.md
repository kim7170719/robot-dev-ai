# RealSense D455 Integration Tests

## Prerequisites

- Ubuntu host with an Intel RealSense D455 connected by USB 3.
- ROS 2 Jazzy is installed at `/opt/ros/jazzy`.
- `ros-jazzy-realsense2-camera` is installed.
- The current user has read/write access to the D455 V4L2 devices.
- Isaac Sim remains on `/camera/image_raw`; this integration uses the separate
  `/webcam` namespace.

## Test 1: Discover the RealSense driver

**Steps:**

1. Source ROS Jazzy.
2. Run `ros2 pkg executables realsense2_camera`.

**Expectations:**

1. The command exits with status 0.
2. Its output includes `realsense2_camera_node`.

## Test 2: Publish an isolated colour stream

**Steps:**

1. Start `realsense2_camera_node` with `camera_name:=webcam`, colour enabled,
   depth disabled, and a 640×480/30 colour profile.
2. Query `/webcam/color/image_raw` and `/webcam/color/camera_info`.

**Expectations:**

1. Each topic has exactly one publisher.
2. The image type is `sensor_msgs/msg/Image`.
3. The camera-info type is `sensor_msgs/msg/CameraInfo`.

## Test 3: Confirm a readable colour frame

**Steps:**

1. Capture one message from `/webcam/color/image_raw` using `ros2 topic echo --once`.

**Expectations:**

1. The command exits with status 0.
2. The output identifies a non-zero image width and height.

## Test 4: Preserve Isaac camera isolation

**Steps:**

1. Query publisher count for `/camera/image_raw`.
2. Query publisher count for `/webcam/color/image_raw`.

**Expectations:**

1. The RealSense driver does not publish to `/camera/image_raw`.
2. The RealSense driver publishes only in the `/webcam` namespace.
