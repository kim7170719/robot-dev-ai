# Gate 0 Windows handoff

This Cursor chat stays on Ubuntu. Do not try to continue it on Windows.

On Windows use:

1. This file on GitHub (browser is enough)
2. The independent clone at `C:\dev\robot-dev-ai`
3. Come back to Ubuntu Cursor after `git push`

GitHub copy of this file:

https://github.com/kim7170719/robot-dev-ai/blob/docs/g0-cross-os-sync/docs/g0_windows_handoff.md

## PowerShell (run in `C:\dev\robot-dev-ai`)

```powershell
git fetch --prune
git switch docs/g0-cross-os-sync
git pull --ff-only
git status
Select-String -Path docs\environment.md -Pattern "g0-ubuntu-probe-2026-09-17"
```

You must see `g0-ubuntu-probe-2026-09-17`. If `git status` shows every file as modified, stop; that is a CRLF/LF problem. Do not commit that.

## Edit only `docs/progress.md`

Replace these two table rows:

```text
| Windows independent clone | NOT TESTED | clone on Windows to `C:\dev\robot-dev-ai` |
| Ubuntu → GitHub → Windows → GitHub → Ubuntu | NOT TESTED | blocked on Windows clone |
```

with:

```text
| Windows independent clone | PASS | `C:\dev\robot-dev-ai`; marker `g0-windows-probe-2026-09-17` |
| Ubuntu → GitHub → Windows → GitHub → Ubuntu | in progress | Windows pulled Ubuntu probe; Ubuntu pull still needed |
```

Add this section above `## Next (after Gate 0)`:

```text
## Gate 0 Windows probe

- Date: 2026-09-17
- Clone: `C:\dev\robot-dev-ai`
- Branch: `docs/g0-cross-os-sync`
- Marker: `g0-windows-probe-2026-09-17`
- Confirmed Ubuntu marker `g0-ubuntu-probe-2026-09-17` after `git pull --ff-only`
```

Do not edit `docs/environment.md`.

## Commit and push

```powershell
git add docs/progress.md
git commit -m "docs: record Windows Gate 0 pull"
git push
git status
```

`git status` should be clean. Then reboot or switch back to Ubuntu and continue the original Cursor chat there. Ubuntu will `git pull` and finish Gate 0.
