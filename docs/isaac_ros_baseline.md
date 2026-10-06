# Isaac ROS 4.5 image-pipeline baseline runbook

## Purpose and scope

This runbook reproduces M5's NVIDIA-accelerated image resize baseline on the Ubuntu host. It builds a project-owned Isaac ROS 4.5 image, starts the official resize graph, plays NVIDIA's quickstart rosbag, and verifies that /resize/image publishes an image.

This is an experimental baseline only. The host is an RTX 2080 Ti (Turing, compute capability 7.5); Isaac ROS 4.5 officially supports x86_64 GPUs with Ampere architecture or newer. Do not treat a pass here as vendor support.

## Prerequisites

- Ubuntu 24.04 with Docker and NVIDIA Container Toolkit working.
- NVIDIA driver 580.178.04 or newer and at least 8 GB VRAM.
- Repository checkout at /home/yu/dev/robot-dev-ai.
- At least 32 GB free disk for the Isaac ROS image and NGC assets.
- An Isaac ROS workspace outside the repository, defaulting to /home/yu/workspaces/isaac_ros-dev.

## Procedure

Build the image:

~~~bash
cd /home/yu/dev/robot-dev-ai
docker build --file docker/Dockerfile.isaac-ros-image-proc \
  --tag robot-dev-ai/isaac-ros-image-proc:4.5 docker
~~~

Run the smoke test:

~~~bash
cd /home/yu/dev/robot-dev-ai
scripts/m5_image_proc_smoke.sh
~~~

The script downloads NVIDIA's latest compatible major-4 quickstart asset when it is absent. At the time this baseline was recorded, that asset was NGC version 4.0.0.

## Verification

The script exits zero only when all of the following are true:

1. The container can access the NVIDIA GPU.
2. isaac_ros_examples starts the ResizeNode.
3. The rosbag publishes its remapped image stream.
4. ros2 topic echo --once /resize/image receives an image.

Recorded successful output on 2026-10-01:

~~~text
RESULT=PASS
width: 480
height: 288
encoding: rgb8
~~~

## Troubleshooting

- Package not found: rebuild the Docker image; the base Isaac ROS image alone does not include isaac_ros_image_proc.
- No /resize/image: inspect the script's launch and rosbag logs, then confirm the asset directory contains quickstart_0.db3.
- no kernel image or CUDA architecture errors: stop. The RTX 2080 Ti is outside the supported Isaac ROS 4.5 architecture matrix.
- Disk exhaustion while building: the binary package dependency set adds about 10 GB and the final image is about 17.7 GB; free Docker space before retrying.

## Cleanup

The quickstart asset is deliberately retained at /home/yu/workspaces/isaac_ros-dev/isaac_ros_assets so subsequent smoke tests do not download it again.

To remove only the locally built M5 image after testing:

~~~bash
docker image rm robot-dev-ai/isaac-ros-image-proc:4.5
~~~

Do not remove shared Isaac Sim images or Docker caches unless that cleanup is separately intended.

## References

- docs/decisions/0005-isaac-ros-container-baseline.md
- https://nvidia-isaac-ros.github.io/v/release-4.5/repositories_and_packages/isaac_ros_image_pipeline/isaac_ros_image_proc/index.html
- https://nvidia-isaac-ros.github.io/v/release-4.5/repositories_and_packages/isaac_ros_image_pipeline/index.html
