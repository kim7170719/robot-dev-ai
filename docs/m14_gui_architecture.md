# M14 GUI MVP architecture

Version: 0.1 (2026-10-06)

## Scope and boundary

M14 turns the verified G7–G12 core into a usable presentation layer. It
includes a typed Python API and a web GUI consuming that API. It excludes an
Isaac viewport, arbitrary shell execution, direct ROS control from the
browser, new robot morphologies, Cosmos installation, Jetson deployment, and
real hardware.

Actors are an operator using the GUI, the API process on the Ubuntu host, and
the existing ROS/Isaac runtime. The browser never owns a ROS or Docker
credential. Cosmos O1 is an absent-by-default external extension.

## Topology

```text
Web GUI / future CLI
        │ HTTPS or local HTTP; typed JSON
        ▼
Robot Dev AI API (FastAPI)
        │ in-process typed calls; no shell construction
        ▼
Requirement | Resolver | Templates | Auto Debug | Validator
        │
        ├── Registry / generated workspace
        └── allowlisted ROS collectors ──► ROS 2 / Isaac Sim

Optional O1 Cosmos ──► reviewable scenario proposal only
```

The API owns request validation and response shaping. Each core component
retains one responsibility: Requirement Agent parses natural language;
Compatibility Resolver chooses or blocks packages; Template Engine generates
authorized files; Auto Debug collects/diagnoses constrained evidence; the
validator reports fixed-scenario results. Isaac Sim remains the physics
authority.

## First response surfaces

The first API schema set represents project summary, requirement result,
compatibility resolution, build result, runtime snapshot, validation result,
and repair proposal. It reports `not-tested` or `unavailable` when evidence
does not exist; it never invents runtime state.
The first implemented paths are `GET /api/v1/project/summary` and
`POST /api/v1/requirements/parse`; both are in-process, typed, and do not
invoke ROS or a shell.
The next path, `POST /api/v1/compatibility/resolve`, accepts an explicit
registry and deployment request, then returns the existing resolver result.

The first GUI views are Dashboard, Requirement, Robot Configuration, Runtime,
and Validation/Experience. View implementation is downstream of the API
contract and does not add a new robotics capability.

## Failure and safety semantics

| Boundary | Failure behavior |
|---|---|
| GUI → API | typed client error; no implicit retry of mutations |
| API → core | validation error returned as structured evidence |
| API → ROS collector | collector timeout/failure is surfaced, never interpreted as absence |
| API → repair | proposal only until the established constrained-repair policy authorizes the exact workspace action |
| API → O1 Cosmos | explicit unavailable result; all G12 paths remain usable |

## Quality realization

- **Safety:** no arbitrary shell endpoint and no browser ROS command publishing.
- **Traceability:** responses preserve command/build/diagnosis evidence from
  existing core types.
- **Compatibility:** Pydantic response models generate OpenAPI schema and
  filter undeclared output fields.
- **Operability:** API exposes project, branch, environment, and test/gate
  summary before live runtime actions.

## Decision index

| ADR | Decision |
|---|---|
| [0006](decisions/0006-cosmos-optional-extension.md) | Cosmos is O1 and cannot block M14 |
| [0007](decisions/0007-gui-through-typed-api.md) | GUI uses a typed API only |

## Downstream work

The next technical slice defines and tests the initial API response schemas
and a read-only project-summary endpoint. A frontend technology is deliberately
not selected until the API contract is proven.
The next technical slice adds template/workspace-generation evidence to the
typed API. A frontend technology is deliberately not selected until the API
contract is proven.
