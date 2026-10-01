"""Launch SLAM Toolbox. Host mock hardware, or Isaac Sim (no ros2_control)."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_isaac_sim = LaunchConfiguration('use_isaac_sim')
    slam_params = PathJoinSubstitution(
        [FindPackageShare('simple_diff_nav'), 'config', 'slam_params.yaml']
    )
    xacro_file = PathJoinSubstitution(
        [FindPackageShare('simple_diff_robot'), 'urdf', 'simple_diff_robot.urdf.xacro']
    )
    robot_description = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', xacro_file]),
        value_type=str,
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('slam_toolbox'),
                'launch',
                'online_async_launch.py',
            ])
        ]),
        launch_arguments={
            'slam_params_file': slam_params,
            'use_sim_time': use_sim_time,
        }.items(),
    )

    robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('simple_diff_robot'),
                'launch',
                'robot.launch.py',
            ])
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'use_rviz': 'false',
        }.items(),
        condition=UnlessCondition(use_isaac_sim),
    )

    rsp_isaac = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': use_sim_time}],
        output='screen',
        condition=IfCondition(use_isaac_sim),
    )
    odom_tf = Node(
        package='simple_diff_nav',
        executable='odom_to_tf.py',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
        condition=IfCondition(use_isaac_sim),
    )
    scan_sim = Node(
        package='simple_diff_nav',
        executable='scan_sim.py',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
        condition=UnlessCondition(use_isaac_sim),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument(
            'use_isaac_sim',
            default_value='false',
            description='If true, skip ros2_control and scan_sim; Isaac Sim provides /odom /scan /clock',
        ),
        robot,
        rsp_isaac,
        odom_tf,
        scan_sim,
        slam,
    ])
