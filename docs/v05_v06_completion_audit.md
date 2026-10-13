# v0.5 / v0.6 completion audit

Updated: 2026-10-13. This is a status audit, not new validation evidence.

| Roadmap requirement | Current evidence | Status |
|---|---|---|
| v0.5 trusted source / lifecycle / read-only Registry GUI | `registry.v05`, typed API, M14 Registry surface, tests | Complete foundation |
| Auditable onboarding plan and persistence | transaction JSONL, chained audit JSONL, restart and tamper tests | Complete foundation |
| Verified local artifact boundary | allowlisted SHA-256, path/type/size checks, artifact-bound audit tests | Complete foundation |
| Dependency, ROS manifest, license metadata inspection | fixed no-network/read-only Docker commands; bounded parsing tests | Complete foundation |
| Docker sandbox self-test | existing local CUDA image self-test evidence | Complete for the fixed self-test only |
| Sandbox build execution | fixed, hash-bound no-network Docker build endpoint; audit retains image reference and output digest; no local image or approved candidate archive | Complete implementation; external validation remains |
| E2 evidence | no recorded isolated build of an approved archive | External prerequisite remains |
| External discovery, clone/download | no candidate source or human review authorization is present | External/human prerequisite remains |
| Promotion/deprecation CRUD | no persistent reviewer identity, reviewed diff, or observed build/hardware evidence exists | Human evidence prerequisite remains |
| v0.6 schema, query, snapshot, review queue | `registry.v06`, `EvidenceRegistry`, snapshot/API tests; pending reports excluded, accepted reports queryable, and E5 only arises from two independent accepted submitters | Complete foundation |
| M14B coverage/conflict/reference views | `/api/v1/evidence/overview`, Evidence Explorer, API tests | Complete foundation |
| Ten E0/E1 provenance records | current default document has one E3 record only | External evidence remains |
| Three E2 recorded sandbox builds | no local Jazzy build image or approved archives | External prerequisite remains |
| E3 differential-drive simulation evidence | existing `generic-diff-base-e3`, G12 virtual-MVP evidence | Complete historical evidence |
| E4 real-hardware record | M15 hardware unavailable | Hardware prerequisite remains |
| E5 reviewed community evidence | no independent reviewed submissions | Human/community prerequisite remains |

## Completion rule

The implementation foundations above are complete only within their stated
boundaries. The remaining rows require new authoritative observations or human
decisions; creating synthetic records, pulling unreviewed sources, or treating
simulation as hardware would violate the roadmap and AGENTS.md safety rules.

## 2026-10-13 verification checkpoint

The full local test suite passed after the trusted-source timestamp, snapshot,
and community-evidence hardening. The checked-out project worktree contains no
tracked uncommitted changes. The only local untracked path is `.agents/`, which
contains machine-local skills and is intentionally excluded from the project.
