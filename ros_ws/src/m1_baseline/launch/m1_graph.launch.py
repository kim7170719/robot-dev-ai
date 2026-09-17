from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(package='m1_baseline', executable='talker', name='m1_talker'),
            Node(package='m1_baseline', executable='listener', name='m1_listener'),
            Node(package='m1_baseline', executable='adder', name='m1_adder'),
            Node(package='m1_baseline', executable='fibonacci', name='m1_fibonacci'),
        ]
    )
