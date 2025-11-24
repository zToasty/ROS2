import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_pylesos_gazebo = get_package_share_directory('pylesos_gazebo')

    # Путь к URDF файлу
    urdf_file = os.path.join(pkg_pylesos_gazebo, 'urdf', 'robot.gazebo.xacro')
    
    # Загрузка URDF через xacro и преобразование в строку
    robot_description_content = Command(['xacro ', urdf_file])

    # Launch Gazebo Sim
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # Robot State Publisher - ФИКС: добавляем use_sim_time
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True  # ВАЖНО для Gazebo!
        }]
    )

    # Spawn Robot с задержкой
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'pylesos_robot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0', 
            '-z', '0.1'
        ],
        output='screen'
    )

    # Bridge для преобразования сообщений
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Управление (ROS -> Gazebo)
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            
            # Одометрия (Gazebo -> ROS)
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            
            # TF (Gazebo -> ROS)
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            
            # ВАЖНО: Состояние суставов (Gazebo -> ROS)
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model'
        ],
        output='screen'
    )

    # *** ДОБАВЛЯЕМ УПРАВЛЕНИЕ ***
    rqt_steering = ExecuteProcess(
        cmd=['ros2', 'run', 'rqt_robot_steering', 'rqt_robot_steering'],
        output='screen'
    )

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        bridge,
        rqt_steering,
        
        # Задержка перед спавном робота
        TimerAction(
            period=3.0,
            actions=[spawn_entity]
        ),
    ])