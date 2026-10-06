# 0007: GUI accesses Robot Dev AI only through a typed API

Date: 2026-10-06

## Status

Accepted.

## Context

M14 needs to expose existing requirement, compatibility, generation, runtime,
validation, and repair evidence without duplicating their logic in a browser
or granting an unbounded shell surface. The roadmap requires a Python/FastAPI
API between the GUI and the core.

## Decision

Create a typed Robot Dev AI API as the sole presentation-to-core boundary.
The GUI and future CLI/IDE clients receive reviewable Pydantic response
schemas. Stateful or mutating actions remain explicitly constrained by the
existing collectors and repair policy; the first GUI does not embed Isaac Sim
or publish ROS commands.

## Alternatives

- Browser or desktop frontend directly imports core/ROS code: rejected because
  it bypasses reviewable API boundaries and cannot run safely off the ROS host.
- Expose an arbitrary shell console: rejected because it violates constrained
  execution and introduces an unreviewable control plane.

## Consequences

- API responses are versioned through Pydantic/OpenAPI schemas.
- API tests can exercise user-visible behavior without a browser or live ROS
  process.
- The initial API may report unavailable or not-tested runtime data; it must
  never fabricate live evidence.
