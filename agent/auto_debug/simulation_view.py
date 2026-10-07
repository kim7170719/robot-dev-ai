"""Read-only bridge from ROS camera and odometry topics to the GUI."""

from __future__ import annotations

import base64
import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CameraSource = Literal["isaac", "webcam"]

CAMERA_TOPICS: dict[CameraSource, str] = {
    "isaac": "/camera/image_raw",
    "webcam": "/webcam/color/image_raw",
}


class SimulationFrame(BaseModel):
    """One camera sample and its matching latest robot pose."""

    model_config = ConfigDict(extra="forbid")

    image_png_base64: str = Field(min_length=1)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    x_m: float
    y_m: float
    yaw_rad: float
    source_topic: str


FrameRunner = Callable[[CameraSource], SimulationFrame]


class SimulationFrameCollector:
    """Call the fixed ROS subscriber helper without a shell or ROS writes."""

    def __init__(self, runner: FrameRunner | None = None) -> None:
        self._runner = runner or _collect_frame

    def collect_frame(self, source: CameraSource = "isaac") -> SimulationFrame:
        return self._runner(source)


def _collect_frame(source: CameraSource) -> SimulationFrame:
    helper = Path(__file__).with_name("camera_frame_capture.py")
    try:
        completed = subprocess.run(
            ("/usr/bin/python3", str(helper), CAMERA_TOPICS[source]),
            check=False,
            capture_output=True,
            text=True,
            timeout=4,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        raise RuntimeError("ROS camera frame was not available") from error
    if completed.returncode != 0:
        message = completed.stderr.strip() or "ROS camera frame was not available"
        raise RuntimeError(message) from None
    try:
        payload = json.loads(completed.stdout)
        image_bytes = base64.b64decode(payload["image_png_base64"], validate=True)
        if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("camera helper did not return PNG data")
        return SimulationFrame.model_validate(payload)
    except (KeyError, ValueError, json.JSONDecodeError) as error:
        raise RuntimeError("ROS camera frame was malformed") from error
