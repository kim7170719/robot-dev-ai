#!/usr/bin/env python3
"""Capture one RGB camera image and one odometry sample as JSON on stdout."""

from __future__ import annotations

import base64
import argparse
import json
import math
import struct
import sys
import time
import zlib

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import Image


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def _rgb8_png(image: Image) -> bytes:
    if image.encoding.lower() != "rgb8":
        raise ValueError(f"unsupported camera encoding: {image.encoding}")
    expected = image.width * image.height * 3
    raw = bytes(image.data)
    if len(raw) < expected or image.step < image.width * 3:
        raise ValueError("invalid rgb8 image dimensions")
    rows = b"".join(
        b"\x00" + raw[index * image.step : index * image.step + image.width * 3]
        for index in range(image.height)
    )
    header = struct.pack(">IIBBBBB", image.width, image.height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", header) + _png_chunk(
        b"IDAT", zlib.compress(rows)
    ) + _png_chunk(b"IEND", b"")


class CaptureNode(Node):
    def __init__(self, image_topic: str) -> None:
        super().__init__("robot_dev_ai_camera_capture")
        self.image: Image | None = None
        self.pose: Odometry | None = None
        self.create_subscription(Image, image_topic, self._on_image, 10)
        self.create_subscription(Odometry, "/odom", self._on_odom, 10)

    def _on_image(self, message: Image) -> None:
        self.image = message

    def _on_odom(self, message: Odometry) -> None:
        self.pose = message


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image_topic")
    arguments = parser.parse_args()
    rclpy.init()
    node = CaptureNode(arguments.image_topic)
    try:
        deadline = time.monotonic() + 2.5
        while time.monotonic() < deadline and node.image is None:
            rclpy.spin_once(node, timeout_sec=0.1)
        if node.image is None:
            raise RuntimeError(f"timed out waiting for {arguments.image_topic}")
        pose_available = node.pose is not None
        if node.pose is not None:
            orientation = node.pose.pose.pose.orientation
            yaw = math.atan2(
                2 * (orientation.w * orientation.z + orientation.x * orientation.y),
                1 - 2 * (orientation.y * orientation.y + orientation.z * orientation.z),
            )
            x_m = node.pose.pose.pose.position.x
            y_m = node.pose.pose.pose.position.y
        else:
            x_m = y_m = yaw = 0.0
        png = _rgb8_png(node.image)
        print(
            json.dumps(
                {
                    "image_png_base64": base64.b64encode(png).decode("ascii"),
                    "width": node.image.width,
                    "height": node.image.height,
                    "x_m": x_m,
                    "y_m": y_m,
                    "yaw_rad": yaw,
                    "source_topic": arguments.image_topic,
                    "pose_available": pose_available,
                }
            )
        )
        return 0
    except (RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
