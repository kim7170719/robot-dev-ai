# Git workflow

Source of truth: `CURSOR_PROJECT_GUIDE.md` section 13.

## Identity

- GitHub owner: `kim7170719`
- Intended repository: `kim7170719/robot-dev-ai`
- Expected SSH remote: `git@github.com:kim7170719/robot-dev-ai.git`
- Suggested `user.name`: `余建樂kim`
- `user.email` must be a verified GitHub email or GitHub noreply email. Do not hardcode a private email in this repo.

Ubuntu and Windows each set Git identity and authentication locally. Do not copy private keys between OS installs.

## Clones

```text
Ubuntu:  ~/dev/robot-dev-ai
Windows: C:\dev\robot-dev-ai
                     │
                     └── GitHub origin as the only sync hub
```

Do not share one working tree across Windows and Ubuntu.

## Branches

```text
main
└── develop
    ├── feature/*
    ├── fix/*
    ├── experiment/*
    └── docs/*
```

Never develop on `main`. Never force-push `main` or `develop`. OS names are not branch names.

## Dual-boot switch (reboot is expected)

Cursor chats do not survive reboot. The live packet is `docs/os_handoff.md` on GitHub.

**Leaving this OS**

1. Update `docs/os_handoff.md` if the next OS needs new instructions.
2. `git status`
3. Commit if there is real work (`wip:` only if you must reboot mid-task)
4. `git push`
5. `scripts/before_reboot.sh` (Ubuntu) or `scripts/before_reboot.ps1` (Windows)
6. Reboot

**Arriving on the other OS**

1. Open the GitHub URL printed at the top of `docs/os_handoff.md`
2. `scripts/after_boot.sh` or `scripts/after_boot.ps1`, or the copy-paste commands in that file
3. `git status` must be clean before new edits

Do not use `git stash` to move work between OS clones.

## Commits

Conventional Commits. One logical change per commit. Update `docs/progress.md` in meaningful commits.

## Gate 0 Git acceptance

Round-trip on `docs/g0-cross-os-sync`:

1. Ubuntu pushed `g0-ubuntu-probe-2026-09-17` in `docs/environment.md`.
2. Windows pulled that branch, wrote `g0-windows-probe-2026-09-17` in `docs/progress.md`, pushed `5abfb65`.
3. Ubuntu `git pull --ff-only` received `5abfb65`. Working tree clean. Markdown stayed LF.

Clones remain independent: `/home/yu/dev/robot-dev-ai` and `C:\dev\robot-dev-ai`.
