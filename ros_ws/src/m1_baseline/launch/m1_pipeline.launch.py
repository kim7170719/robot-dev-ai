from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(package='m1_baseline', executable='sensor_node', name='sensor_node'),
            Node(
                package='m1_baseline',
                executable='planner_node',
                name='planner_node',
                parameters=[{'stop_distance': 0.35}],
            ),
            Node(package='m1_baseline', executable='controller_node', name='controller_node'),
        ]
    )
