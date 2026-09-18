# 0001: NVIDIA GLX fix — disable threaded optimizations for Ogre3D

Date: 2026-09-17

## Problem

RViz2 crashed on this host with:

```
X Error of failed request: BadValue (integer parameter out of range for operation)
  Major opcode: 152 (GLX)
  Minor opcode: 24 (X_GLXCreateNewContext)
  Value in failed request: 0x0
```

and `Unable to create the rendering window after 100 tries`.

## Host

- Ubuntu 24.04.4 LTS, GNOME / X11, `DISPLAY=:1`
- NVIDIA GeForce RTX 2080 Ti (single GPU, no iGPU)
- Driver: 595.84 open kernel module (`nvidia-driver-595-open`)
- `prime-select on-demand` (desktop with one GPU — `prime-select nvidia` not applicable)
- `glxgears` worked; base GLX is fine
- `glxinfo` shows `OpenGL renderer: NVIDIA GeForce RTX 2080 Ti`

## Root cause

NVIDIA's threaded GL optimizations (`__GL_THREADED_OPTIMIZATIONS`) causes Ogre3D (used by RViz2) to receive an invalid fbconfig ID (0x0) when creating its GLX context. This is an Ogre + NVIDIA driver interaction bug, not a ROS problem.

## Fix

```bash
export __GL_THREADED_OPTIMIZATIONS=0
```

Add to `~/.bashrc` for persistence. After this, `rviz2` starts with `OpenGL 4.6 (GLSL 4.6)` using hardware acceleration.

## Workaround (no longer needed)

`LIBGL_ALWAYS_SOFTWARE=1` forces Mesa software rendering. Works but uses CPU only.

## Affected tools

Any application using Ogre3D with NVIDIA on this host (primarily RViz2).
