#!/usr/bin/env python3
"""Publish /scan from /odom so slam_toolbox can build map without RTX LiDAR."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rclpy
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

from room_scan import N_RAYS, RANGE_MAX, RANGE_MIN, ranges_from_pose


class ScanSim(Node):
    def __init__(self):
        super().__init__('scan_sim', automatically_declare_parameters_from_overrides=True)
        self._pose = (0.0, 0.0, 0.0)
        self._stamp = None
        self.create_subscription(Odometry, 'odom', self._on_odom, 10)
        self._pub = self.create_publisher(LaserScan, 'scan', 10)
        self.create_timer(0.1, self._tick)
        self.get_logger().info('scan_sim publishing /scan from /odom (synthetic 8x6m room)')

    def _on_odom(self, msg: Odometry):
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        self._pose = (p.x, p.y, yaw)
        self._stamp = msg.header.stamp

    def _tick(self):
        x, y, yaw = self._pose
        msg = LaserScan()
        msg.header.stamp = self._stamp if self._stamp is not None else self.get_clock().now().to_msg()
        msg.header.frame_id = 'lidar_link'
        msg.angle_min = -math.pi
        msg.angle_max = math.pi - (2.0 * math.pi / N_RAYS)
        msg.angle_increment = 2.0 * math.pi / N_RAYS
        msg.time_increment = 0.0
        msg.scan_time = 0.1
        msg.range_min = RANGE_MIN
        msg.range_max = RANGE_MAX
        msg.ranges = ranges_from_pose(x, y, yaw)
        self._pub.publish(msg)


def main():
    rclpy.init()
    node = ScanSim()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
