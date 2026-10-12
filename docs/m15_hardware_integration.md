---
template: technical-design
title: M15 Jetson Orin Nano differential-drive hardware integration
status: active-preflight
version: 0.1
date: 2026-10-12
---

# M15 Jetson Orin Nano differential-drive hardware integration

## 1. Purpose and boundary

M15 moves the validated virtual differential-drive path toward a real platform:
Jetson Orin Nano, a differential-drive base, and Intel RealSense D455. The
target platform also requires a physical 2D LiDAR, wheel encoders, an
independent emergency stop, a known motor controller, and a documented power
path before it can move.

This document is a staged bring-up design, not real-hardware evidence. The
existing M12/G12 Isaac path remains the physics and regression baseline. M14
remains a presentation/API layer and is not a motor-control interface.

## 2. Requirement trace

| ID | Requirement | Source |
|---|---|---|
| R1 | Bring up the user-selected Jetson Orin Nano differential-drive platform with D455. | User-confirmed M15 target |
| R2 | Support physical navigation inputs: 2D LiDAR, wheel encoders/odometry, and D455. | M15 real-robot scope; M12 virtual capabilities |
| R3 | Prevent unsafe motion until the physical stop, power, controller, and restrained test procedure are verified. | Repository hardware-aware / sim-first rules |
| R4 | Preserve ROS 2 Jazzy and the existing simulation baseline; do not make Windows a ROS host. | `AGENTS.md`, `docs/roadmap_v0.3.md` |
| R5 | Publish reproducible, truthful evidence rather than inferred hardware success. | Repository hard rules |

## 3. Chosen approach

Use a staged, evidence-gated bring-up. Each stage must produce its own record
before the next stage can start; a failed or missing prerequisite blocks motion
instead of triggering a workaround. The approach satisfies R1–R5 by separating
read-only discovery from actuator enablement and by keeping hardware-specific
drivers behind normal ROS interfaces.

```mermaid
flowchart LR
  A[Record exact hardware manifest] --> B[Verify power path and independent E-stop]
  B --> C[Jetson OS and ROS read-only inventory]
  C --> D[D455 and LiDAR read-only checks]
  D --> E[Encoder and base-controller bench check]
  E --> F[Restrained low-speed teleop]
  F --> G[Odometry / TF / Nav2 integration]
  G --> H[G15 evidence review]
```

1. Record model, serial, cable, voltage, firmware, and owner details; unknown
   items are blockers, not defaults.
2. Verify battery, fuse, regulator, common ground, and independent emergency
   stop with the drive wheels safely raised or mechanically restrained.
3. Inventory the Jetson and its Jazzy ROS environment without starting motors.
4. Confirm D455 and LiDAR data independently; validate timestamps and frame
   names before combining them.
5. Prove the controller/encoder contract on a bench, then allow a bounded
   low-speed command only in a restrained test.
6. Only after stable odometry, TF, scan, and stop behavior, integrate Nav2 and
   capture a repeatable real-robot G15 run.

## 4. Current evidence and assumptions

- The selected target is Jetson Orin Nano + differential-drive base + D455.
- Earlier Ubuntu-host evidence identified D455 serial `203522250679`; colour
  and RGBD were tested. Its observed USB 2.1 connection is insufficient
  evidence for sustained depth/high-rate operation; use direct USB 3.x for
  the real deployment test.
- No evidence has yet been collected for a physical Jetson, motor controller,
  base protocol, encoder model, LiDAR model, emergency stop, battery, or
  wiring. These are open inputs, not implementation choices.

## 5. Interface contracts

Hardware-specific nodes may vary, but the integration must expose standard ROS
interfaces. Exact package and controller choices wait for the real hardware
manifest.

| Boundary | Required contract | Gate |
|---|---|---|
| Drive input | Controller declares and validates its accepted velocity message type before Nav2 is connected. | E |
| Drive feedback | Wheel state yields timestamped odometry and a documented base frame transform. | E–G |
| LiDAR | Timestamped `sensor_msgs/msg/LaserScan` with documented sensor frame and TF. | D, G |
| D455 | Colour and, where USB 3.x permits, depth/camera-info topics with documented optical frames. | D |
| Safety | Independent physical emergency stop removes drive enable; software stop alone is insufficient. | B, F |

The existing resolver already models message conversion. If the real controller
requires `TwistStamped` while a producer emits `Twist`, the conversion must be
an explicit, tested adapter rather than an undocumented remap.

## 6. Detailed safety state

```text
DISCOVERY -> SENSOR_READY -> BENCH_READY -> RESTRAINED_MOTION -> NAV_READY
              |                  |                 |
              +---- failure -----+------> SAFE_BLOCKED
```

`SAFE_BLOCKED` means no command publisher is started. Transition out requires
a new recorded check of the failed prerequisite; retries are never automatic.
Motion is bounded to a documented low speed and duration in the restrained
stage. No browser endpoint becomes an actuator path.

## 7. Failure modes and handling

| Failure mode | Detection | Handling / recovery | Visible effect |
|---|---|---|---|
| Emergency stop or power path is unverified | Physical inspection and documented stop test absent | Remain `SAFE_BLOCKED`; do not start drive controller | G15 blocked before motion |
| D455 is USB 2.x, missing, or wrong serial | USB inventory and camera diagnostic | Use colour-only diagnostic if appropriate; block depth acceptance until direct USB 3.x is proven | Sensor capability marked limited/failed |
| LiDAR or encoder stream absent / bad TF | Topic/type/rate inspection and TF check | Stop at sensor/bench gate; fix driver, power, frame, or cable | Navigation integration blocked |
| Base protocol or velocity type unknown | Controller documentation and read-only inspection | Do not publish commands; add an explicit adapter only after contract is known | Drive gate blocked |
| Motor moves unexpectedly or telemetry becomes stale | Restrained observer, watchdog, and stop test | Trigger physical emergency stop, remove drive enable, record incident, return to `SAFE_BLOCKED` | Test aborted; no Nav2 attempt |
| Battery/regulator thermal or voltage issue | Measured voltage/current/thermal observation | Power down, correct power design, repeat safety check | Drive gate blocked |

Retries are manual and evidence-driven. No automatic retry may re-enable a
drive controller after a safety failure.

## 8. Observability and evidence

Each stage records date, operator, commands, hardware identifiers, ROS
distribution, driver version, topic/type/rate snapshots, TF snapshot, and raw
log location. Jetson records include power mode, thermal state, and `tegrastats`
evidence during sensor and restrained-motion tests.

The dominant alert is any missing stop verification, stale odometry, missing
scan, unexpected motion, or thermal/power fault: it immediately triggers the
same rollback action—remove drive enable and return to `SAFE_BLOCKED`. A G15
report must distinguish passing sensor evidence from any blocked actuator
evidence.

## 9. Validation plan

| Stage | Acceptance evidence | Motion allowed |
|---|---|---|
| G15-A manifest | Exact part numbers, firmware, power/wiring diagram, controller contract, and safety owner recorded | No |
| G15-B Jetson base | Jetson boots supported image; Jazzy environment and network/USB inventory recorded | No |
| G15-C sensors | D455 and LiDAR streams, frame IDs, timestamps, and diagnostics captured; D455 depth acceptance requires USB 3.x | No |
| G15-D drive bench | Emergency-stop proof, encoder direction/scale, controller state, odometry, and TF evidence captured | Wheels raised or restrained only |
| G15-E restrained teleop | Bounded low-speed command, stop response, odometry direction, and watchdog behavior observed | Yes, restrained only |
| G15-F navigation | Stable `/scan`, odometry, TF, and a documented controlled navigation test | Controlled environment only |

Where code is added, unit tests cover manifest validation and message-contract
selection; integration tests cover the actual ROS driver boundary; end-to-end
evidence covers the relevant G15 stage. A simulated or mocked test cannot
replace a physical stop or drive test.

## 10. Alternative considered

Starting with direct teleoperation would shorten the first demo, but it cannot
satisfy R3 or R5: controller semantics, stop behavior, and encoder direction
would be unproven. The selected staged approach adds time but makes a failed
precondition explicit and reversible.

## 11. Rollout and rollback

Rollout is stage-by-stage, with each stage manually approved from its recorded
evidence. No persistent data migration is involved. The immediate rollback for
any actuator anomaly is the independent physical emergency stop, followed by
removing drive enable/power according to the actual base manual. Software
processes are then deactivated and the run is recorded as failed. A new attempt
starts from the failed stage, not from an assumed-good later stage.

## 12. Open inputs before implementation

1. Exact Jetson Orin Nano model, storage, JetPack/Ubuntu image, and cooling/power arrangement.
2. Differential-drive base, motor driver/controller model, its ROS driver or protocol, motor voltage/current, and connector pinout.
3. Encoder type, resolution, wiring, and expected wheel geometry.
4. 2D LiDAR model, mounting location, driver, USB/serial identity, and power.
5. Emergency-stop component and its independent physical path to drive enable/power.
6. Battery, BMS, fuse, regulators, grounding, and charge procedure.
7. D455 mounting and confirmation of a direct USB 3.x path.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-12 | Initial active preflight design for the user-selected M15 target; no hardware implementation or G15 claim. |
