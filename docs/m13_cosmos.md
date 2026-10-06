# M13: Cosmos scenario-generation preflight

## Scope

M13 selects **scenario generation**, not physical reasoning. Cosmos may propose a
reviewable visual or textual scenario for the existing differential-drive robot.
Isaac Sim remains the only authority for deterministic physics, ROS topics,
TF, navigation, and PASS/FAIL validation. Cosmos must never publish robot
commands or replace the G4 simulation validator.

## Interface boundary

The future Cosmos adapter accepts a declarative scenario request:

```json
{
  "scenario_id": "m13-room-001",
  "prompt": "A differential-drive robot navigates around one box obstacle.",
  "seed": 1,
  "camera_frame": "camera_link"
}
```

It returns a proposal or an explicit unavailable result. A proposal is
human-reviewed input to an Isaac world; it is not a simulation result. The
existing `IsaacSimulationValidator` continues to produce navigation PASS/FAIL
evidence after Isaac Sim starts.

## Host preflight — 2026-10-06

| Check | Result | Consequence |
|---|---|---|
| GPU | RTX 2080 Ti, Turing, compute capability 7.5 | unsupported for current Cosmos Predict family |
| VRAM | 11,264 MiB | below the 24 GB minimum documented for Cosmos Reason1 inference; exact Predict model sizing must be rechecked when hardware changes |
| Driver | 580.178.04 | meets the published Predict2.5 driver floor |
| Docker | 29.8.1 with `nvidia-container-runtime` | independent-container route is available |
| Disk | 347 GB free | sufficient for a future isolated image/model cache subject to the selected model's current requirements |

NVIDIA's current prerequisites require Ampere or newer for Predict2/2.5 and
Transfer2.5. The installed Turing GPU therefore fails the architecture
requirement even before model download. No Cosmos image, checkpoint, Conda
environment, or system Python change was made.

## Container plan (not executed on this host)

When an Ampere-or-newer supported host is available, use a dedicated Docker
image and dedicated bind mounts for source, datasets, and checkpoints. Do not
mount the ROS workspace as a writable model environment, and do not install
Cosmos dependencies into system Python or the ROS Jazzy environment.

Before pulling anything, re-check the selected model's official model matrix,
hardware prerequisites, gated-model access, image tag, storage requirement,
and license. Keep credentials outside Git and outside this repository.

## G13 status

**BLOCKED — hardware prerequisite.** The following remain unexecuted:

1. Start a supported independent Cosmos container or environment.
2. Reproduce the selected official scenario-generation example.
3. Turn its result into a reviewable Isaac-world candidate and validate that
   Isaac Sim, rather than Cosmos, remains the physics and PASS/FAIL authority.
4. Demonstrate that G12 still runs when Cosmos is absent.

This is an evidence-based block, not a failed G13 gate. G12 remains fully
usable without Cosmos.

## Official references

- [Cosmos prerequisites](https://docs.nvidia.com/cosmos/latest/prerequisites.html)
- [Cosmos Predict2 installation](https://docs.nvidia.com/cosmos/latest/predict2/installation.html)
- [Cosmos Predict2.5 quickstart](https://docs.nvidia.com/cosmos/latest/predict2.5/quickstart_guide.html)
