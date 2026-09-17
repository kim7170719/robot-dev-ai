from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    pkg = FindPackageShare('simple_diff_robot')
    xacro_file = PathJoinSubstitution([pkg, 'urdf', 'simple_diff_robot.urdf.xacro'])
    controllers = PathJoinSubstitution([pkg, 'config', 'diff_drive_controllers.yaml'])
    rviz_config = PathJoinSubstitution([pkg, 'rviz', 'robot.rviz'])

    robot_description = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', xacro_file]),
        value_type=str,
    )

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': use_sim_time}],
        output='screen',
    )
    control = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[controllers, {'use_sim_time': use_sim_time}],
        remappings=[
            ('~/robot_description', '/robot_description'),
            ('/diff_drive_controller/cmd_vel_unstamped', '/cmd_vel'),
            ('/diff_drive_controller/odom', '/odom'),
        ],
        output='screen',
    )
    js = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )
    dd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller'],
        output='screen',
    )
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        condition=IfCondition(use_rviz),
        output='screen',
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument('use_sim_time', default_value='false'),
            DeclareLaunchArgument('use_rviz', default_value='false'),
            rsp,
            control,
            RegisterEventHandler(OnProcessExit(target_action=js, on_exit=[dd])),
            js,
            rviz,
        ]
    )
