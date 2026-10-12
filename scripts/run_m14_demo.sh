#!/usr/bin/env bash
set -eo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

mode=${ROBOT_DEV_AI_MODE:-local}
case "$mode" in
  local)
    host=127.0.0.1
    read_only=false
    ;;
  lan-readonly)
    host=${ROBOT_DEV_AI_LAN_BIND:?Set ROBOT_DEV_AI_LAN_BIND to the intended LAN IP (or 127.0.0.1 behind a reverse proxy).}
    read_only=true
    ;;
  *)
    echo "Unsupported ROBOT_DEV_AI_MODE: $mode (use local or lan-readonly)" >&2
    exit 2
    ;;
esac

source /opt/ros/jazzy/setup.bash
source "$repo_root/ros_ws/install/setup.bash"
set -u

export ROBOT_DEV_AI_READ_ONLY="$read_only"

exec "$repo_root/.venv/bin/uvicorn" api.app:create_app --factory \
  --host "$host" --port "${ROBOT_DEV_AI_PORT:-8000}"
