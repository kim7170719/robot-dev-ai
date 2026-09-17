from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class PlannerNode(Node):
    def __init__(self):
        super().__init__('planner_node')
        self.declare_parameter('stop_distance', 0.35)
        self._cmd = self.create_publisher(Twist, 'cmd_vel', 10)
        self.create_subscription(Float32, 'range', self._on_range, 10)

    def _on_range(self, msg):
        stop = self.get_parameter('stop_distance').get_parameter_value().double_value
        twist = Twist()
        if msg.data > stop:
            twist.linear.x = 0.2
        self._cmd.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = PlannerNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
