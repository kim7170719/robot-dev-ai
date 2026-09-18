# Windows checklist (M2)

Do **not** install ROS / Isaac / Cosmos on Windows.

G1 and the M1 pipeline are on **`develop`**. M2 URDF work is Ubuntu-only.

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git fetch --tags
git status
git log -5 --oneline
```

You should see PR #4 and #5 merge commits. If every file is modified, stop (CRLF).

Browser (M2 notes, Ubuntu will run these):  
https://github.com/kim7170719/robot-dev-ai/blob/feature/m2-simple-diff-robot/docs/m2_simple_diff_robot.md
