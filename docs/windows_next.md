# Windows next steps (after Gate 0 probe)

This Cursor Ubuntu chat is not shared with Windows. Use this file on GitHub.

**Open here:**

https://github.com/kim7170719/robot-dev-ai/blob/docs/g0-cross-os-sync/docs/windows_next.md

Previous (done): `docs/g0_windows_handoff.md`  
Master plan: `CURSOR_PROJECT_GUIDE.md`  
Ubuntu ROS work: wait until Gate 0 is merged; then M1 is **Ubuntu only**.

Do not install ROS 2, Isaac Sim, Isaac ROS, or Cosmos on Windows. Windows is Cursor, documents, Git, and reading.

---

## 1. Right now: sync this branch

Gate 0 probe already passed. PR to `develop` is:

https://github.com/kim7170719/robot-dev-ai/pull/1

Until that PR is merged, stay on the docs branch:

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch docs/g0-cross-os-sync
git pull --ff-only
git status
```

Read this file again after pull. `git status` must be clean. If every file looks modified, stop (CRLF problem).

---

## 2. After PR #1 is merged: move to `develop`

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git status
git log -5 --oneline
```

You should see the Gate 0 docs on `develop`. Then this same guide will live at:

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/windows_next.md

Do not develop on `main`. Do not `git push --force`.

---

## 3. Next milestone is M1 (not Cosmos)

Issue: **M1-01 — Install and verify ROS 2 Jazzy on Ubuntu 24.04**

That install runs only on Ubuntu. On Windows you may:

- Read https://docs.ros.org/en/jazzy/ before Ubuntu starts the install
- Edit docs, thesis notes, issues, and this repo via Git
- Use Cursor on `C:\dev\robot-dev-ai` in a **new** chat
- Before editing: `git fetch --prune`, same branch as Ubuntu, `git pull --ff-only`, then `git status` clean

On Windows you must **not**:

- Treat Windows as the ROS / Isaac machine
- Change ROS distribution, system Python, or add extra robot types
- Start Cosmos, Isaac Sim, Nav2, or Jetson work

M1 acceptance (verified on Ubuntu, recorded in `docs/progress.md`):

- `source /opt/ros/jazzy/setup.bash`
- `ros2 --help`
- turtlesim starts
- workspace `colcon build`
- first own package exists
- install commands written in docs

---

## 4. If you must commit from Windows during M1

Use a task branch from `develop`, never `main`:

```powershell
git switch develop
git pull --ff-only
git switch -c docs/m1-notes
```

Commit message style: `docs: ...`  
After push, open a PR into `develop`.

Before switching back to Ubuntu: commit and push. Do not use `git stash` to carry work across OS.

---

## 5. Stop condition

When Ubuntu records M1 Gate G1 in `docs/progress.md`, the next Windows guide will be added on GitHub the same way. Until then, this file is the Windows checklist.
