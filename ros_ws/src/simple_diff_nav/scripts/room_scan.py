"""2D room raycast for synthetic LaserScan.

Room is axis-aligned: x in [-ROOM_X, ROOM_X], y in [-ROOM_Y, ROOM_Y],
plus one box obstacle. Keep in sync with simulator/worlds/m4_lidar_scan.py.
"""
from __future__ import annotations

import math

ROOM_X = 4.0
ROOM_Y = 3.0
OBSTACLE = (2.0, 1.0, 0.5, 0.5)  # cx, cy, width, height
RANGE_MIN = 0.05
RANGE_MAX = 8.0
N_RAYS = 360


def _ray_walls(px: float, py: float, dx: float, dy: float) -> float:
    hit = RANGE_MAX
    if dx > 1e-12:
        t = (ROOM_X - px) / dx
        y = py + t * dy
        if t > 1e-6 and -ROOM_Y <= y <= ROOM_Y:
            hit = min(hit, t)
    if dx < -1e-12:
        t = (-ROOM_X - px) / dx
        y = py + t * dy
        if t > 1e-6 and -ROOM_Y <= y <= ROOM_Y:
            hit = min(hit, t)
    if dy > 1e-12:
        t = (ROOM_Y - py) / dy
        x = px + t * dx
        if t > 1e-6 and -ROOM_X <= x <= ROOM_X:
            hit = min(hit, t)
    if dy < -1e-12:
        t = (-ROOM_Y - py) / dy
        x = px + t * dx
        if t > 1e-6 and -ROOM_X <= x <= ROOM_X:
            hit = min(hit, t)
    return hit


def _ray_aabb(
    px: float,
    py: float,
    dx: float,
    dy: float,
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
) -> float | None:
    tmin = 0.0
    tmax = RANGE_MAX
    for origin, direction, lo, hi in (
        (px, dx, xmin, xmax),
        (py, dy, ymin, ymax),
    ):
        if abs(direction) < 1e-12:
            if origin < lo or origin > hi:
                return None
            continue
        t1 = (lo - origin) / direction
        t2 = (hi - origin) / direction
        tmin = max(tmin, min(t1, t2))
        tmax = min(tmax, max(t1, t2))
        if tmin > tmax:
            return None
    if tmax < 0.0:
        return None
    t = tmin if tmin > 1e-6 else tmax
    if t <= 1e-6 or t > RANGE_MAX:
        return None
    return t


def ranges_from_pose(x: float, y: float, yaw: float) -> list[float]:
    """Return N_RAYS ranges in the lidar frame (angle -pi .. pi)."""
    cx, cy, w, h = OBSTACLE
    xmin, xmax = cx - w / 2.0, cx + w / 2.0
    ymin, ymax = cy - h / 2.0, cy + h / 2.0
    out: list[float] = []
    for i in range(N_RAYS):
        angle = -math.pi + (2.0 * math.pi * i) / N_RAYS
        world = yaw + angle
        dx = math.cos(world)
        dy = math.sin(world)
        hit = _ray_walls(x, y, dx, dy)
        box = _ray_aabb(x, y, dx, dy, xmin, xmax, ymin, ymax)
        if box is not None:
            hit = min(hit, box)
        if hit < RANGE_MIN:
            hit = RANGE_MIN
        if hit >= RANGE_MAX:
            hit = float('inf')
        out.append(hit)
    return out
