# E2 sandbox build image

This image is a prerequisite for the future E2 sandbox-build gate. It is not
downloaded, built, or started by the API.

An operator who has reviewed the Dockerfile may provision it explicitly:

```bash
docker build --file docker/Dockerfile.sandbox-ros-jazzy-build \
  --tag robot-dev-ai/ros-jazzy-build:0.1 .
```

Then expose only that already-local image to the API process:

```bash
export ROBOT_DEV_AI_SANDBOX_BUILD_IMAGE=robot-dev-ai/ros-jazzy-build:0.1
```

`GET /api/v1/registry/sandbox/build-readiness` must report `available` before
any future sandbox build is considered. That check never pulls an image or
starts a container. Building the image may pull `ros:jazzy-ros-base`, so it is
an explicit operator action and must be recorded separately from candidate
source evidence.

This image definition does not authorize acquisition, build, promotion, or
installation of any third-party source archive.
