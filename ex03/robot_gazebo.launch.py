import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    base_dir = os.path.expanduser('~/ROS2/ex03')
    urdf_path = os.path.join(base_dir, 'robot.gazebo.xacro')

    return LaunchDescription([
        # Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': urdf_path}]
        ),

        # Joint state publisher GUI
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
        ),

        # Gazebo simulator
        Node(
            package='gazebo_ros',
            executable='gzserver',
            name='gazebo',
            output='screen',
            arguments=['-s', 'libgazebo_ros_factory.so']
        ),

        Node(
            package='gazebo_ros',
            executable='gzclient',
            name='gazebo_gui',
            output='screen'
        ),
    ])
