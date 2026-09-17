# Windows checklist

Ubuntu Cursor chat is not shared. Use GitHub.

**Browser first:**

https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-pipeline/docs/windows_next.md

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/m1_g1.md

## Do this now

G1 is **on `develop`** (PR #4 merged). Do **not** install ROS.

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git fetch --tags
git status
git log -5 --oneline
```

You should see commit `feat: M1 Jazzy baseline and Gate G1 launch (#4)`.

If every file looks modified, stop (CRLF). Do not commit that.

Optional read-only: https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-pipeline/docs/m1_pipeline.md

If you changed nothing, reboot back to Ubuntu when done.

## Must not

ROS 2 / Isaac / Cosmos / Nav2 on Windows. No `main`. No force-push.
