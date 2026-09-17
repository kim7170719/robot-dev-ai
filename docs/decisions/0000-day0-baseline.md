# 0000: Day 0 research baseline

Date: 2026-09-17

## Decision

Keep the stack frozen as written in `CURSOR_PROJECT_GUIDE.md` version 0.2:

- Ubuntu 24.04 LTS as the official research OS
- ROS 2 Jazzy as the only ROS distribution for MVP
- System Python 3.12 series
- Isaac Sim as the physics simulator
- Differential-drive robot as the first target

## Why

This matches the NVIDIA / ROS 2 Jazzy path in the guide. Changing any of these before Gate 0 would restart environment work.

## Status

Accepted for M0. ROS 2 Jazzy itself is not installed yet; that is M1.
