"""G14.5 component-library artifacts and a dependency-free seed-manifest loader."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from .models import (
    Capability,
    Hardware,
    Identifier,
    RegistryModel,
    RobotKnowledgeRegistry,
    RosInterface,
)
from .v04 import (
    AdapterContract,
    Constraint,
    EvidenceStatus,
    HardwareProfileV04,
    RegistryDocumentV04,
    SoftwareProfileV04,
)
from .v05 import SourceType, TrustLevel


ArtifactType = Literal[
    "hardware_profile",
    "software_package",
    "driver_sdk",
    "protocol",
    "adapter",
    "component_template",
    "simulation_adapter",
    "validation_recipe",
    "evidence_record",
]
EvidenceLevel = Literal["E0", "E1", "E2", "E3", "E4", "E5"]


class ArtifactLicense(RegistryModel):
    """Declared source-license metadata, including an explicit unknown state."""

    spdx: str = Field(min_length=1, max_length=128)
    redistribution: Literal["allowed", "prohibited", "unknown"]


class ArtifactSource(RegistryModel):
    """Traceable metadata source; loading it never fetches the URL."""

    source_type: SourceType
    url: str = Field(min_length=8, max_length=2048, pattern=r"^https?://")
    trust_level: TrustLevel
    license: ArtifactLicense
    retrieved_at: date
    source_commit: str | None = Field(default=None, min_length=1, max_length=128)


class ArtifactConstraints(RegistryModel):
    """Declared compatibility envelope; empty lists mean no claim was recorded."""

    os: list[str] = Field(default_factory=list)
    ros_distro: list[str] = Field(default_factory=list)
    cpu_arch: list[str] = Field(default_factory=list)
    firmware: list[str] = Field(default_factory=list)
    runtime: list[str] = Field(default_factory=list)


class ArtifactVerification(RegistryModel):
    """Current evidence observation and the highest intended next gate."""

    evidence_level: EvidenceLevel
    status: EvidenceStatus
    target_evidence_level: EvidenceLevel

    @model_validator(mode="after")
    def reject_unavailable_real_or_community_claims(self) -> ArtifactVerification:
        if self.evidence_level in {"E4", "E5"}:
            raise ValueError("G14.5 seed artifacts cannot claim E4 or E5 evidence")
        return self


class ComponentArtifact(RegistryModel):
    """One narrow component record linked later to the frozen core registry."""

    id: Identifier
    name: str = Field(min_length=1, max_length=128)
    artifact_type: ArtifactType
    vendor: str = Field(min_length=1, max_length=128)
    model: str = Field(min_length=1, max_length=128)
    version: str | None = Field(default=None, max_length=128)
    source: ArtifactSource
    capabilities: list[Identifier] = Field(default_factory=list)
    interfaces: list[Identifier] = Field(default_factory=list)
    transports: list[Identifier] = Field(default_factory=list)
    requires: list[Identifier] = Field(default_factory=list)
    constraints: ArtifactConstraints = Field(default_factory=ArtifactConstraints)
    limitations: list[str] = Field(default_factory=list)
    verification: ArtifactVerification
    provenance: str = Field(min_length=1, max_length=128)
    registry_version: Literal["g14.5"] = "g14.5"


class SeedManifest(RegistryModel):
    """Minimal G14.5 catalog; intentionally separate from legacy registry envelopes."""

    schema_version: Literal["g14.5"] = "g14.5"
    artifacts: list[ComponentArtifact] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_artifact_ids(self) -> SeedManifest:
        artifact_ids = [artifact.id for artifact in self.artifacts]
        if len(artifact_ids) != len(set(artifact_ids)):
            raise ValueError("G14.5 seed manifest contains duplicate artifact identifiers")
        return self


def load_seed_manifest(path: Path) -> SeedManifest:
    """Load JSON-compatible YAML without installing a parser or fetching data."""
    return SeedManifest.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_default_seed_manifest() -> SeedManifest:
    """Load the repository-owned P0 catalog; it has no network or hardware I/O."""
    return load_seed_manifest(Path(__file__).parents[1] / "data" / "registry" / "seed_manifest.yaml")


def build_reference_registry(manifest: SeedManifest) -> RegistryDocumentV04:
    """Compile the narrow G14.5 fixture into the unchanged v0.4 resolver schema."""
    artifacts = {artifact.id: artifact for artifact in manifest.artifacts}
    required = {
        "differential-drive", "jetson-generic", "esp32", "ld06",
        "realsense-d455", "ros2-control", "diff-drive-controller",
        "serial-bridge", "twist-twiststamped", "nav2",
    }
    missing = sorted(required - set(artifacts))
    if missing:
        raise ValueError("G14.5 reference registry is missing seed artifacts: " + ", ".join(missing))

    capabilities = [
        Capability(id="differential-drive", interface_ids=["cmd-vel", "odometry"], template_id="differential-drive"),
        Capability(id="motor-control"),
        Capability(id="encoder-feedback", interface_ids=["joint-state"]),
        Capability(id="real-time-loop"),
        Capability(id="ros2-runtime"),
        Capability(id="nav2-runtime"),
        Capability(id="navigation", interface_ids=["cmd-vel", "laser-scan", "odometry"], template_id="nav2"),
        Capability(id="planar-lidar", interface_ids=["laser-scan"], template_id="lidar"),
        Capability(id="rgbd-camera", interface_ids=["camera-image", "camera-info"], template_id="camera"),
        Capability(id="hardware-abstraction", interface_ids=["joint-state", "cmd-vel-stamped"]),
        Capability(id="simulation-validation"),
    ]
    interfaces = [
        RosInterface(id="cmd-vel", topic="/cmd_vel", message_type="geometry_msgs/msg/Twist"),
        RosInterface(id="cmd-vel-stamped", topic="/cmd_vel", message_type="geometry_msgs/msg/TwistStamped"),
        RosInterface(id="odometry", topic="/odom", message_type="nav_msgs/msg/Odometry"),
        RosInterface(id="joint-state", topic="/joint_states", message_type="sensor_msgs/msg/JointState"),
        RosInterface(id="laser-scan", topic="/scan", message_type="sensor_msgs/msg/LaserScan"),
        RosInterface(id="camera-image", topic="/camera/image_raw", message_type="sensor_msgs/msg/Image"),
        RosInterface(id="camera-info", topic="/camera/camera_info", message_type="sensor_msgs/msg/CameraInfo"),
    ]
    hardware = [
        Hardware(id="differential-drive", kind="mobile-base", vendor="Robot Dev AI", capability_ids=["differential-drive"]),
        Hardware(id="jetson-generic", kind="edge-compute", vendor="NVIDIA", capability_ids=["ros2-runtime", "nav2-runtime", "navigation"]),
        Hardware(id="esp32", kind="mcu", vendor="Espressif", capability_ids=["motor-control", "encoder-feedback", "real-time-loop"]),
        Hardware(id="ld06", kind="lidar", vendor="LDROBOT", capability_ids=["planar-lidar"]),
        Hardware(id="realsense-d455", kind="camera", vendor="Intel", capability_ids=["rgbd-camera"]),
    ]
    verification = {artifact.id: _verification_state(artifact) for artifact in manifest.artifacts}
    registry = RobotKnowledgeRegistry(hardware=hardware, interfaces=interfaces, capabilities=capabilities)
    return RegistryDocumentV04(
        source_schema_version="v0.3",
        registry=registry,
        constraints=[Constraint(id="serial-transport", kind="transport", expected_value="serial", provenance="g14.5-seed-manifest")],
        software_profiles=[
            SoftwareProfileV04(id="ros2-control", kind="runtime", verification_state=verification["ros2-control"], provenance=artifacts["ros2-control"].provenance),
            SoftwareProfileV04(id="diff-drive-controller", kind="driver", verification_state=verification["diff-drive-controller"], provenance=artifacts["diff-drive-controller"].provenance),
            SoftwareProfileV04(id="nav2", kind="runtime", verification_state=verification["nav2"], provenance=artifacts["nav2"].provenance),
        ],
        hardware_profiles=[
            HardwareProfileV04(device_id="differential-drive", device_class="mobile-base", capability_ids=["differential-drive"], driver_ids=["ros2-control", "diff-drive-controller"], verification_state=verification["differential-drive"], provenance=artifacts["differential-drive"].provenance),
            HardwareProfileV04(device_id="jetson-generic", device_class="edge-compute", capability_ids=["ros2-runtime", "nav2-runtime", "navigation"], driver_ids=["nav2"], verification_state=verification["jetson-generic"], provenance=artifacts["jetson-generic"].provenance),
            HardwareProfileV04(device_id="esp32", device_class="mcu", capability_ids=["motor-control", "encoder-feedback", "real-time-loop"], transport_ids=["serial-transport"], verification_state=verification["esp32"], provenance=artifacts["esp32"].provenance),
            HardwareProfileV04(device_id="ld06", device_class="lidar", capability_ids=["planar-lidar"], transport_ids=["serial-transport"], verification_state=verification["ld06"], provenance=artifacts["ld06"].provenance),
            HardwareProfileV04(device_id="realsense-d455", device_class="camera", capability_ids=["rgbd-camera"], verification_state=verification["realsense-d455"], provenance=artifacts["realsense-d455"].provenance),
        ],
        adapter_contracts=[
            AdapterContract(id="serial-bridge", kind="serial", supported_device_classes=["mcu"], required_transport_ids=["serial-transport"], verification_state=verification["serial-bridge"], provenance=artifacts["serial-bridge"].provenance),
            AdapterContract(id="ros2-control", kind="ros2-control", supported_device_classes=["mobile-base"], required_software_profile_ids=["ros2-control", "diff-drive-controller"], verification_state=verification["ros2-control"], provenance=artifacts["ros2-control"].provenance),
            AdapterContract(id="twist-twiststamped", kind="interface-normalization", supported_device_classes=["mobile-base"], required_software_profile_ids=["ros2-control"], verification_state=verification["twist-twiststamped"], provenance=artifacts["twist-twiststamped"].provenance),
        ],
    )


def _verification_state(artifact: ComponentArtifact) -> Literal["verified", "experimental", "unknown"]:
    if artifact.verification.evidence_level == "E0":
        return "unknown"
    return "experimental"


ComponentArtifact.model_rebuild()
SeedManifest.model_rebuild()
