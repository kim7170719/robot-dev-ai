from geometry_msgs.msg import TransformStamped, Twist
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')
        self._x = 0.0
        self._vx = 0.0
        self._tf = TransformBroadcaster(self)
        self.create_subscription(Twist, 'cmd_vel', self._on_cmd, 10)
        self.create_timer(0.1, self._tick)

    def _on_cmd(self, msg):
        self._vx = msg.linear.x

    def _tick(self):
        self._x += self._vx * 0.1
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self._x
        t.transform.rotation.w = 1.0
        self._tf.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
