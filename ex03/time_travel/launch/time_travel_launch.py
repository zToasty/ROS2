from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    delay_arg = DeclareLaunchArgument(
        'delay',
        default_value='5.0',
        description='Time delay (in seconds) for turtle2 to follow turtle1'
    )

    return LaunchDescription([
        delay_arg,

        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim',
            output='screen'
        ),

        TimerAction(
            period=2.0,
            actions=[
                ExecuteProcess(
                    cmd=[
                        'ros2', 'service', 'call', '/spawn', 'turtlesim/srv/Spawn',
                        "{x: 4.0, y: 2.0, theta: 0.0, name: 'turtle2'}"
                    ],
                    output='screen'
                )
            ]
        ),

        Node(
            package='time_travel',
            executable='turtle_tf2_broadcaster',
            name='turtle1_tf2_broadcaster',
            parameters=[{'turtlename': 'turtle1'}],
            output='screen'
        ),

        Node(
            package='time_travel',
            executable='turtle_tf2_broadcaster',
            name='turtle2_tf2_broadcaster',
            parameters=[{'turtlename': 'turtle2'}],
            output='screen'
        ),

        Node(
            package='time_travel',
            executable='time_travel_turtle',
            name='time_travel_turtle',
            parameters=[{'delay': LaunchConfiguration('delay')}],
            output='screen'
        ),
    ])
