# M3: Isaac Sim 4.5 via Docker

Not Isaac Sim 5.x/6.0 (requires RTX 4080 / 16GB VRAM). See `docs/decisions/0002-isaac-sim-version-docker.md`.

Host: RTX 2080 Ti 11GB. Isaac Sim 4.5 minimum is RTX 3070 / 8GB.

---

## Verified setup (2026-09-18)

| Item | Status |
|---|---|
| Docker | 29.8.1 |
| NVIDIA Container Toolkit | installed |
| `docker run --gpus all ... nvidia-smi` | PASS (RTX 2080 Ti 11GB) |
| Isaac Sim 4.5 image | `nvcr.io/nvidia/isaac-sim:4.5.0` pulled |
| Driver when 595 used | **CRASH** — `librtx.scenedb.plugin.so` segfault |
| Driver downgrade to 580 | PASS — `nvidia-driver-580` installed |
| Isaac Sim headless startup | **PASS** — `isaacsim.exp.full.streaming-4.5.0` loaded, 1781 MiB VRAM |
| Startup time (first run) | ~35 min (shader compilation); subsequent runs ~1–3 min |

Driver note: 595 causes `librtx.scenedb.plugin.so` crash in Isaac Sim 4.5. Driver 580 works.

---

## Step 1: Install Docker

```bash
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc 2>/dev/null || true

# Install via official script
curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
sudo sh /tmp/get-docker.sh
sudo usermod -aG docker $USER

# Verify (log out and back in for group to take effect, or use newgrp)
newgrp docker
docker --version
```

## Step 2: Install NVIDIA Container Toolkit

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Verify:

```bash
docker run --rm --gpus all nvidia/cuda:12.6-base-ubuntu24.04 nvidia-smi
```

## Step 3: Pull Isaac Sim 4.5

```bash
docker pull nvcr.io/nvidia/isaac-sim:4.5.0
```

**Note:** ~25 GB. Needs internet. Allow downloads from `nvcr.io`.

## Step 4: Run basic scene

```bash
docker run --gpus all -e "ACCEPT_EULA=Y" \
  -v ~/docker/isaac-sim/cache/kit:/isaac-sim/kit/cache:rw \
  -v ~/docker/isaac-sim/cache/ov:/root/.cache/ov:rw \
  -v ~/docker/isaac-sim/cache/pip:/root/.cache/pip:rw \
  -v ~/docker/isaac-sim/cache/glcache:/root/.cache/mesa_shader_cache:rw \
  -v ~/docker/isaac-sim/cache/computecache:/root/.nv/ComputeCache:rw \
  -v ~/docker/isaac-sim/logs:/root/.nvidia-omniverse/logs:rw \
  -v ~/docker/isaac-sim/data:/root/.local/share/ov/data:rw \
  -v ~/docker/isaac-sim/documents:/root/Documents:rw \
  --network=host \
  nvcr.io/nvidia/isaac-sim:4.5.0 ./runheadless.native.sh
```

## Step 5: ROS 2 Bridge (in container)

Isaac Sim 4.5 includes the ROS 2 bridge. To enable:

```bash
# Inside container or via extension manager
# Extension: isaacsim.ros2.bridge
```

## Gate G3 acceptance

- [ ] Isaac Sim 4.5 container starts
- [ ] Basic scene opens (headless OK)
- [ ] URDF import of `simple_diff_robot`
- [ ] USD saved
- [ ] ROS 2 bridge enabled
- [ ] `/cmd_vel` controls robot in Isaac Sim
- [ ] Isaac Sim publishes `/odom` `/scan` `/camera` to ROS 2
