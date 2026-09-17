import time

from example_interfaces.action import Fibonacci
import rclpy
from rclpy.action import ActionServer
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class FibonacciServer(Node):
    def __init__(self):
        super().__init__('m1_fibonacci')
        self._server = ActionServer(self, Fibonacci, 'fibonacci', self._execute)

    def _execute(self, goal_handle):
        feedback = Fibonacci.Feedback()
        sequence = [0, 1]
        order = goal_handle.request.order
        for i in range(1, max(order, 1)):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                return Fibonacci.Result()
            sequence.append(sequence[i] + sequence[i - 1])
            feedback.sequence = sequence
            goal_handle.publish_feedback(feedback)
            time.sleep(0.05)
        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = sequence
        return result


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciServer()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
