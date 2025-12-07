import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_name = 'pylesos_lidar'
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_share = get_package_share_directory(pkg_name)

    # Путь к конфигу RViz и URDF
    rviz_config_file = os.path.join(pkg_share, 'config', 'lidar.rviz') 
    urdf_file = os.path.join(pkg_share, 'urdf', 'robot.urdf.xacro')
    robot_desc = ParameterValue(Command(['xacro ', urdf_file]), value_type=str)

    # 1. Запуск GAZEBO
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r gpu_lidar_sensor.sdf'}.items() 
    )

    # 2. State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # 3. Спавн робота
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-z', '0.5'],
        output='screen'
    )

    # 4. BRIDGE
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',

            '/depth_camera@sensor_msgs/msg/Image[gz.msgs.Image',

            '/depth/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            
            '/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo'
        ],
        remappings=[
            ('/depth_camera', '/image_raw') # Переименовываем для ROS
        ],
        output='screen'
    )

    # 5. RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_file], 
        parameters=[{'use_sim_time': True}]
    )

    # 6. Управление
    rqt_steering = Node(
        package='rqt_robot_steering',
        executable='rqt_robot_steering',
        parameters=[{'default_topic': '/cmd_vel'}] 
    )

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        spawn,
        bridge,
        rviz,
        rqt_steering
    ])
