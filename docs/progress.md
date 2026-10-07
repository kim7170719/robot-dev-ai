# Progress

## Week 00 Goal

Gate 0 environment audit and repository baseline on Ubuntu.

Acceptance criteria:

1. Ubuntu version, GPU, Python, and disk space are recorded in `docs/environment.md`.
2. Repository layout matches `CURSOR_PROJECT_GUIDE.md` section 3.
3. Cursor can read `CURSOR_PROJECT_GUIDE.md` and `.cursor/rules/robotics.mdc`.
4. GitHub `kim7170719/robot-dev-ai` exists, Ubuntu and Windows each have an independent clone, and round-trip sync works.

Out of scope:

- ROS 2 Jazzy install (M1)
- Isaac Sim / Isaac ROS / Cosmos
- GUI
- First robot package

## Current milestone

M0 Environment Audit. Gate G0 **PASS**. Tag `g0-environment-baseline` is on `main`.

Current work: **M14 GUI MVP complete (G14 PASS)**. G12 remains frozen and runnable without Cosmos; M13/G13 is deferred as Optional Extension O1. Windows remains a Git, Cursor, and documentation helper only.

## M8 Template Engine / Gate G8

| Criterion | Status | Evidence |
|---|---|---|
| Registry-authorized template selection | PASS | `TemplateExpander.expand()` rejects capabilities not declared by selected hardware |
| Differential-drive project skeleton | PASS | package metadata, Python node, resource marker, config, and launch template |
| Sensor/navigation/GPU fragments | PASS | LiDAR, camera, Nav2, and Isaac ROS image-processing templates expand deterministically |
| Generated ROS package builds | PASS | generated `demo_diff_drive` passed Jazzy `colcon build --packages-select demo_diff_drive` |

Automated test suite: `.venv/bin/pytest` → 61 passed (2026-10-07).

## M9 Requirement Agent / Gate G9

| Capability | Status | Evidence |
|---|---|---|
| Explicit requirement parsing | PASS | `RequirementAgent.parse()` recognizes MVP capability phrases |
| Structured specification and provenance | PASS | Pydantic `RobotSpecification` / `RequirementResult` |
| Ambiguity handling | PASS | unspecified capabilities produce a question rather than invented hardware |
| Provider validation and retry | PASS | injectable structured-output provider retries once after invalid output |
| Gemini Free Tier structured output | PASS | real `gemini-3.5-flash-lite` request returned registry-compatible MVP IDs |

## M10 Compatibility Resolver / Gate G10

| Capability | Status | Evidence |
|---|---|---|
| Capability and dependency reasoning | PASS | selects validated packages; blocks undeclared or unpackaged capabilities |
| ROS distro and target platform | PASS | requires a Jazzy driver and filters platform-restricted packages |
| Message type conversion | PASS | selects validated `Twist → TwistStamped` conversion package |
| Explainable output | PASS | returns selected package IDs and rule-derived issue strings |
| M9 → M10 integration | PASS | parsed differential-drive + Nav2 specification resolves to validated packages |
| GPU support classification | PASS | Turing Isaac ROS path is experimental only with M5 evidence; otherwise below-Ampere is blocked |

## M11 Auto Debug Agent / Gate G11

| Capability | Status | Evidence |
|---|---|---|
| Build and launch package diagnosis | PASS | detects CMake and `ros2 launch` missing-package evidence |
| Restricted build collection | PASS | only valid package names can form `colcon build --packages-select`; real selected-package build returned `build-succeeded` |
| Successful build classification | PASS | real `simple_diff_robot` + `simple_diff_nav` build exited 0 and returned `build-succeeded` |
| Topic/type validation | PASS | reports a `Twist` versus `TwistStamped` mismatch |
| TF validation | PASS | identifies a required but absent parent-to-child edge |
| Controller validation | PASS | identifies required controllers not in `active` state |
| Bounded repair policy | PASS | stops at the configured maximum and emits reviewable failure evidence |
| Read-only runtime collection | PASS | allowlisted node, topic, and controller commands return captured evidence |
| Runtime snapshot | PASS | one read-only collection returns parsed node, topic-type, controller-state, and per-command evidence |
| Runtime snapshot diagnosis | PASS | command failures, missing required nodes, topic-type mismatches, and inactive controllers are diagnosed from one snapshot; failed collection is not treated as absent state |
| TF runtime collection and diagnosis | PASS | parses fixed one-shot `/tf` and `/tf_static` observations; required edges are checked only when both collections succeed |
| Collector timeout diagnosis | PASS | live `ros2 control list_controllers` 10-second timeout is classified safely |
| Failure report | PASS | diagnosis includes command, exit code, evidence, repair budget, and null/no patch diff |
| Patch proposal | PASS | produces a reviewable, path-constrained `package.xml` dependency diff |
| Patch application | NOT IMPLEMENTED | recommendations are intentionally non-mutating |

**Gate G11: PASS (2026-10-06).** The M11 gate requires evidence-backed build and ROS diagnostics, bounded repair recommendations, reviewable diffs, and failure reports. Automated patch application is deliberately excluded from this gate.

## M12 MVP Freeze

| Capability | Status | Evidence |
|---|---|---|
| Prompt-to-build orchestration | PASS | `MvpPipeline.run()` parses a differential-drive + Nav2 request, resolves packages, renders templates, and materializes an isolated ROS workspace |
| Generated-project build | PASS | a temporary generated `mvp_diff_drive` workspace passed restricted `colcon build --packages-select mvp_diff_drive` |
| Frozen four-capability request | PASS | the exact Chinese NVIDIA differential-drive + LiDAR + Camera + navigation request resolves all four capabilities and materializes their templates |
| Generated-package runtime integration | PASS | corrected package-share launch rerun had no config-path warning; observer received Nav2 `/cmd_vel` count `3`, and fixed `(1.0, 0.0)` validator returned `SUCCEEDED` |
| Fixed simulation validator | PASS | `IsaacSimulationValidator.validate(m4-navigation)` maps the fixed G4 navigation goal outcome to explicit PASS/FAIL evidence without a shell |
| Live Isaac Sim PASS/FAIL | PASS | isolated G4 Isaac Sim + SLAM + Nav2 stack reached `(1.0, 0.0)`; fixed validator received `SUCCEEDED` |
| Virtual camera integration | PASS | G4 now publishes RGB8 `/camera/image_raw` and `/camera/camera_info` at `camera_link`; the existing `base_link → camera_link` TF was observed |
| Bounded automatic repair | PASS | verified `package.xml` dependency diff applied only in a temporary generated workspace; restricted rebuild returned `build-succeeded` |
| Exact generated workspace launch | PASS | the exact four-capability workspace launched in G4; its non-controlling observer received Nav2 `/cmd_vel` count `1411` while the fixed validator returned `SUCCEEDED` |

**Gate G12: PASS (2026-10-06).** The frozen request completed deterministic parsing, registry resolution, template/workspace generation, restricted build, generated-package launch, isolated Isaac Sim graph and TF validation, fixed navigation PASS/FAIL evidence, and one constrained reproducible repair. This gate covers virtual LiDAR and Camera only; no physical hardware was used.

## M13 Cosmos scenario generation (Optional Extension O1)

| Criterion | Status | Evidence |
|---|---|---|
| Scope choice | PASS | scenario generation selected; Isaac Sim remains the physics and validator authority |
| Independent environment plan | PASS | documented Docker-only isolation; no ROS or system-Python mutation |
| Official hardware preflight | DEFERRED | RTX 2080 Ti is Turing / 11 GB; current Cosmos Predict prerequisites require Ampere+ |
| Core MVP without Cosmos | PASS | G12 remains runnable and has no Cosmos dependency |

**Gate G13: DEFERRED.** See `docs/m13_cosmos.md` and ADR 0006; no model/container pull was attempted on unsupported hardware, and G13 no longer blocks the main roadmap.

## M14 GUI MVP (completed)

| Criterion | Status | Evidence |
|---|---|---|
| Roadmap re-baseline | PASS | `docs/roadmap_v0.3.md` moves Cosmos to Optional Extension O1 and makes GUI the main path |
| API / GUI safety boundary | PASS | ADR 0007 and `docs/m14_gui_architecture.md`: GUI reaches core only through a typed API; no arbitrary shell, direct ROS, or Isaac viewport |
| Project, requirement, compatibility, template preview, confirmed workspace generation, and restricted build API | PASS | Typed core behavior is exposed without ROS; generated ROS packages are confined to `<workspace>/src/`, and only an already generated package with a third `confirmed=true` can run `colcon build --packages-select`; typed diagnosis preserves build failures |
| Read-only runtime snapshot API | PASS | `GET /api/v1/runtime/snapshot` returns the existing allowlisted ROS node, topic-type, controller, and TF evidence; it does not start nodes or publish messages |
| Fixed simulation validation and repair-proposal APIs | PASS | The fixed `m4-navigation` scenario requires explicit confirmation; repair proposals return typed diffs without applying them |
| Full Run orchestration and live simulation health | PASS | Confirmed `POST /api/v1/mvp/full-run` uses the frozen M12 pipeline in an ephemeral workspace, then returns build and runtime evidence; dashboard distinguishes Online, Partial, and Unavailable runtime states |
| Five GUI views | PASS | Same-origin build-less GUI exposes Dashboard, Requirement, Robot Configuration, Runtime, and Validation/Experience through a responsive latest-run dashboard; `docs/m14_demo.md` records the local HTTP smoke and 1440px/390px visual review |

**Gate G14: PASS (2026-10-07).** The five-view GUI consumes the typed API only, preserves confirmation gates for workspace/build/virtual validation, and renders runtime, validation, and repair evidence without direct browser ROS, shell, Isaac viewport, Cosmos, Jetson, or physical-hardware access. Full suite: 61 tests; local HTTP demo passed. A verified Full Run parsed four capabilities, passed restricted build, cleaned its temporary workspace, and observed 25 nodes / 80 topics / 3 TF edges with a truthful Partial status for one timed-out TF inspection.

## Gate 0 checklist

| Criterion | Status | Evidence |
|---|---|---|
| Ubuntu 24.04 LTS | PASS | `lsb_release -a` → 24.04.4 LTS |
| `nvidia-smi` works | PASS | Driver 595.84, RTX 2080 Ti |
| GPU / VRAM / Driver recorded | PASS | `docs/environment.md` |
| RAM / disk recorded | PASS | 31 GiB RAM, 412G free on `/` |
| Git installed | PASS | 2.43.0 |
| Project directories | PASS | repo layout created |
| `.gitignore` / `.gitattributes` | PASS | repo root |
| Cursor rules | PASS | `.cursor/rules/robotics.mdc` |
| Guide in repo | PASS | `CURSOR_PROJECT_GUIDE.md` |
| Git identity on Ubuntu | PASS | local git identity present |
| GitHub SSH/HTTPS on Ubuntu | PASS | SSH as `kim7170719`; `gh` 2.99.0 |
| GitHub repo `kim7170719/robot-dev-ai` | PASS | https://github.com/kim7170719/robot-dev-ai |
| First commit / push | PASS | Ubuntu `main` + `develop` pushed |
| Windows independent clone | PASS | `C:\dev\robot-dev-ai`; marker `g0-windows-probe-2026-09-17` |
| Ubuntu → GitHub → Windows → GitHub → Ubuntu | PASS | Ubuntu `git pull --ff-only` `0c51e4f..5abfb65`; `docs/progress.md` is LF-only; `git status` clean |
| Milestone tag `g0-environment-baseline` | PASS | `main` `c771bf1`; `git fetch --tags` |

## This session

- Created `/home/yu/dev/robot-dev-ai` and moved `CURSOR_PROJECT_GUIDE.md` into it.
- Installed user-local `gh` 2.99.0; GitHub CLI logged in as `kim7170719`.
- Created public GitHub repo `kim7170719/robot-dev-ai` and pushed the Ubuntu clone.

## Gate 0 Windows probe

- Date: 2026-09-17
- Clone: `C:\dev\robot-dev-ai`
- Branch: `docs/g0-cross-os-sync`
- Marker: `g0-windows-probe-2026-09-17`
- Confirmed Ubuntu marker `g0-ubuntu-probe-2026-09-17` after `git pull --ff-only`

## Gate 0 Ubuntu return pull

- Date: 2026-09-17
- Clone: `/home/yu/dev/robot-dev-ai`
- Command: `git pull --ff-only` on `docs/g0-cross-os-sync`
- Windows commit: `5abfb65` `docs: record Windows Gate 0 pull`
- Line endings: `docs/progress.md` and `docs/environment.md` are LF-only; `git diff --check` clean

## Next (M1)

Issue M1-01: Install and verify ROS 2 Jazzy on Ubuntu 24.04. Commands in `docs/m1_ros_jazzy.md`. Do not start Cosmos.

| M1-01 check | Status | Evidence |
|---|---|---|
| `source /opt/ros/jazzy/setup.bash` | PASS | `/opt/ros/jazzy/setup.bash` |
| `ros2 --help` | PASS | `ROS_DISTRO=jazzy` |
| turtlesim | PASS | user GUI test of `turtlesim_node` / `turtle_teleop_key` |
| workspace `colcon build` | PASS | `colcon build --packages-select m1_baseline` |
| first own package | PASS | `ros_ws/src/m1_baseline` talker on `chatter` |

## Gate G1

| Criterion | Status | Evidence |
|---|---|---|
| Source ROS / workspace from clean terminal | PASS | `source /opt/ros/jazzy/setup.bash` then `source ros_ws/install/setup.bash` |
| Own package builds | PASS | `colcon build --packages-select m1_baseline` |
| Launch starts multiple nodes | PASS | `ros2 launch m1_baseline m1_graph.launch.py` → talker, listener, adder, fibonacci |
| CLI topic / node / service / action | PASS | `/chatter`; `/m1_talker` `/m1_listener` `/m1_adder` `/m1_fibonacci`; `/add_two_ints` sum=5; `/fibonacci` order 3 succeeded |

Commands: `docs/m1_g1.md`.

## M1 pipeline (after G1)

| Item | Status | Evidence |
|---|---|---|
| `sensor_node` → `planner_node` → `controller_node` | PASS | `ros2 launch m1_baseline m1_pipeline.launch.py` |
| Parameter | PASS | `ros2 param get /planner_node stop_distance` → 0.35 |
| TF2 `odom` → `base_link` | PASS | `ros2 run tf2_ros tf2_echo odom base_link` |
| RViz2 | NOT TESTED | GUI; `rviz2` not run in this session |

```bash
source /opt/ros/jazzy/setup.bash
cd ~/dev/robot-dev-ai/ros_ws
colcon build --packages-select m1_baseline
source install/setup.bash
ros2 launch m1_baseline m1_pipeline.launch.py
```

## M2 Gate G2

| Criterion | Status | Evidence |
|---|---|---|
| `simple_diff_robot` builds | PASS | `colcon build --packages-select simple_diff_robot` |
| Launch: `robot_state_publisher` + `diff_drive_controller` + `joint_state_broadcaster` | PASS | Both controllers `active` |
| `/cmd_vel` (`TwistStamped`) moves `/odom` | PASS | `odom.x` 0.006 → 8.102 while commanding 0.3 m/s |
| RViz: robot/TF display | PASS | `__GL_THREADED_OPTIMIZATIONS=0 rviz2`；OpenGL 4.6 NVIDIA 硬體加速；TF `base_link` 隨 `/cmd_vel` 移動 |

G2 is considered **PASS** for the ROS milestone. RViz environment fix is a separate task.

```bash
# Drive command (Jazzy uses TwistStamped):
ros2 topic pub -r 20 /cmd_vel geometry_msgs/msg/TwistStamped \
  "{header: {stamp: {sec: 0}}, twist: {linear: {x: 0.2}}}"
```

Full commands: `docs/m2_simple_diff_robot.md`.

## M4 Nav2 / Gate G4

| Item | Status | Evidence |
|---|---|---|
| Nav2 + SLAM Toolbox installed | PASS | `ros2 pkg list` → `nav2_bringup` `slam_toolbox` |
| Synthetic `/scan` (host) | PASS | `scan_sim.py`; 6 raycast tests; `/scan` `lidar_link` |
| Isaac Sim `/scan` `/odom` `/clock` | PASS | CycloneDDS; `/scan` ~10 Hz wall-clock stamps |
| `slam_toolbox` `map → odom` | PASS | with `use_isaac_sim:=true` |
| Nav2 lifecycle `active` | PASS | controller / planner / bt_navigator `active [3]` |
| Host RViz navigate-to-pose | PASS | user: 測試沒問題 |
| Isaac Sim navigate-to-pose | PASS | `navigate_to_pose` SUCCEEDED; odom 3.09 → 0.96 |
| Obstacle avoidance | PASS | goal (2.0, 2.2) around box at (2.0, 1.0); odom 1.87, 2.25 |
| Gate G4 | PASS | `experiments/raw/M4-G4.md` |

Commands: `docs/m4_nav2.md`. Decision: `docs/decisions/0004-synthetic-2d-lidar.md`.

## M14 simulation telemetry extension (2026-10-07)

| Item | Status | Evidence |
|---|---|---|
| Fixed camera/odometry API | PASS | `GET /api/v1/simulation/frame`; no request parameters and no ROS publication |
| Isaac camera, odometry, LiDAR publishers | PASS | one publisher each on `/camera/image_raw`, `/odom`, `/scan` |
| GUI telemetry view | PASS | dashboard renders returned odometry marker and ROS camera PNG |
| Motion proof | PASS | bounded virtual command yielded `x=0.350 m`, `y=0.080 m`, `yaw=0.452 rad` |
| Automated suite | PASS | `pytest -q` → 63 passed |

The M4 camera sample is a 64×48 synthetic RGB8 diagnostic colour field. It is
shown honestly as sensor evidence, not presented as an Isaac viewport or a
photorealistic vehicle view. Start the pinned container with
`bash scripts/start_m4_isaac_sim.sh` and the GUI with
`bash scripts/run_m14_demo.sh`.

M14 Sensor Workbench extension (2026-10-07): the Dashboard now separates
runtime health from a full-width camera workbench. It offers a fixed,
read-only source selector for Isaac `/camera/image_raw` and RealSense D455
`/webcam/color/image_raw`, a large RGB frame stage, per-source status/topic/
resolution metadata, live-refresh control, and odometry map. A selected source
without a publisher returns typed HTTP 503; it is never represented as live.

## M4 navigation runtime recovery (2026-10-07)

| Check | Status | Evidence |
|---|---|---|
| Root cause isolated | PASS | stale Nav2 process group plus orphan lifecycle manager competed with a new instance's DDS services |
| Prerequisite graph | PASS | `/scan`, `/odom`, `/map`, TF and `map → base_link` were present |
| Fresh Nav2 lifecycle | PASS | `controller_server`, `planner_server`, `bt_navigator` each reported `active [3]` |
| Fixed virtual goal | PASS | `(1.0, 0.0)` `NavigateToPose` returned `SUCCEEDED` |

Recovery sequence: stop the complete old Nav2 launch process tree, verify no
Nav2 server/lifecycle process remains, then start exactly one
`nav2_launch.py` instance after SLAM has map/TF data. Do not use the action
name advertised through stale DDS discovery as evidence that navigation works.

## AI-assisted Design first slice (2026-10-07)

`POST /api/v1/design/plan` now composes the existing requirement parser,
frozen validated registry, compatibility resolver, and in-memory template
expander. It returns capability IDs, selected packages, and template previews
with no generated workspace. The GUI Design workspace presents that reviewable
plan rather than raw parser JSON. The existing structured-provider contract can
later connect a local or external model, but no key, provider, workspace write,
or build is enabled by this endpoint. Full suite: 64 tests.

## M14 GUI presentation refinement (2026-10-07)

The five existing, typed-API GUI views now use the operator-facing labels
Overview, Design, Build, Run, and Diagnose. The landing view narrows the
workflow to three understandable stages: create a plan, review/generate, and
run in simulation. Its Design CTA is the primary next action; operational
evidence remains available without dominating the starting screen. The
existing local CSS tokens were used for a typography-first, low-chrome visual
pass. Chrome renders were reviewed at 1500px and 390px; the narrow layout now
uses full-width stacked actions and has no page-level horizontal overflow.
No robotics behavior, API contract, ROS topic, or safety boundary changed.
Automated suite: `.venv/bin/python -m pytest -q` → 64 passed.

## M14 precision product-surface redesign (2026-10-07)

M14 was visually rebuilt without changing a robotics/API behavior or safety
boundary. The workspace now uses a low-chrome titanium surface, ink-first
typography, a single signal-blue active state, and a dark stage only for
simulation evidence. `PRODUCT.md` records the real product constraints and
`DESIGN.md` records the implemented tokens, responsive layout, components, and
accessibility rules. The redesigned Overview and Design views were visually
reviewed at 1500px and 390px. Automated suite:
`.venv/bin/python -m pytest -q` → 64 passed.

## M14 workflow-motion and compact-navigation pass (2026-10-07)

The M14 presentation now communicates state changes rather than behaving as a
static dashboard: workspace navigation uses a short clipped transition,
runtime updates confirm their affected surface, and the live camera indicator
signals sampling. The only persistent motion is that live signal and it has a
reduced-motion alternative. At tablet and mobile widths the workflow is a
3+2 stage grid, replacing the previous horizontally scrollable navigation.
No API/ROS behavior changed. Automated suite:
`.venv/bin/python -m pytest -q` → 64 passed.
