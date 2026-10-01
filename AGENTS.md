# Agent instructions

Open-source, model-agnostic, hardware-aware AI robot platform. Users describe a robot in natural language; the system uses structured hardware knowledge, ROS 2 packages, and templates to generate, build, diagnose, validate in Isaac Sim, and later deploy to NVIDIA Jetson.

This file is the stable rule set. Live status: `docs/AI_HANDOFF.md`. Tasks: `docs/TODO.md`. Architecture choices: `docs/DECISIONS.md`.

## Stack (do not change without an ADR)

- Ubuntu 24.04 LTS — official ROS / Isaac host
- Windows 10 — helper OS only (Cursor, docs, Git). No ROS, Isaac, or Nav2 on Windows
- ROS 2 Jazzy only (MVP)
- System Python 3.12 — do not replace or globally downgrade
- Isaac Sim 4.5 via Docker (`nvcr.io/nvidia/isaac-sim:4.5.0`) — not 5.x/6.0 (VRAM)
- Nav2 + slam_toolbox on Jazzy
- First robot: differential drive (`simple_diff_robot`)
- Later: Isaac ROS, then Jetson. Cosmos is not a physics replacement (M13+)

## Layout

```text
ros_ws/src/     ROS 2 packages (m1_baseline, simple_diff_robot, simple_diff_nav)
simulator/      Isaac Sim --exec scripts and worlds
docs/           progress, runbooks, ADRs (docs/decisions/)
experiments/    raw milestone logs
scripts/        dual-boot git helpers
agent/          AI orchestration (not started)
registry/       hardware/package knowledge (not started)
templates/      reusable ROS fragments (not started)
validator/      automated graph/TF/nav checks (not started)
```

## Build / test / run

```bash
source /opt/ros/jazzy/setup.bash
cd ~/dev/robot-dev-ai/ros_ws
colcon build --packages-select simple_diff_robot simple_diff_nav
source install/setup.bash
colcon test --packages-select simple_diff_nav
```

Host Nav2 (no Isaac): `docs/m4_nav2.md` Step 3.
Isaac Sim G4: `docs/m4_nav2.md` Step 4 (`--entrypoint /isaac-sim/kit/kit`, CycloneDDS, `use_isaac_sim:=true`).

RViz on this NVIDIA host: `export __GL_THREADED_OPTIMIZATIONS=0`.

## Git

- Repo: `kim7170719/robot-dev-ai`
- Ubuntu clone: `/home/yu/dev/robot-dev-ai`
- Windows clone: `C:\dev\robot-dev-ai` (independent; sync only via GitHub)
- Never develop on `main`. Never force-push `main` or `develop`
- Branches: `develop` ← `feature/*` / `fix/*` / `docs/*`
- Dual-boot: commit + push before reboot; update `docs/os_handoff.md`; other OS reads GitHub, not chat
- Do not commit secrets, `.env`, credentials, `ros_ws/build`, `install`, `log`, or large generated assets

## Hard rules

1. Do not change ROS distro, system Python, or Isaac Sim major version without `docs/decisions/`.
2. Smallest change that satisfies the current milestone. No speculative frameworks.
3. Never hide build/test failures. Never claim a gate PASS unless acceptance criteria ran.
4. Hardware-dependent code behind interfaces. Sim before real hardware.
5. After a task: tests if behavior changed; update `docs/progress.md` and `docs/AI_HANDOFF.md`.

## More detail

- Research plan: `CURSOR_PROJECT_GUIDE.md`
- Context: `docs/PROJECT_CONTEXT.md`
- Cursor rules: `.cursor/rules/robotics.mdc`
- Git: `docs/git_workflow.md`
- Environment: `docs/environment.md` (driver note: ADR 0003 is newer than the 595 audit line)
