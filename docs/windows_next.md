# Windows checklist (after Gate G1)

This Cursor Ubuntu chat is **not** shared with Windows. After reboot, use GitHub only.

**Open these pages in the browser first** (do not use the stale `develop` copies until the M1 PR merges):

1. https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-ros-baseline/docs/os_handoff.md
2. https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-ros-baseline/docs/windows_next.md
3. https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-ros-baseline/docs/m1_g1.md

Clone: `C:\dev\robot-dev-ai`

---

## Do this now

Ubuntu Gate **G1 is PASS** (`m1_baseline` launch + CLI). You still **do not install ROS**.

1. Sync Git (stay on `develop` until the M1 PR is merged):

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git fetch --tags
git status
git tag -l "g0-*"
```

2. If almost every file is modified, stop (CRLF). Do not commit that.

3. Read the three GitHub URLs above. Confirm G1 in `docs/progress.md` on the **feature branch page**, not an old `develop` file.

4. After the M1 PR is merged into `develop`, run the same fetch/switch/pull again so local `develop` has `m1_baseline` and `docs/m1_g1.md`.

5. If you changed nothing: `git status` clean, then reboot back to Ubuntu when you are done reading.

---

## Must not do on Windows

- Install ROS 2, Isaac Sim, Isaac ROS, Nav2, or Cosmos
- Develop on `main` or force-push `main` / `develop`
- Use deleted branch `docs/g0-cross-os-sync`

---

## Ubuntu next (not you)

Remaining M1 learning (TF2, RViz2, sensor→planner→controller) is optional after G1. M2 is not started. Cosmos is not started.
