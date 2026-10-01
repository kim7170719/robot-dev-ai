"""Raycast geometry for the synthetic M4 room (no ROS required)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from room_scan import N_RAYS, RANGE_MAX, ROOM_X, ROOM_Y, ranges_from_pose


def _range_at(yaw_offset: float, pose=(0.0, 0.0, 0.0)) -> float:
    x, y, yaw = pose
    ranges = ranges_from_pose(x, y, yaw)
    idx = int(round((yaw_offset + math.pi) / (2.0 * math.pi / N_RAYS))) % N_RAYS
    return ranges[idx]


def test_forward_hits_east_wall():
    r = _range_at(0.0)
    assert abs(r - ROOM_X) < 0.05, r


def test_left_hits_north_wall():
    r = _range_at(math.pi / 2.0)
    assert abs(r - ROOM_Y) < 0.05, r


def test_back_hits_west_wall():
    r = _range_at(math.pi)
    assert abs(r - ROOM_X) < 0.05, r


def test_obstacle_is_closer_than_wall():
    # Obstacle center (2, 1); ray along that bearing should hit the box first.
    bearing = math.atan2(1.0, 2.0)
    r = _range_at(bearing)
    wall = ROOM_X / math.cos(bearing)
    assert r < wall
    assert r < 2.5
    assert r > 1.5


def test_shifted_pose_shortens_forward_range():
    r = _range_at(0.0, pose=(1.0, 0.0, 0.0))
    assert abs(r - (ROOM_X - 1.0)) < 0.05, r


def test_ray_count_and_max_range_cap():
    ranges = ranges_from_pose(0.0, 0.0, 0.0)
    assert len(ranges) == N_RAYS
    finite = [r for r in ranges if math.isfinite(r)]
    assert finite
    assert max(finite) <= RANGE_MAX + 1e-6
