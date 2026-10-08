# AI handoff (live)

Updated: 2026-10-07. Next editor should refresh this file after the next real task.

## Where we are

**G0–G12 and G14 PASS** on Ubuntu. M13/G13 is deferred as Optional Extension O1. Isaac Sim remains the physics authority.

G4 was merged into `develop` through PR [#10](https://github.com/kim7170719/robot-dev-ai/pull/10). Create a new feature branch for M5; do not develop directly on `develop`.

## Done

| Gate | What | Evidence |
|---|---|---|
| G0 | Repo, GitHub, dual-OS clone sync | tag `g0-environment-baseline` on `main` |
| G1 | ROS 2 Jazzy, own package, launch, topic/service/action | `docs/m1_g1.md` |
| G2 | `simple_diff_robot` URDF + ros2_control + RViz | `/cmd_vel` TwistStamped moves `/odom` |
| G3 | Isaac Sim 4.5 Docker, Humble↔Jazzy via CycloneDDS | `/cmd_vel` → `/odom`; tag `m3-g3-isaac-sim` |
| G4 | Nav2 + SLAM, host RViz goal, Isaac Sim goals | `experiments/raw/M4-G4.md` |
| G5 | Isaac ROS GPU image-pipeline baseline | `docs/isaac_ros_baseline.md`; `scripts/m5_image_proc_smoke.sh` |
| G6 | Proposal and MVP scope freeze | `docs/m6_proposal.md`; user accepted scope |
| G7 | Hardware capability drives template expansion | `registry/models.py`; registry + template tests |
| G8 | Structured spec produces a buildable ROS skeleton | `TemplateExpander`; generated `demo_diff_drive` passed Jazzy `colcon build` |
| G9 | Natural language produces a validated robot specification | Gemini Free Tier request → differential drive, LiDAR, RGB camera, Nav2, Isaac Sim spec |
| G10 | Structured rules resolve compatible packages or explicit blocks | 9 resolver tests: capability, Jazzy, platform, GPU support, message conversion, dependency |

Isaac Sim G4 CLI results (2026-09-21):

- `navigate_to_pose` `(1.0, 0.0)` SUCCEEDED (odom 3.09 → 0.96)
- `navigate_to_pose` `(2.0, 2.2)` around box at `(2.0, 1.0)` SUCCEEDED (odom 1.87, 2.25)

## Next

- M14 exposes the frozen core through a typed API. Workspace mutation and restricted build require separate explicit confirmations; M13 is Optional Extension O1: do not pull Cosmos models on this Turing 11 GB GPU; resume only on supported hardware with a measurable scenario-generation hypothesis.

## M5 evidence

- Reproducible image: `docker/Dockerfile.isaac-ros-image-proc`; local tag `robot-dev-ai/isaac-ros-image-proc:4.5`
- The project smoke-test script passed twice on 2026-10-01: official NGC 4.0.0 quickstart rosbag → `nvidia::isaac_ros::image_proc::ResizeNode` → `/resize/image` (`480×288`, `rgb8`)
- Host GPU is RTX 2080 Ti (Turing, compute capability 7.5). Isaac ROS 4.5 officially requires Ampere+ on x86_64, so G5 is a reproducible but unsupported-platform experimental result.

## Not done

- M12+ validation and orchestration agents
- Real-hardware / Jetson
- Isaac Sim RTX/PhysX LiDAR (synthetic 2D scan is the G4 path)
- Full URDF physics in Isaac Sim (crashes; G3/G4 use kinematic cube + raycast)
- Cosmos (forbidden as Isaac physics replacement; not before M13)

## Recently touched files (M12 in progress)

- `agent/requirement_agent/`, `agent/schemas/` — M9 parser, specification schema, provenance, ambiguity handling, Gemini adapter, and structured-output retry
- `agent/compatibility_resolver/`, `registry/models.py` — M10 rule resolver, target-platform constraints, interface dependencies, and conversion records
- `agent/auto_debug/` — M11 restricted build collection plus non-mutating diagnostics from build, node, topic, TF, and controller evidence
- `agent/mvp_pipeline/` — M12 deterministic prompt → registry resolution → template materialization → restricted build orchestration
- `agent/template_engine/` — deterministic registry-authorized expansion and safe output writing
- `templates/` — differential-drive, LiDAR, camera, Nav2, and Isaac ROS project fragments
- `tests/test_template_expander.py` — expansion, refusal, materialization, and fragment tests

M8 build evidence: temporary generated `demo_diff_drive` passed `colcon build --packages-select demo_diff_drive` on 2026-10-01.

M10 boundary: static rules distinguish validated, experimental, and blocked configurations. Build, ROS graph, Isaac Sim, Jetson, and real-hardware evidence remain M11+ responsibilities.

M11 live evidence: `ros2 node list` and `ros2 topic list -t` returned successfully; `ros2 control list_controllers` timed out at 10 seconds. The node snapshot contained only `/tm_smooth_controller`, so M11 diagnosed missing `/controller_manager`; no host process was mutated.

M11 build evidence: `colcon build --packages-select simple_diff_robot simple_diff_nav` exited 0 on 2026-10-01, and `AutoDebugAgent` classified its evidence as `build-succeeded`.

M11 runtime-snapshot evidence (2026-10-06): node and topic inspection completed; the snapshot parsed the active topic types. `ros2 control list_controllers` again timed out at 10 seconds, so controller state is empty and the timeout remains explicit evidence; no process or controller was changed.

M11 end-to-end snapshot diagnosis (2026-10-06): with `/controller_manager` required and `/joint_command` constrained to `sensor_msgs/msg/JointState`, live evidence produced `ros-command-timeout` and `missing-ros-node`. It did not infer an inactive controller from the failed controller query.

M11 TF snapshot evidence (2026-10-06): fixed one-shot `/tf` and `/tf_static` collection succeeded and parsed seven observed edges, including `world → base`. A required `map → odom` edge was correctly diagnosed as missing. The controller query independently timed out; failed collection is never interpreted as missing TF or controller state.

M11 restricted-build evidence (2026-10-06): `BuildCommandCollector` accepted only valid package names and ran `colcon build --packages-select simple_diff_robot simple_diff_nav` without a shell. The build exited 0 and was diagnosed as `build-succeeded`.

**Gate G11 PASS (2026-10-06):** all M11 checklist items have automated tests and/or live evidence. Patch application remains intentionally manual and non-mutating.

M12 pre-build evidence (2026-10-06): the differential-drive + Nav2 request generated an isolated temporary workspace, selected `diff-drive-controller` and `nav2-bringup`, and passed restricted `colcon build --packages-select mvp_diff_drive` with `build-succeeded`. The frozen Chinese NVIDIA differential-drive + LiDAR + Camera + navigation request now resolves four capabilities and renders all four templates.

M12 generated-runtime evidence (2026-10-06): corrected generated `mvp_diff_drive` package-share launch completed a clean rerun with no config-path warning. Its non-controlling `/cmd_vel` observer published count `3` during fixed `(1.0, 0.0)` validation, and Nav2 returned `SUCCEEDED`.

M12 automatic-repair evidence (2026-10-06): `ConstrainedRepairer` verified an M11 `package.xml` dependency proposal against the current temporary generated manifest, applied it only under that workspace's `src/`, and rebuilt `mvp_diff_drive` successfully. It rejects other repair types and paths outside `src/`.

M12 virtual-camera evidence (2026-10-06): isolated G4 Isaac Sim was restarted with `m4_lidar_scan.py` publishing RGB8 `/camera/image_raw` (64×48) and `/camera/camera_info`, both with `camera_link`. Host inspection received both message types; `base_link → camera_link` reported translation `(0.150, 0.000, 0.020)`. The fixed `m4-navigation` validator again returned `SUCCEEDED` after the camera addition.

M13 preflight evidence (2026-10-06): local inspection found RTX 2080 Ti (Turing, compute capability 7.5, 11,264 MiB), Docker 29.8.1, NVIDIA runtime, and 347 GB free disk. Current official Cosmos Predict prerequisites require Ampere-or-newer GPUs, so no image, model, Conda environment, or system-Python change was attempted. Scope and isolated-container plan: `docs/m13_cosmos.md`.

M14 first API evidence (2026-10-06): FastAPI provides `GET /api/v1/project/summary` for frozen-MVP metadata and `POST /api/v1/requirements/parse` for the existing Requirement Agent's typed result. Both endpoints are in-process/read-only and do not invoke ROS or a shell. API tests plus the full suite pass: 51 tests.
M14 compatibility evidence (2026-10-06): `POST /api/v1/compatibility/resolve` accepts an explicit validated registry and deployment context and returns the existing resolver result. Project summary now reads Git HEAD without a Git shell invocation. Full suite: 52 tests.
M14 template-preview evidence (2026-10-06): `POST /api/v1/templates/preview` renders registry-authorized templates in memory and returns the typed file map; it does not write a workspace or invoke ROS. Full suite: 53 tests.
M14 workspace evidence (2026-10-06): `POST /api/v1/workspaces/plan` returns preview files and a confirmation ID without writing. `POST /api/v1/workspaces/apply` requires that ID plus `confirmed=true`, then writes only below the configured workspace root. Full suite: 54 tests.

M14 workspace-build evidence (2026-10-06): generated packages are restricted to `<workspace>/src/<ros_package_name>`. `POST /api/v1/workspaces/build` accepts only the confirmation ID of an already generated package plus a third `confirmed=true`, then runs the existing `colcon build --packages-select <package>` collector in the configured workspace and returns its typed diagnosis. Full suite: 55 tests.

M14 runtime-snapshot evidence (2026-10-07): `GET /api/v1/runtime/snapshot` returns the existing fixed read-only ROS inspection snapshot: nodes, topic types, controller states, TF edges, and raw command evidence. It neither starts ROS nodes nor publishes messages. Full suite: 56 tests.

M14 GUI / G14 evidence (2026-10-07): fixed virtual navigation validation and repair-proposal endpoints are typed and bounded; the former requires explicit confirmation and the latter returns a diff without writing. The same-origin, build-less GUI exposes Dashboard, Requirement, Robot Configuration, Runtime, and Validation/Experience views. Local HTTP smoke exercised GUI delivery, project summary, requirement parsing, and a non-mutating repair proposal; no runtime collection or navigation goal was issued. Full suite: 59 tests. Demo: `docs/m14_demo.md`.

M14 GUI visual pass (2026-10-07): the initial functional page was replaced by a responsive control-room UI with a guided-workflow sidebar, dashboard status cards, per-step evidence panels, confirmation messaging, keyboard focus styles, and reduced-motion support. Local Chrome renders were visually inspected at 1440px and 390px; the mobile card layout is single-column. The template preview now supplies the complete differential-drive values and template errors normalize to typed 422 JSON rather than HTML 500 responses. Full suite: 60 tests.

M14 precision-surface redesign (2026-10-07): the same five typed-API views now use a restrained product interface—soft titanium canvas, ink typography, signal-blue activation, and dark simulation evidence only. `PRODUCT.md` and `DESIGN.md` preserve the product/design contract. A skip link, visible focus states, and narrow-screen single-column actions are in place. This is presentation-only: browser ROS/shell access, confirmations, fixed camera sources, and all API contracts remain unchanged. Full suite: 64 tests.

M14 motion/navigation pass (2026-10-07): the GUI uses bounded CSS/View Transition motion to preserve continuity when an operator changes workspace, acknowledge new runtime evidence, and denote active live-camera sampling. `prefers-reduced-motion` removes spatial motion while retaining state. Mobile/tablet navigation is a compact 3+2 stage grid rather than a horizontal scrolling rail. No API or ROS capability changed. Full suite: 64 tests.

M14 animated entry surface (2026-10-07): `/` now opens an immersive, local SVG robot-startup scene before the workspace. The robot's LiDAR sweep, camera response, and signal paths are one bounded readiness animation; “進入工作區” opens Overview and “直接建立方案” opens Design. The app now safely handles an empty URL hash rather than generating an invalid selector. Explicit workspace hash links work as before. This remains presentation-only; full suite: 64 tests.

M14 top-nav/i18n pass (2026-10-07): the permanent left rail was replaced by a five-stage top navigation. A local Chinese/English preference covers the entry surface, stage labels, and primary Overview copy; ROS/API technical evidence remains unmodified. On narrow screens the top bar is fixed and direct `#dashboard` links position the title below it. This remains presentation-only; full suite: 64 tests.

M14 plain-language pass (2026-10-08): primary operator copy now says what the user can do—plan, review, check, or get help—rather than exposing AI implementation words. ROS/API evidence remains literal in the technical detail surfaces. Simulation status uses plain outcomes (normal, partially readable, unavailable). No backend or safety boundary changed; full suite: 64 tests.

M14 humanoid/control pass (2026-10-08): root landing now presents a local SVG humanoid with eight named readiness poses. Its timer runs only while the landing view is active and reduced-motion leaves it static. Overview adopts the landing's deep-ink, cool-blue control surface; task views remain bright. No API, ROS, or safety behavior changed; full suite: 64 tests.

M14 3D humanoid refinement (2026-10-08): the provisional SVG landing robot was replaced with one locally served original 3D product render. Its continuous 7.2-second idle animation communicates a weight shift and bounded visor scan without cycling static images; it runs only while `/` is visible, pauses in a hidden tab, and retains boot for reduced motion. This is visual art only—not an Isaac viewport, a physical robot, or a backend capability change. Local HTTP checks returned the image with `200 image/png`; desktop and 390px mobile Chrome renders were reviewed; full suite: 64 tests.

M14 rigged WebGL humanoid (2026-10-08): landing now uses a local Three.js canvas and a rigged glTF humanoid, with 580ms cross-fades among idle, acknowledgement, wave, thumbs-up, walking, and jump clips. It no longer presents a rotated set of static images; the prior PNG remains only if WebGL cannot start. The animation stops off landing, in hidden tabs, and for reduced motion. Three.js/model attribution is in `docs/THIRD_PARTY_NOTICES.md`. Local WebGL was rendered and inspected at 1500px and 390px; full suite: 64 tests.

M14 original procedural humanoid (2026-10-08): the landing scene no longer loads a third-party robot or GLTF helpers. `gui/hero-robot.js` builds the original white-ceramic/graphite/cyan-visor character entirely from native Three.js geometry and continuously damps six presentation states: ready, scan, wave, acknowledgement, mobility, and stance. The local PNG remains only as a WebGL failure fallback; hidden-tab, off-landing, and reduced-motion safeguards are unchanged. Desktop and 390px mobile renders were reviewed. Only the local MIT-licensed Three.js runtime remains third-party; no API, ROS, Isaac, or hardware behavior changed.

M14 Full Run evidence (2026-10-07): `POST /api/v1/mvp/full-run` requires explicit confirmation and composes the frozen M12 parser, resolver, template generation, restricted build, and runtime snapshot in a temporary workspace that is removed before returning. A real run of the frozen Chinese four-capability request returned `build-succeeded`, then observed 25 nodes, 80 topics, and 3 TF edges. One `/tf_static --once` command timed out; the dashboard reports the simulation as Partial rather than healthy. `scripts/run_m14_demo.sh` sources ROS Jazzy and `ros_ws/install` before starting uvicorn. Full suite: 61 tests.

M14 simulation-telemetry evidence (2026-10-07): `GET /api/v1/simulation/frame` uses a fixed system-Python ROS subscriber helper to return one `/camera/image_raw` RGB8 PNG and `/odom` pose; it publishes nothing. With the pinned Isaac 4.5 G4 container running, host ROS observed one publisher on each of `/camera/image_raw`, `/odom`, and `/scan`; the endpoint returned a valid 64×48 PNG. A bounded virtual velocity test moved odometry from origin to `x=0.350 m`, `y=0.080 m`, `yaw=0.452 rad`, which the dashboard's top-down marker can render. The camera remains the M4 synthetic diagnostic colour field, not an Isaac viewport. Full suite: 63 tests.

M14 GUI presentation refinement (2026-10-07): the same five typed-API views now present as Overview, Design, Build, Run, and Diagnose. The landing page makes Design Plan the clear first action and reduces the visible workflow to plan → review/generate → run in simulation. The local M14 token map received a restrained typography-first polish; desktop (1500px) and mobile (390px) Chrome renders were reviewed. The mobile action layout is stacked and no longer causes page-level horizontal overflow. No API, ROS, build, or safety behavior changed. Full suite: 64 tests with `.venv/bin/python -m pytest -q`.

M14 Sensor Workbench extension (2026-10-07): Dashboard camera observation is now a full-width workbench with fixed source selection: `isaac` maps to `/camera/image_raw`; `webcam` maps to the pending D455 `/webcam/color/image_raw`. The typed API refuses unavailable sources with 503 and accepts no arbitrary topic. The D455 USB device is visible as RealSense D455 V4L2 nodes but its Jazzy driver awaits privileged package installation. Full suite: 63 tests.

M4 navigation runtime recovery (2026-10-07): a long-lived stale Nav2 launch lacked `/bt_navigator`; its remaining lifecycle manager conflicted with a new Nav2 instance's DDS services, so initial bringup aborted at `controller_server/get_state`. Isaac `/scan`, `/odom`, `/map`, TF and `map → base_link` were healthy. After terminating the verified old Nav2 process tree and starting exactly one new `nav2_launch.py`, `/controller_server`, `/planner_server`, and `/bt_navigator` each reported `active [3]`; the fixed `(1.0, 0.0)` virtual `NavigateToPose` goal returned `SUCCEEDED`.

AI-assisted Design first slice (2026-10-07): `POST /api/v1/design/plan` produces an in-memory, registry-bounded plan (structured requirements, compatibility selection, template previews) with no workspace write or build. The GUI Design workspace renders capabilities, validated packages, and template previews. The existing `StructuredOutputProvider` remains the only future local/external model seam; no provider key is stored or activated. Full suite: 64 tests.

M12 exact-workspace evidence (2026-10-06): a fresh temporary workspace generated from the exact frozen Chinese request selected all four packages, rendered differential-drive, LiDAR, Camera, and Nav2 templates, and passed restricted `colcon build --packages-select mvp_diff_drive`. That same generated workspace then launched its observer in the isolated G4 stack. During the fixed validator goal it received `/cmd_vel` count `1411`; the validator returned `SUCCEEDED`.

**Gate G12 PASS (2026-10-06):** M12 has reproducible virtual-only evidence for parsing, structured spec, registry lookup, compatibility, template/workspace generation, restricted build, generated launch, isolated Isaac Sim start, ROS graph/topic inspection, TF validation, navigation PASS/FAIL, and constrained repair. No physical robot was commanded or required.

## Known issues / debt

- **Humble CycloneDDS ↔ Jazzy**: `/clock` publisher type hash can show `INVALID`; wall-clock stamps + `use_sim_time:=false` is the working G4 pattern
- **`/cmd_vel` types**: ros2_control (host G2) wants **TwistStamped**; Nav2 Jazzy collision_monitor publishes **Twist**. Isaac G4 script subscribes to Twist
- **collision_monitor** must use `base_link` (not TurtleBot `base_footprint`) or it zeros `/cmd_vel`
- **Kit `--exec`**: container must use `--entrypoint /isaac-sim/kit/kit` or the script never runs
- Keep `UPDATE_SUB` (or equivalent) so the Kit update callback is not garbage-collected
- Isaac `m4_lidar_scan.py` and `room_scan.py` must stay geometrically in sync (8×6 m room, box at 2,1)
- `docs/environment.md` is aligned with the verified 580.178.04 driver (ADR 0003)
- G4 `cmd_vel` timeout (0.5 s) is in the script on disk; running containers may be older

## Environment (Ubuntu)

| Item | Value |
|---|---|
| OS | Ubuntu 24.04 LTS |
| GPU | RTX 2080 Ti 11 GB |
| Driver for Isaac | 580.178.04 (not 595) |
| ROS | Jazzy at `/opt/ros/jazzy` |
| Isaac Sim | Docker `nvcr.io/nvidia/isaac-sim:4.5.0`, Humble rclpy inside |
| DDS | `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` + unicast peer `127.0.0.1` both sides |
| RViz | `__GL_THREADED_OPTIMIZATIONS=0` |

FastDDS Humble 2.x ↔ Jazzy 3.x is one-way; do not go back to FastDDS for host↔container.

## Windows / Ubuntu

- Two clones; GitHub only sync. No shared working tree
- Windows: docs/Git only. Do not install ROS / Isaac / Nav2 / Cosmos
- Before reboot: commit, push, update `docs/os_handoff.md`
- After reboot: open the GitHub `os_handoff.md` URL, not the previous chat

## Git

| Field | Value |
|---|---|
| Branch | `feature/gui-mvp` (from merged `develop`) |
| `develop` | `2d39098` — M12 freeze merged |
| `main` | `c771bf1` — do not develop here |
| Working tree | M14 changes belong on `feature/gui-mvp`; generated status DOCX is intentionally ignored |

## Suggested next step

1. Review PR #13 into `develop`; then begin M15 planning only after selecting the target Jetson and real differential-drive hardware.
2. For Ubuntu interactive simulation, start the pinned G4 container with `bash scripts/start_m4_isaac_sim.sh`, then start the GUI with `bash scripts/run_m14_demo.sh`. The Dashboard telemetry panel is read-only and requires `/odom` plus `/camera/image_raw` publishers.
M12 simulation-validator evidence (2026-10-06): isolated G4 Isaac Sim, SLAM, and Nav2 were started; `/controller_server`, `/planner_server`, and `/bt_navigator` reached `active [3]`. The fixed `m4-navigation` validator sent the `(1.0, 0.0)` map goal and received `SUCCEEDED`. The Isaac container and host launch processes remain running for interactive testing.
