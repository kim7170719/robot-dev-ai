from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'm1_baseline'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yu',
    maintainer_email='kim7170719@gmail.com',
    description='M1 ROS 2 Jazzy baseline: talker, listener, service, action, launch.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'talker = m1_baseline.talker:main',
            'listener = m1_baseline.listener:main',
            'adder = m1_baseline.adder:main',
            'fibonacci = m1_baseline.fibonacci:main',
            'sensor_node = m1_baseline.sensor_node:main',
            'planner_node = m1_baseline.planner_node:main',
            'controller_node = m1_baseline.controller_node:main',
        ],
    },
)
