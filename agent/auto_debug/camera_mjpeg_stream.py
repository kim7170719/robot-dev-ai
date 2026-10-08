#!/usr/bin/env python3
"""Read an authorized ROS RGB topic and emit a multipart MJPEG response."""

from __future__ import annotations

import argparse
import sys

import cv2
import numpy
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class MjpegNode(Node):
    def __init__(self, image_topic: str) -> None:
        super().__init__("robot_dev_ai_mjpeg_stream")
        self.create_subscription(Image, image_topic, self._on_image, 10)

    def _on_image(self, message: Image) -> None:
        encoding = message.encoding.lower()
        if encoding not in {"rgb8", "bgr8"} or message.step < message.width * 3:
            return
        image = numpy.ndarray(
            shape=(message.height, message.width, 3),
            dtype=numpy.uint8,
            buffer=message.data,
            strides=(message.step, 3, 1),
        )
        bgr = image if encoding == "bgr8" else cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        success, encoded = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, 82])
        if not success:
            return
        frame = encoded.tobytes()
        sys.stdout.buffer.write(
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n"
            + f"Content-Length: {len(frame)}\r\n\r\n".encode()
            + frame
            + b"\r\n"
        )
        sys.stdout.buffer.flush()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image_topic")
    arguments = parser.parse_args()
    rclpy.init()
    node = MjpegNode(arguments.image_topic)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
