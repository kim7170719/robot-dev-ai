# Run in C:\dev\robot-dev-ai before rebooting to Ubuntu.
$ErrorActionPreference = "Stop"
Set-Location "C:\dev\robot-dev-ai"
git status
$dirty = git status --porcelain
if ($dirty) {
    throw "Dirty tree. Commit and push before reboot."
}
git rev-parse --abbrev-ref --symbolic-full-name "@{u}" | Out-Null
$ahead = git log --oneline "@{u}..HEAD"
if ($ahead) {
    throw "Unpushed commits. git push before reboot."
}
Write-Host "Clean. Reboot is OK. Other OS: open docs/os_handoff.md on GitHub."
