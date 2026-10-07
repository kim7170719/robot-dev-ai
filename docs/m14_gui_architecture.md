# M14 GUI MVP architecture

Version: 0.2 (2026-10-07)

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
`POST /api/v1/templates/preview` uses the same explicit-registry pattern to
render files in memory only; it does not call the expander write operation.
`POST /api/v1/workspaces/plan` returns a one-time confirmation ID and file
map without writing. Only `POST /api/v1/workspaces/apply` with that ID and
`confirmed=true` writes a ROS-valid package below the API-configured
`<workspace>/src/` root. `POST /api/v1/workspaces/build` requires a third
`confirmed=true` and the ID of an already generated plan. It invokes only the
existing restricted `colcon build --packages-select <package>` collector in
that configured workspace and returns its typed diagnosis; it never repairs
or executes arbitrary commands.
`GET /api/v1/runtime/snapshot` exposes the existing fixed, read-only ROS
inspection set: nodes, topic types, controller states, and TF edges together
with the raw command evidence. It starts no nodes and publishes no messages.
`POST /api/v1/mvp/full-run` composes the frozen M12 pipeline in a temporary
workspace. It requires explicit confirmation, uses the fixed four-capability
registry and existing restricted build collector, removes generated files
before returning, and includes runtime evidence. Fixed simulation validation
is opt-in in the same confirmed request.

The first GUI views are Dashboard, Requirement, Robot Configuration, Runtime,
and Validation/Experience. View implementation is downstream of the API
contract and does not add a new robotics capability.

## Failure and safety semantics

| Boundary | Failure behavior |
|---|---|
| GUI → API | typed client error; no implicit retry of mutations |
| API → core | validation error returned as structured evidence |
| API → workspace build | only a generated, ROS-valid package selected from an explicit confirmation ID; build failure remains diagnosis evidence |
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

The implemented GUI is a same-origin, build-less ES-module application served
by FastAPI. Its five views consume only `/api/v1/*`; it has no browser-side ROS
or shell integration. The GUI renders JSON evidence as text, so command output
and generated diffs are not interpreted as HTML.

The v0.2 presentation layer uses a responsive control-room shell: a guided
workflow sidebar, dashboard status cards, focused per-step screens, explicit
confirmation messaging, and evidence panels. It was rendered and visually
reviewed at 1440px and 390px widths; mobile uses a single-column evidence-card
layout. There was no pre-existing design-system or wireframe artifact, so the
small CSS token map in `gui/index.css` is a M14-local visual foundation rather
than a project-wide design-system decision.

The dashboard uses a conventional latest-run layout: a Full Run CTA, pipeline
timeline, build status, and a three-state simulation-health summary (Online,
Partial, Unavailable). `scripts/run_m14_demo.sh` sources Jazzy and the
repository workspace before starting uvicorn, so an API service without `ros2`
on `PATH` is not confused with a simulation failure.
