#!/usr/bin/env bash
set -eo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

source /opt/ros/jazzy/setup.bash
source "$repo_root/ros_ws/install/setup.bash"
set -u

exec "$repo_root/.venv/bin/uvicorn" api.app:create_app --factory \
  --host 127.0.0.1 --port "${ROBOT_DEV_AI_PORT:-8000}"
