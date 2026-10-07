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

## Elevation & Depth

- Surfaces separate through a one-pixel neutral edge and tonal contrast.
- The sidebar and top bar use restrained translucency and blur only when the
  platform supports it.
- Shadows are neutral and soft; do not use coloured glows or card stacks to
  fabricate hierarchy.

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
