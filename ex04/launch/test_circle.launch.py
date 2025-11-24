import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Только Gazebo
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # Только узел движения по кругу
    circle_movement = Node(
        package='gaz_circle_movement',
        executable='circle_movement',
        output='screen'
    )

    # Только bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'],
        output='screen'
    )

    return LaunchDescription([
        gz_sim,
        bridge,
        circle_movement,
    ])