from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    base_dir = os.path.expanduser('~/ROS2')
    xacro_file = os.path.join(base_dir, 'ex02/robot.urdf.xacro')
    rviz_config_path = os.path.join(base_dir, 'ex01/pylesos.rviz')

    return LaunchDescription([
        # --- Генерация URDF из Xacro и запуск Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': os.popen(f"xacro {xacro_file}").read()}]
        ),

        # --- GUI для управления суставами
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
        ),

        # --- RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_path]
        )
    ])
