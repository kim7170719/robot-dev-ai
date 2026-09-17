# robot-dev-ai

Open-source, model-agnostic, hardware-aware AI robot development platform.

Users describe a robot in natural language. The platform uses structured hardware knowledge, ROS 2 packages, and templates to generate and integrate a project, build it, diagnose failures, validate in Isaac Sim, and later deploy to NVIDIA Jetson.

## Research environment

- **Primary OS:** Ubuntu 24.04 LTS (ROS / Isaac)
- **Helper OS:** Windows 10 (Cursor, docs, Git)
- **ROS:** ROS 2 Jazzy only (MVP)
- **First robot:** differential drive

Ubuntu and Windows each keep an independent clone. GitHub is the only sync point.

## Current milestone

Gate 0 **PASS**. Gate G1 **PASS** on `feature/m1-ros-baseline`. Windows: `docs/windows_next.md` on that branch.

## Start here

1. `CURSOR_PROJECT_GUIDE.md`
2. `docs/PROJECT_CONTEXT.md`
3. `docs/environment.md`
4. `docs/progress.md`
5. `docs/windows_next.md` (Windows clone / helper OS; do not share the Ubuntu Cursor chat)
6. `docs/os_handoff.md` (live dual-boot packet; open on GitHub after every reboot)
7. `.cursor/rules/robotics.mdc`

## Scope freeze (MVP)

No extra ROS distributions, no Windows ROS/Isaac as the official stack, no extra robot morphologies, no training a foundation model, and no Cosmos in place of Isaac Sim physics. GUI work waits until after M12.
