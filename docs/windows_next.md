# Windows checklist (after G4)

Ubuntu Cursor chat is not shared. Use GitHub.

**Open first:**

https://github.com/kim7170719/robot-dev-ai/blob/feature/m4-nav2/docs/os_handoff.md

https://github.com/kim7170719/robot-dev-ai/blob/feature/m4-nav2/docs/windows_next.md

---

## Do this now

G0 through **G4** are all **PASS** on `feature/m4-nav2`. G4 must be merged into `develop` before treating `develop` as the current milestone branch.

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch feature/m4-nav2
git pull --ff-only
git fetch --tags
git status
git log -5 --oneline
git tag -l "g*" "m*"
```

You should see:
- the G4 checkpoint commit in the log
- Tags: `g0-environment-baseline`, `m2-g2-simple-diff-robot`, `m3-g3-isaac-sim`

If every file looks modified, stop (CRLF). Do not commit that.

---

## What was completed (Ubuntu, not for Windows)

| Milestone | Status |
|---|---|
| G0 environment baseline | PASS |
| G1 ROS 2 Jazzy + multi-node | PASS |
| G2 simple_diff_robot URDF + ros2_control | PASS |
| G3 Isaac Sim 4.5 + cmd_vel/odom via CycloneDDS | **PASS** |
| G4 Nav2 + SLAM navigation in Isaac Sim | **PASS** |

---

## Next milestone (Ubuntu only)

M5 Isaac ROS baseline: one reproducible NVIDIA-accelerated ROS pipeline. This is Ubuntu-only and has not started.

**Do NOT do on Windows:**
- Install ROS 2, Isaac Sim, Isaac ROS, Nav2, Cosmos
- Work on `main` or force-push `develop`

---

## If you commit docs from Windows

```powershell
git switch develop
git pull --ff-only
git switch -c docs/notes
# edit markdown only
git add <files>
git commit -m "docs: ..."
git push -u origin docs/notes
```

Open PR into `develop`. Commit/push before rebooting.
