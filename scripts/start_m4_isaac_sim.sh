#!/usr/bin/env bash
set -euo pipefail

container_name="isaac-m4-g4"
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cache_root="/home/yu/docker/isaac-sim"

if docker ps --format '{{.Names}}' | rg -qx "$container_name"; then
  echo "$container_name is already running"
  exit 0
fi

mkdir -p "$cache_root/kit" "$cache_root/ov" "$cache_root/pip"
exec docker run -d --rm --name "$container_name" --gpus all --network=host \
  -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
  -e CYCLONEDDS_URI='<CycloneDDS><Domain><General><AllowMulticast>false</AllowMulticast></General><Discovery><Peers><Peer address="127.0.0.1"/></Peers></Discovery></Domain></CycloneDDS>' \
  -v "$repo_root/simulator/worlds:/root/worlds:ro" \
  -v "$cache_root/kit:/root/.cache/ov/kit" \
  -v "$cache_root/ov:/root/.cache/ov" \
  -v "$cache_root/pip:/root/.cache/pip" \
  --entrypoint /isaac-sim/kit/kit \
  nvcr.io/nvidia/isaac-sim:4.5.0 \
  /isaac-sim/apps/omni.isaac.sim.streaming.kit --no-window --allow-root \
  --exec /root/worlds/m4_lidar_scan.py
