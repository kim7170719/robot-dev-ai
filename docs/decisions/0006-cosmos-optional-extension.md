# 0006: Cosmos is an optional scenario-proposal extension

Date: 2026-10-06

## Status

Accepted.

## Context

G12 provides a complete virtual MVP. M13 preflight found that the local RTX
2080 Ti is Turing with 11 GB VRAM, while current Cosmos Predict prerequisites
require Ampere-or-newer hardware. Requiring Cosmos before productization would
block GUI, Jetson, real-robot, and experiment work without improving the
existing deterministic simulation validator.

## Decision

Move Cosmos to Optional Extension O1. Its only permitted role is to generate a
reviewable scenario proposal. Isaac Sim and, later, the real robot retain
authority for physics, ROS runtime, TF, navigation, and PASS/FAIL validation.
G13 is deferred, not passed. No Cosmos image, checkpoint, or special Python
environment is installed on the current host.

## Alternatives

- Keep Cosmos as a mandatory M13 gate: rejected because unsupported local
  hardware would block the main research path.
- Remove Cosmos entirely: rejected because supported hardware plus a
  measurable scenario-generation hypothesis may make it useful later.

## Consequences

- M14 can begin without Cosmos and must remain functional when O1 is absent.
- A future O1 restart requires supported hardware or remote runner, an explicit
  quantitative hypothesis, and a separate execution plan.
- `docs/m13_cosmos.md` remains the preflight and unblock record.
