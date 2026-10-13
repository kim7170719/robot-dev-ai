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
the fixed `POST /api/v1/registry/onboarding/{id}/bundle/build` endpoint can be
considered. That check never pulls an image or starts a container. The endpoint
requires the same archive to have passed human authorization, dependency scan,
ROS manifest metadata, and license metadata gates; it runs a fixed no-network
`colcon build` in a disposable tmpfs workspace. Building the image may pull
`ros:jazzy-ros-base`, so it is an explicit operator action and must be recorded
separately from candidate-source evidence.

When the configured tag is available, readiness also records Docker's local
`sha256:` image ID. The isolated build uses that immutable ID rather than the
tag, so a later tag retarget cannot silently change the audited build input.

This image definition does not authorize acquisition, promotion, or
installation of any third-party source archive. A successful isolated build is
an auditable observation, not an automatic E2 record or a compatibility claim.
