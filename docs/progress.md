# Progress

## Week 00 Goal

Gate 0 environment audit and repository baseline on Ubuntu.

Acceptance criteria:

1. Ubuntu version, GPU, Python, and disk space are recorded in `docs/environment.md`.
2. Repository layout matches `CURSOR_PROJECT_GUIDE.md` section 3.
3. Cursor can read `CURSOR_PROJECT_GUIDE.md` and `.cursor/rules/robotics.mdc`.
4. GitHub `kim7170719/robot-dev-ai` exists, Ubuntu and Windows each have an independent clone, and round-trip sync works.

Out of scope:

- ROS 2 Jazzy install (M1)
- Isaac Sim / Isaac ROS / Cosmos
- GUI
- First robot package

## Current milestone

M0 Environment Audit. Gate G0 is **not** complete.

## Gate 0 checklist

| Criterion | Status | Evidence |
|---|---|---|
| Ubuntu 24.04 LTS | PASS | `lsb_release -a` → 24.04.4 LTS |
| `nvidia-smi` works | PASS | Driver 595.84, RTX 2080 Ti |
| GPU / VRAM / Driver recorded | PASS | `docs/environment.md` |
| RAM / disk recorded | PASS | 31 GiB RAM, 412G free on `/` |
| Git installed | PASS | 2.43.0 |
| Project directories | PASS | repo layout created |
| `.gitignore` / `.gitattributes` | PASS | repo root |
| Cursor rules | PASS | `.cursor/rules/robotics.mdc` |
| Guide in repo | PASS | `CURSOR_PROJECT_GUIDE.md` |
| Git identity on Ubuntu | PASS | local git identity present |
| GitHub SSH/HTTPS on Ubuntu | PASS | SSH as `kim7170719`; `gh` 2.99.0 |
| GitHub repo `kim7170719/robot-dev-ai` | PASS | https://github.com/kim7170719/robot-dev-ai |
| First commit / push | PASS | Ubuntu `main` + `develop` pushed |
| Windows independent clone | PASS | `C:\dev\robot-dev-ai`; marker `g0-windows-probe-2026-09-17` |
| Ubuntu → GitHub → Windows → GitHub → Ubuntu | in progress | Windows pulled Ubuntu probe; Ubuntu pull still needed |
| Milestone tag `g0-environment-baseline` | FAIL | Gate 0 not passed |

## This session

- Created `/home/yu/dev/robot-dev-ai` and moved `CURSOR_PROJECT_GUIDE.md` into it.
- Installed user-local `gh` 2.99.0; GitHub CLI logged in as `kim7170719`.
- Created public GitHub repo `kim7170719/robot-dev-ai` and pushed the Ubuntu clone.

## Gate 0 Windows probe

- Date: 2026-09-17
- Clone: `C:\dev\robot-dev-ai`
- Branch: `docs/g0-cross-os-sync`
- Marker: `g0-windows-probe-2026-09-17`
- Confirmed Ubuntu marker `g0-ubuntu-probe-2026-09-17` after `git pull --ff-only`

## Next (after Gate 0)

Issue M1-01: Install and verify ROS 2 Jazzy on Ubuntu 24.04. Do not start Cosmos.

## Open blockers

1. On Windows, independently `git clone git@github.com:kim7170719/robot-dev-ai.git` into `C:\dev\robot-dev-ai`.
2. Complete Ubuntu → GitHub → Windows → GitHub → Ubuntu sync, then add tag `g0-environment-baseline`.
