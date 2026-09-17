# Run in C:\dev\robot-dev-ai after clone.
# This chat cannot be shared with Windows; the script is the handoff.

$ErrorActionPreference = "Stop"
Set-Location "C:\dev\robot-dev-ai"

git fetch --prune
git switch docs/g0-cross-os-sync
git pull --ff-only
git status

$probe = Select-String -Path "docs\environment.md" -Pattern "g0-ubuntu-probe-2026-09-17"
if (-not $probe) {
    throw "Ubuntu probe marker not found. Stop and do not commit."
}

Write-Host "Ubuntu probe found. Next: edit only docs/progress.md using docs/g0_windows_handoff.md"
Write-Host "Then:"
Write-Host '  git add docs/progress.md'
Write-Host '  git commit -m "docs: record Windows Gate 0 pull"'
Write-Host '  git push'
