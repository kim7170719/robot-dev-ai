# Windows checklist (M1)

This Cursor Ubuntu chat is **not** shared with Windows. After reboot, use GitHub only.

**Open these two pages in the browser first:**

1. Live packet: https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-ros-baseline/docs/os_handoff.md
2. This checklist: https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-ros-baseline/docs/windows_next.md

Clone: `C:\dev\robot-dev-ai`  
Do not open the Ubuntu working tree from a shared disk.

---

## Do this now (this reboot)

1. Fetch tags and stay on `develop` (do **not** install ROS).

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git fetch --tags
git status
git log -5 --oneline
git tag -l "g0-*"
```

2. Confirm you see tag `g0-environment-baseline`. If `git status` lists almost every file as modified, **stop** (CRLF). Do not commit that.

3. Optional: bookmark the two GitHub URLs above.

4. You may **read** (no install):

- https://docs.ros.org/en/jazzy/
- https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
- Issue https://github.com/kim7170719/robot-dev-ai/issues/3
- Ubuntu install notes (on the feature branch in the browser): https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-ros-baseline/docs/m1_ros_jazzy.md

5. Do **not** edit files this round unless you have a docs-only change. If you changed nothing:

```powershell
git status
```

Must be clean, then reboot back to Ubuntu.

6. If you **must** commit docs from Windows, use a branch from `develop`, never `main`:

```powershell
git switch develop
git pull --ff-only
git switch -c docs/m1-notes
# edit markdown only
git add <files>
git commit -m "docs: ..."
git push -u origin docs/m1-notes
```

Then open a PR into `develop`. Before reboot: commit and push. Do not use `git stash` across OS.

---

## Must not do on Windows

- Install ROS 2 / Jazzy / turtlesim
- Install Isaac Sim, Isaac ROS, Nav2, or Cosmos
- Treat Windows as the official ROS machine
- Change ROS distribution or system Python
- `git push --force` on `main` or `develop`
- Work on `main`
- Switch to deleted branch `docs/g0-cross-os-sync`

---

## Ubuntu is doing (not you)

M1-01: install ROS 2 Jazzy desktop with `sudo` using `docs/m1_ros_jazzy.md`.  
Gate G1 is not PASS until Ubuntu has `ros2 --help`, turtlesim, `colcon build`, and a first package.

When Ubuntu records G1 in `docs/progress.md`, a new Windows GitHub checklist will replace this one.

---

## After every reboot (habit)

Leaving Windows: `git status` → commit if needed → `git push` → `.\scripts\before_reboot.ps1` → reboot.  
Arriving: browser packet first → then the PowerShell block in **Do this now**.
