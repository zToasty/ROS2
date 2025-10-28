from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([

        # --- Запуск turtlesim ---
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim',
            output='screen'
        ),

        # --- Спавним черепах с задержками ---
        TimerAction(
            period=0.5,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'service', 'call', '/spawn', 'turtlesim/srv/Spawn',
                         '"{x: 5.54, y: 5.54, theta: 0.0, name: turtle1}"'],
                    shell=True
                )
            ]
        ),
        TimerAction(
            period=1.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'service', 'call', '/spawn', 'turtlesim/srv/Spawn',
                         '"{x: 5.0, y: 5.0, theta: 0.0, name: turtle2}"'],
                    shell=True
                )
            ]
        ),
        TimerAction(
            period=1.5,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'service', 'call', '/spawn', 'turtlesim/srv/Spawn',
                         '"{x: 8.0, y: 8.0, theta: 0.0, name: turtle3}"'],
                    shell=True
                )
            ]
        ),

        # --- TF для черепах ---
        Node(
            package='turtle_multi_target',
            executable='turtle_tf_broadcaster',
            name='turtle_tf_broadcaster',
            output='screen'
        ),

        # --- Вращающиеся цели ---
        Node(
            package='turtle_multi_target',
            executable='target_switcher',
            name='target_switcher',
            output='screen',
            parameters=[
                {'radius': 2.0},
                {'direction_of_rotation': 1}
            ]
        ),

        # --- Контроллер черепах ---
        Node(
            package='turtle_multi_target',
            executable='turtle_controller',
            name='turtle_controller',
            output='screen',
            parameters=[
                {'switch_threshold': 1.5}
            ]
        ),
    ])
