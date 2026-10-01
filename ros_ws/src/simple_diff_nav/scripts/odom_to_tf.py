#!/usr/bin/env python3
"""Broadcast odom → base_link from /odom (Isaac Sim does not publish TF)."""
import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class OdomToTf(Node):
    def __init__(self):
        super().__init__('odom_to_tf', automatically_declare_parameters_from_overrides=True)
        self._br = TransformBroadcaster(self)
        self.create_subscription(Odometry, 'odom', self._on_odom, 10)
        self.get_logger().info('odom_to_tf broadcasting odom → base_link')

    def _on_odom(self, msg: Odometry):
        tf = TransformStamped()
        tf.header.stamp = msg.header.stamp
        tf.header.frame_id = msg.header.frame_id or 'odom'
        tf.child_frame_id = msg.child_frame_id or 'base_link'
        tf.transform.translation.x = msg.pose.pose.position.x
        tf.transform.translation.y = msg.pose.pose.position.y
        tf.transform.translation.z = msg.pose.pose.position.z
        tf.transform.rotation = msg.pose.pose.orientation
        self._br.sendTransform(tf)


def main():
    rclpy.init()
    node = OdomToTf()
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
