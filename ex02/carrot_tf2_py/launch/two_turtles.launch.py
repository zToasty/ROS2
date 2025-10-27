from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        # Запускаем turtlesim с двумя черепахами
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim_node'
        ),
        
        # Создаем вторую черепаху
        ExecuteProcess(
            cmd=['ros2 service call /spawn turtlesim/srv/Spawn '
                 '{x: 5.0, y: 5.0, theta: 0.0, name: "turtle2"}'],
            shell=True
        ),
    ])