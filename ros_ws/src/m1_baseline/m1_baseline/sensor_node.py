from std_msgs.msg import Float32
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')
        self._pub = self.create_publisher(Float32, 'range', 10)
        self._t = 0.0
        self.create_timer(0.2, self._tick)

    def _tick(self):
        msg = Float32()
        msg.data = 1.0 + 0.8 * ((self._t % 4.0) - 2.0) / 2.0
        self._pub.publish(msg)
        self._t += 0.2


def main(args=None):
    rclpy.init(args=args)
    node = SensorNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
