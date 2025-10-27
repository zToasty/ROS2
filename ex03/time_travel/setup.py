from setuptools import find_packages, setup

package_name = 'time_travel'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/time_travel_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='toasty',
    maintainer_email='g.karateev@g.nsu.ru',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtle_tf2_broadcaster = time_travel.turtle_tf2_broadcaster:main',
            'time_travel_turtle = time_travel.time_travel_turtle:main',
        ],
    },
)
