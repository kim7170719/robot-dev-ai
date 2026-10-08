# MJPEG D455 integration

## Prerequisites

- Start the D455 colour/depth driver in another terminal with the verified
  640×480 / 30 FPS launch arguments.
- Start the local API using `bash scripts/run_m14_demo.sh`.
- Confirm `/webcam/color/image_raw` has an `rgb8` publisher.

## Test 1: bounded MJPEG endpoint

1. Request `GET /api/v1/simulation/stream?source=webcam` with a client that
   reads at least one multipart boundary.
2. Inspect the response content type and first emitted part.

Expected results:

1. HTTP status is 200 and content type is
   `multipart/x-mixed-replace; boundary=frame`.
2. The first part starts with `--frame` and identifies `image/jpeg`.

## Test 2: browser source switching

1. Open the Dashboard and select `RealSense D455 · USB colour`.
2. Inspect `#camera-frame.src` and the live label.
3. Select Isaac Sim again.

Expected results:

1. The D455 selection uses `/api/v1/simulation/stream?source=webcam` and the
   label is `Live · MJPEG`.
2. Returning to Isaac clears the MJPEG image source and restores snapshot
   collection; no ROS topic outside the fixed sources is accepted.
