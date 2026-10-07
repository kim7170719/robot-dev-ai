# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary users are robot developers and operators working on the Robot Dev AI
virtual MVP. They need to turn a robot requirement into a reviewable plan,
inspect bounded build/runtime evidence, and decide the next safe action.

## Product Purpose

Robot Dev AI turns a natural-language robot request into structured,
registry-bounded ROS 2 templates, then presents build, simulation, and
validation evidence. Success means the user can understand the current state
and take a deliberate next step without treating the browser as a robot
controller.

## Positioning

The product joins a frozen hardware/package registry, explicit confirmations,
and observable ROS/Isaac evidence in one workflow; it does not give an AI or a
browser unrestricted command execution.

## Operating Context

The current deployment runs locally on an Ubuntu ROS/Isaac host. The initial
robot is a differential-drive virtual robot with LiDAR, camera, Nav2, and
Isaac Sim evidence. Windows is documentation and Git only.

## Capabilities and Constraints

- GUI consumes typed same-origin API responses only; it does not invoke ROS,
  Docker, or a shell directly.
- Workspace mutation, build, and fixed navigation validation remain
  confirmation-gated.
- Runtime and camera views are read-only evidence, not a simulation viewport
  or remote-control interface.
- M15 real hardware is pending because no physical hardware has been funded.

## Brand Commitments

The user requested a practical, technology-forward interface with the
restraint, hierarchy, and finish associated with Apple product surfaces. This
is an inspiration constraint, not permission to copy Apple assets or layouts.

## Evidence on Hand

The frozen G12 virtual MVP, M14 typed API, Isaac camera/odometry telemetry,
and 64 automated tests are documented in `docs/progress.md` and
`docs/AI_HANDOFF.md`. There is no physical robot or Jetson evidence.

## Product Principles

1. Put the next safe operator decision ahead of raw telemetry.
2. Never make unavailable, partial, or simulated evidence look confirmed.
3. Reveal operational detail progressively rather than hiding it.
4. Preserve explicit confirmation before every mutating action.

## Accessibility & Inclusion

Keyboard focus must remain visible; status cannot rely on colour alone; the
web workspace must remain usable at narrow mobile widths and with reduced
motion enabled.
