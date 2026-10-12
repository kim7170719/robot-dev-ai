# ADR 0010: Start v0.5 with trusted-source metadata and read-only management

**Status:** Accepted (2026-10-12)

## Context

The v0.5 roadmap asks the GUI to manage component sources, licenses,
compatibility claims, lifecycle, discovery, sandbox validation, and promotion.
The project has no audit-backed acquisition transaction or sandbox executor
yet. Exposing CRUD or a discovery action that appears to install a package
would make the GUI overstate what the Core can safely do.

## Decision

Begin v0.5 with validated source metadata, a deterministic source-review
policy, and read-only Registry Management API/GUI views. A BLOCKED source is
never eligible for acquisition. An allowed source is still sandbox-only and
requires future human approval before promotion or deployment.

## Consequences

The initial GUI can inspect and filter truthful registry facts but cannot add,
edit, fetch, install, build, validate, or promote external components. Those
operations remain deferred until an audited transaction and sandbox contract
are implemented. This preserves the v0.4 mutation-safety boundary and avoids
misrepresenting virtual evidence as real-hardware verification.
