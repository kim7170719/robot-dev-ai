#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git status
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Dirty tree. Commit and push before reboot."
  exit 1
fi
git rev-parse --abbrev-ref '@{u}' >/dev/null
ahead="$(git rev-list --count '@{u}..HEAD')"
if [[ "${ahead}" -gt 0 ]]; then
  echo "Unpushed commits. git push before reboot."
  exit 1
fi
echo "Clean. Reboot is OK. Other OS: open docs/os_handoff.md on GitHub."
