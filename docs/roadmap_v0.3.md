# Roadmap v0.3 — 2026-10-06

This is the repository's execution baseline derived from the user-provided
v0.3 roadmap. It supersedes the post-M12 sequencing in
`CURSOR_PROJECT_GUIDE.md` without rewriting historical G0–G12 evidence.

## Main path

```text
G12 core freeze → M14 GUI MVP → M15 Jetson + real-robot bring-up
→ M16 sim-to-real experiments → M17 thesis freeze → M18 release
```

M13 Cosmos is **Optional Extension O1**: its preflight remains documented, G13
is deferred (not PASS), and it cannot block the main path.

## M14 boundary

The first GUI is a presentation layer over the Robot Dev AI API. It must
display Project, Requirement, Robot Configuration, Runtime, and
Validation/Experience views. It may not execute arbitrary shell commands,
control ROS directly, embed an Isaac viewport, or require Cosmos.

The API is the only GUI-to-core boundary. Existing Requirement Agent,
Compatibility Resolver, Template Engine, Auto Debug Agent, and simulator
validator stay authoritative; M14 composes rather than rewrites them.

## Evidence constraints

- G0–G12 are PASS with virtual-only evidence.
- M13 preflight is complete but G13 is deferred because the local RTX 2080 Ti
  is Turing with 11 GB VRAM and does not meet current Cosmos Predict hardware
  prerequisites.
- M14 must preserve the existing automated-test baseline and not claim real
  robot, Jetson, or full sensor-fidelity evidence.

## Milestone map

| Milestone | Focus | Gate |
|---|---|---|
| M13 | Cosmos preflight / optional extension | G13 deferred |
| M14 | GUI MVP over a typed API | G14 |
| M15 | Jetson + real robot bring-up | G15 |
| M16 | Sim-to-real + reproducible experiments | G16 |
| M17 | Thesis freeze | G17 |
| M18 | Open-source release + defense | G18 |
