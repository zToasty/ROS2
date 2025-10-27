from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        # Аргументы запуска
        DeclareLaunchArgument(
            'radius',
            default_value='2.0',
            description='Radius for carrot rotation'
        ),
        DeclareLaunchArgument(
            'direction_of_rotation',
            default_value='1',
            description='Direction of rotation (1 for clockwise, -1 for counterclockwise)'
        ),
        
        # Запускаем turtlesim
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim_node'
        ),
        
        # Создаем вторую черепаху с задержкой
        TimerAction(
            period=2.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'service', 'call', '/spawn', 'turtlesim/srv/Spawn', 
                         '{"x": 5.0, "y": 5.0, "theta": 0.0, "name": "turtle2"}'],
                    shell=False
                )
            ]
        ),
        
        # Broadcaster для turtle1
        Node(
            package='carrot_tf2_py',
            executable='turtle_tf2_broadcaster',
            name='turtle1_tf2_broadcaster',
            parameters=[{'turtle_name': 'turtle1'}]
        ),
        
        # Broadcaster для turtle2 с задержкой (после создания черепахи)
        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package='carrot_tf2_py',
                    executable='turtle_tf2_broadcaster',
                    name='turtle2_tf2_broadcaster',
                    parameters=[{'turtle_name': 'turtle2'}]
                )
            ]
        ),
        
        # Broadcaster для морковки
        Node(
            package='carrot_tf2_py',
            executable='carrot_tf2_broadcaster',
            name='carrot_tf2_broadcaster',
            parameters=[{
                'radius': LaunchConfiguration('radius'),
                'direction_of_rotation': LaunchConfiguration('direction_of_rotation')
            }]
        ),
        
        # Listener для следования за морковкой с задержкой
        TimerAction(
            period=4.0,
            actions=[
                Node(
                    package='carrot_tf2_py',
                    executable='turtle_tf2_listener',
                    name='turtle_tf2_listener'
                )
            ]
        ),
    ])