# 0005: Isaac ROS 4.5 Docker image-pipeline baseline

Date: 2026-10-01

## Decision

Use a project-owned Docker image based on the official Isaac ROS 4.5 base image, with the release-4.5 Debian packages ros-jazzy-isaac-ros-image-proc and ros-jazzy-isaac-ros-examples.

The first M5 acceptance path is the official resize pipeline: NGC quickstart rosbag → ResizeNode → /resize/image. The image is defined by docker/Dockerfile.isaac-ros-image-proc and exercised by scripts/m5_image_proc_smoke.sh.

## Reasoning

- Docker keeps CUDA, Isaac ROS, and ROS package dependencies isolated from the Ubuntu 24.04/Jazzy host.
- The binary packages match the project's fixed Isaac ROS 4.5 and ROS 2 Jazzy stack, avoiding a source build for the first accelerated baseline.
- The official quickstart provides a reproducible input stream and a concrete output topic.
- The host RTX 2080 Ti has sufficient VRAM and driver 580.178.04 for this experiment, but is Turing (compute capability 7.5). NVIDIA's 4.5 x86_64 support matrix requires Ampere or newer, so this decision does not claim official support.

## Impact

- The baseline image is large (about 17.7 GB) because upstream CUDA development dependencies are pulled by the binary packages.
- The image-pipeline baseline is reproducible with the documented Dockerfile and smoke-test script.
- This establishes only one M5 pipeline. Object detection and Visual SLAM remain future M5 work, not Gate G5 requirements.
- Failures on this GPU must be treated as unsupported-platform observations; do not generalize them to supported Ampere-or-newer systems.

## References

- docs/isaac_ros_baseline.md
- https://nvidia-isaac-ros.github.io/v/release-4.5/getting_started/index.html
- https://nvidia-isaac-ros.github.io/v/release-4.5/repositories_and_packages/isaac_ros_image_pipeline/index.html
