# Run in C:\dev\robot-dev-ai after reboot from Ubuntu.
$ErrorActionPreference = "Stop"
Set-Location "C:\dev\robot-dev-ai"
git fetch --prune
git switch develop
git pull --ff-only
git status
Write-Host "---- docs/os_handoff.md ----"
Get-Content "docs\os_handoff.md" -TotalCount 80
Write-Host "Browser copy: https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/os_handoff.md"
