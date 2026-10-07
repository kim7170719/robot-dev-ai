# M14 GUI MVP architecture

Version: 0.5 (2026-10-07)

## Scope and boundary

M14 turns the verified G7–G12 core into a usable presentation layer. It
includes a typed Python API and a web GUI consuming that API. It excludes an
Isaac viewport, arbitrary shell execution, direct ROS control from the
browser, new robot morphologies, Cosmos installation, Jetson deployment, and
real hardware. A later M14 extension adds a **read-only telemetry view**: one
ROS camera image and current odometry are sampled through a fixed host helper.
It is not a viewport or a remote-control channel.

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
`GET /api/v1/simulation/frame` invokes only the fixed system-Python ROS
subscriber helper. It waits for one RGB8 `/camera/image_raw` sample and one
`/odom` sample, encodes the image as PNG, and returns it with x/y/yaw. Its
`source` query is a fixed literal: `isaac` maps to `/camera/image_raw` and
`webcam` maps to `/webcam/color/image_raw`; it never accepts an arbitrary ROS
topic, constructs no shell command, or publishes. It returns HTTP 503 when the
selected source cannot be observed.

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

The dashboard's Robot telemetry view draws the M4 room and robot marker from
the returned odometry and displays the returned camera image. The M4 script's
camera is a 64×48 synthetic RGB8 sensor whose current image is a diagnostic
colour field, not a photorealistic render or an Isaac viewport. This explicit
label prevents the GUI from overstating the visual fidelity of the simulation.

## Changelog

### 0.3 — 2026-10-07

- Added the Dashboard Sensor Workbench with a large camera stage, source
  selector, device metadata, live-refresh control, and odometry panel.
- Added the fixed `isaac` / `webcam` camera-source API selection boundary.

### 0.4 — 2026-10-07

- Simplified the five-view language to Overview, Design, Build, Run, and
  Diagnose; the landing view now prioritizes a three-step task flow.
- Applied a restrained, typography-first visual refinement using the existing
  M14-local token map: one clear next action, reduced card chrome, and a
  responsive mobile action layout.
- Rendered and reviewed the changed landing view at 1500px and 390px. No
  upstream wireframes or project-wide design system exist; this remains a
  scoped M14 presentation refinement, not a new design-system decision.

### 0.5 — 2026-10-07

- Rebuilt the M14 presentation as a precision product surface: a soft titanium
  canvas, ink controls, one signal-blue interaction state, and a dark runtime
  evidence stage. The five typed-API views and their safety semantics are
  unchanged.
- Added a keyboard skip link, visible focus treatment, responsive single-column
  controls, and decorative-icon cleanup. The product brief and reusable visual
  rules are captured in `PRODUCT.md` and `DESIGN.md`.
- Added purposeful motion to explain workspace changes, live sensor sampling,
  and newly received status evidence. `prefers-reduced-motion` keeps the same
  state information without spatial motion; no API behavior changed.
