# ADR 0010: Start v0.5 with trusted-source metadata and read-only management

**Status:** Accepted; implementation boundary amended (2026-10-13)

## Context

The v0.5 roadmap asks the GUI to manage component sources, licenses,
compatibility claims, lifecycle, discovery, sandbox validation, and promotion.
At the time of the original decision, the project had no audit-backed
acquisition transaction or sandbox executor. It now has append-only
transactions and a fixed, hash-bound local-bundle inspection/build path, but
still has no authorized external discovery or acquisition workflow. Exposing
CRUD or discovery that appears to install a package would overstate what the
Core can safely do.

## Decision

Begin v0.5 with validated source metadata, a deterministic source-review
policy, and read-only Registry Management API/GUI views. A BLOCKED source is
never eligible for acquisition. An allowed source is still sandbox-only and
requires future human approval before promotion or deployment.

The only execution exception is the fixed Docker build path for an already
operator-approved local archive, after authorization plus artifact-bound scan,
ROS manifest, and license metadata gates. It is no-network, non-root,
read-only at the container root, and records an audit event only. It does not
download, promote, or create E2 evidence automatically.

## Consequences

The GUI can inspect and filter truthful registry facts and preview a safe plan,
but cannot add, edit, fetch, install, promote, or execute external components.
The API's constrained local-bundle build is not exposed as a Registry GUI
action and remains dependent on explicit human authorization. External
discovery, identity-backed review, promotion, and real-hardware validation
remain deferred. This preserves the v0.4 mutation-safety boundary and avoids
misrepresenting virtual evidence as real-hardware verification.
