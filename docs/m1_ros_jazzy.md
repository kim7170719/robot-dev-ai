# M1-01: ROS 2 Jazzy on Ubuntu 24.04

Official source (re-checked 2026-09-17):  
https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

Ubuntu is the only install target. Do not install ROS 2 as the research stack on Windows. Do not start Cosmos.

Locale on this machine is already UTF-8 (`zh_TW.UTF-8`). Apt suites include `noble noble-updates noble-backports`.

This agent cannot enter `sudo` password. Run the commands below in an Ubuntu terminal, then come back to Cursor.

## Install (desktop, recommended)

```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt update
sudo apt upgrade
sudo apt install ros-jazzy-desktop
sudo apt install ros-dev-tools
```

## Verify

```bash
source /opt/ros/jazzy/setup.bash
ros2 --help
ros2 doctor --report | head
```

turtlesim (needs a display):

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

In another terminal:

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtle_teleop_key
```

Workspace + first package come after `ros2 --help` succeeds. Record results in `docs/progress.md`. Do not claim Gate G1 until the package builds and launch starts multiple nodes.
