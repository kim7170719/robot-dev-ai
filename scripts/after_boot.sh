#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch --prune
git switch develop
git pull --ff-only
git status
echo "---- docs/os_handoff.md ----"
sed -n '1,80p' docs/os_handoff.md
