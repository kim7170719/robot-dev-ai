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

M0 Environment Audit. Probe round-trip is PASS. Tag `g0-environment-baseline` is created when this branch reaches `main`.

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
| Ubuntu → GitHub → Windows → GitHub → Ubuntu | PASS | Ubuntu `git pull --ff-only` `0c51e4f..5abfb65`; `docs/progress.md` is LF-only; `git status` clean |
| Milestone tag `g0-environment-baseline` | in progress | PR #1 merged to `develop` (`c951015`); waiting `develop` → `main` |

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

## Gate 0 Ubuntu return pull

- Date: 2026-09-17
- Clone: `/home/yu/dev/robot-dev-ai`
- Command: `git pull --ff-only` on `docs/g0-cross-os-sync`
- Windows commit: `5abfb65` `docs: record Windows Gate 0 pull`
- Line endings: `docs/progress.md` and `docs/environment.md` are LF-only; `git diff --check` clean

## Next (after Gate 0)

Issue M1-01: Install and verify ROS 2 Jazzy on Ubuntu 24.04. Do not start Cosmos.

## Open blockers

1. `develop` → `main`, then tag `g0-environment-baseline`.
2. Windows: `git fetch --prune; git switch develop; git pull --ff-only` (docs branch is deleted).
3. Then M1-01 ROS 2 Jazzy on Ubuntu only.
