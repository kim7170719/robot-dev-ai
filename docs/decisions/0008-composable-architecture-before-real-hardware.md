# 0008: Complete composable architecture core refactor before real-hardware execution

Date: 2026-10-12

## Status

Accepted — user-supplied roadmap v0.4.

## Context

G0–G12 prove a virtual differential-drive MVP using known registry entries and
templates. M14 is a completed typed-API presentation layer. The next physical
target includes Jetson, a differential-drive base, D455, and potentially
non-ROS controller/MCU hardware, but exact controller, transport, firmware,
encoder, LiDAR, and power facts are not yet evidenced.

Proceeding directly to M15 would make every integration exception a local,
hardware-specific special case. The system needs first-class architecture,
capability, composition, adapter, readiness, safety, and evidence concepts to
generalize safely.

## Decision

Insert G12.5 as an architecture-aware, composable core refactor before further
M15 real-hardware execution. Preserve historical G0–G12/G14 evidence and the
M14 GUI, but pause M15 preflight until G12.5 passes. Make all v0.4 state
explicit: verified, experimental, unknown, blocked, unsupported, degraded, and
not tested are not interchangeable.

## Alternatives considered

1. Continue M15 immediately with device-specific scripts. Rejected because it
   cannot prove generalization or safely represent missing hardware facts.
2. Rewrite the M14 GUI first. Rejected because UI schema would be coupled to
   an unstable core model and create rework.
3. Build a universal multi-robot framework now. Rejected because it expands
   beyond the differential-drive reference and lacks evidence.

## Consequences

- New G12.5 work is schema/migration → resolver → registry → composition →
  generation/adapters → readiness/safety → tests/API freeze.
- Existing M15 documentation remains useful input for readiness/safety but is
  not G15 proof.
- New implementation belongs on `refactor/composable-architecture-v0.4` until
  G12.5 is ready to merge into `develop`.
