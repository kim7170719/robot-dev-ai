---
name: Robot Dev AI M14
description: Precision product surface for a safe virtual-robot workflow.
---

# Design System

## Overview

**Creative North Star:** Precision Product Surface — a calm, high-fidelity
workspace that makes the next safe robotics action obvious. The visual language
is Apple-inspired in restraint, material clarity, and typography, without
copying Apple UI, marks, or layouts.

The interface is operational rather than decorative: a bright product surface
for planning and review, with a dark stage reserved for runtime evidence.

## Colors

| Role | Token | Value |
|---|---|---|
| Canvas | `--canvas` | `#f5f5f7` |
| Surface | `--surface` | `#ffffff` |
| Ink | `--text` | `#17181c` |
| Supporting text | `--muted` | `#60646f` |
| Signal/action | `--primary` | `#0071e3` |
| Focus | `--focus` | `#005bb8` |
| Evidence stage | — | `#10151d` |
| Safe state | — | `#25714e` |

Use signal blue only for an active state, a focus ring, or an intentional
operator action. Dark surfaces are evidence contexts, not a second app theme.

## Typography

- Interface: system UI stack with `PingFang TC` and `Noto Sans TC` fallbacks.
- Display: `clamp(44px, 5.8vw, 74px)`, tight tracking, `0.98` line height.
- Section title: 22–30px, tight tracking.
- Body: 16–18px, `1.55` line height; supporting evidence never below 12px.
- Uppercase metadata is limited to compact navigation/context labels.

## Layout

- Desktop: 238px translucent sidebar; content is capped at 1240px.
- Content padding: responsive 20–72px; primary header has intentional open
  space before evidence.
- Spacing follows the existing scale and uses 12/16/20/28/34/54px intervals.
- At 960px the sidebar becomes a horizontal workflow rail; at 640px actions,
  cards, sensor controls, and evidence panels become one column.
- The page must never require horizontal scrolling at narrow widths.
- Workspace navigation lives in a three-part top bar: brand/home, five-stage
  workflow navigation, then language and safety utilities. It replaces the
  former permanent left rail.

## Language

The UI offers a Chinese/English switch for the entry surface, primary
workspace navigation, and primary Overview actions. ROS topic names, message
types, and API evidence remain literal technical evidence and are not
translated.

## Operator Copy

Primary UI text uses everyday task language: explain the immediate goal first
(for example, “開始規劃” or “確認建議內容”), then put implementation details
in supporting copy or the Diagnose view. Do not lead a non-specialist with
terms such as schema, registry, template, workspace, command, or runtime.
Technical evidence remains available and literal when an operator needs it.

## Elevation & Depth

- Surfaces separate through a one-pixel neutral edge and tonal contrast.
- The sidebar and top bar use restrained translucency and blur only when the
  platform supports it.
- Shadows are neutral and soft; do not use coloured glows or card stacks to
  fabricate hierarchy.

## Motion

The authored moment is an evidence signal travelling through the robot-workflow
surface: a view change is a short clipped workspace transition, and a freshly
received runtime value briefly confirms its own card. The live-camera dot is
the only persistent loop; it means sampling is active. Routine controls respond
within 180ms. Motion is reduced to static state changes under
`prefers-reduced-motion`.

## Landing Surface

The entry surface is intentionally separate from the operator workspace. Its
single SVG robot performs an environment-readiness sequence: a differential
drive body settles in space while its LiDAR sweep, camera glint, and two signal
points communicate sensor readiness. “進入工作區” moves directly to the
existing Overview; “直接建立方案” opens Design. The scene has no external image
dependency and reduces to a still, readable robot under `prefers-reduced-motion`.

The current landing implementation is a locally served WebGL scene with an
original procedural humanoid assembled from native geometry; it does not
download or depend on a third-party robot model at runtime. Its white-shell,
charcoal-joint, and cyan-visor treatment is an illustrative concept, not a
simulator viewport or a physical-hardware claim.

## Humanoid Motion Sequence

The landing robot uses continuous, damped joint motion between system-ready,
environment-scan, friendly-wave, acknowledgement, mobility-check, and
ready-stance states. It never swaps a robot image mid-sequence. The motion
stops outside the landing surface or in a hidden tab and remains a still,
readable pose when reduced motion is requested.

## Control Surface

Overview is the operational counterpart to the landing surface: deep ink,
cool-blue signal lines, and high-contrast data surfaces communicate the same
robotic system without compromising readable controls. The task-form views
stay bright and calm for focused input and review.

## Shapes

- Small control radius: 12px.
- Standard card radius: 18px.
- Feature surface radius: 26px.
- Primary and secondary buttons are full pills. Avoid arbitrary radii.

## Components

### Workflow navigation

Small circular CSS indicators and an active blue row show the current stage.
Use text labels (`Overview`, `Design`, `Build`, `Run`, `Diagnose`) rather than
decorative glyphs.

### Primary action

Ink pill with white text. One primary action per decision area; on small
screens it fills the available width.

### Secondary action

Transparent, neutral-outline pill. It supports the primary action rather than
competing with it.

### Status metric

Bright neutral card for normal data; an ink card may summarize the selected
run. Status is conveyed with text as well as colour.

### Evidence stage

Deep-ink panel for simulation health, live camera material, and runtime data.
It clearly identifies the source and never implies an interactive viewport.

### Form and focus treatment

Inputs have a quiet neutral field. Keyboard focus is a 3px blue outline with
an offset. A skip link takes keyboard users directly to the workspace.

## Do's and Don'ts

**Do:** keep one clear next action; preserve generous whitespace; label
simulated and unavailable data honestly; show confirmation requirements near
mutating operations; keep mobile actions stacked and tappable.

**Don't:** add browser ROS controls or arbitrary command entry; use gradients,
neon glows, emoji, or Unicode symbols as structural icons; hide important
status in colour alone; create nested-card clutter; imitate Apple branding.
