# Windows checklist (after G3)

Ubuntu Cursor chat is not shared. Use GitHub.

**Open first:**

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/os_handoff.md

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/windows_next.md

---

## Do this now

G0, G1, G2, **G3** are all **PASS** on `develop`.

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git fetch --tags
git status
git log -5 --oneline
git tag -l "g*" "m*"
```

You should see:
- `feat: M3 Isaac Sim 4.5 Docker + G3 PASS (#8)` in log
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

---

## Next milestone (Ubuntu only)

M4 Nav2: SLAM, localization, autonomous navigation in Isaac Sim.

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
