# ADR 0009: Add a scalable evidence registry after the composable core

**Status:** Accepted (2026-10-12)

## Context

The project cannot physically validate every robot, sensor, controller, and
environment combination. A single verified/unsupported flag would either hide
useful documented knowledge or overstate untested hardware support. The
user-supplied v0.6 roadmap introduces E0–E5 evidence levels, source trust,
coverage, conflict retention, and immutable benchmark snapshots.

## Decision

Complete the currently active G12.5 composable core before starting G12.6.
G12.6 will store evidence level separately from source trust and preserve
environment-specific evidence. It will not promote E4/E5 without complete,
reviewed evidence. G12.6 precedes registry-management GUI work and M15 claims.

## Alternatives

1. Mark documented components as verified. Rejected: it creates false real-world
   confidence.
2. Require real-hardware testing for every component. Rejected: it is not
   feasible for the research constraints and discards useful lower-level evidence.
3. Start G12.6 immediately. Rejected: G12.5 owns the stable architecture,
   composition, adapter, readiness, and mutation seams that evidence must
   describe.

## Consequences

The registry will grow more slowly because provenance and context are required,
but it can scale without concealing uncertainty. Existing evidence stays valid
as historical records and is migrated without fabricated levels. API/GUI schema
changes remain deferred until the G12.5 core contract is frozen.
