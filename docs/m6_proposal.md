# Robot development AI platform proposal

## Problem statement

Developing a mobile robot requires compatible choices across hardware, drivers, ROS 2 interfaces, packages, simulation, and deployment. Today those choices are often integrated manually from fragmented documentation. Errors frequently surface late as build failures, incompatible message types, unavailable capabilities, or simulation failures.

This project investigates whether a structured, evidence-backed workflow can turn a natural-language robot request into a constrained ROS 2 project plan, generate only compatible artifacts, and validate the result in simulation before real-hardware work begins.

## Related work and research gap

ROS 2 supports component composition and managed lifecycle interfaces, but it does not provide a project-specific knowledge layer that reasons from hardware capabilities through drivers and ROS interfaces to package and template selection. Isaac Sim and Isaac ROS provide simulation and accelerated perception components, but they are not an end-to-end requirement-to-validated-project workflow.

Robotics verification research identifies system-level validation as difficult because robotic systems combine multiple technical disciplines. Simulation provides a controlled software-in-the-loop environment, yet its results require explicit limits and evaluation criteria. The gap addressed here is a small, auditable engineering workflow that combines structured requirements, verified reusable templates, compatibility reasoning, and simulator-backed acceptance checks.

## System architecture

~~~text
Natural-language request
        ↓
Requirement agent
        ↓
Structured robot specification
        ↓
Knowledge registry + compatibility resolver
        ↓
Verified project templates
        ↓
ROS 2 build and graph checks
        ↓
Isaac Sim validation
        ↓
Evidence registry: PASS / FAIL / known issue
~~~

The initial implementation sequence is:

1. M7 defines the hardware, driver, ROS interface, capability, package, and validation schemas.
2. M8 creates deterministic templates for differential drive, LiDAR, camera, Nav2, launch, YAML, and Isaac ROS fragments.
3. M9 converts a natural-language request into a validated structured specification.
4. M10 resolves compatibility and chooses packages, conversions, and constraints.
5. M11 captures build and ROS-graph failures with evidence and known fixes.
6. M12 demonstrates prompt to simulation PASS or FAIL for the frozen MVP path.

## Research questions

1. RQ1: Do AI-assisted requirement extraction plus verified templates reduce integration time compared with manual assembly from documentation?
2. RQ2: Does simulation-in-the-loop validation improve the rate at which generated integrations reach a defined ROS and simulation acceptance gate?
3. RQ3: As the evidence registry gains validated capability and issue records, does the workflow reduce human intervention and AI repair iterations?

## Evaluation metrics and protocol

Each evaluation task uses the same differential-drive robot target and a predefined acceptance checklist.

| Metric | Definition |
|---|---|
| Time to first valid integration | Wall-clock time from complete task brief to the first acceptance PASS. |
| Acceptance-pass rate | Passed tasks divided by attempted tasks. |
| Human interventions | Count of human edits or decisions after the task brief. |
| AI repair iterations | Count of generate-diagnose-repair cycles before a terminal result. |
| Reproducibility rate | Repeated executions that reach the same PASS or expected FAIL outcome. |
| Traceability coverage | Required output fields linked to a source requirement, compatibility rule, template, or validation log. |

For each task, run the manual baseline and the assisted workflow under the same environment. Record commands, generated files, build outputs, ROS graph evidence, and Isaac Sim result. Report expected failures as failures; do not exclude them from the denominator.

## Baseline groups

| Group | Method |
|---|---|
| B0 Manual | Engineer assembles a ROS 2 integration from official documentation and project notes. |
| B1 LLM-only | LLM generates artifacts directly from the task brief without registry constraints or verified templates. |
| B2 Templates-only | Structured input selects deterministic templates without an LLM requirement agent. |
| B3 Proposed workflow | Requirement agent, schema validation, registry/resolver, verified templates, and simulation-in-the-loop validation. |

## MVP scope freeze

The M12 MVP supports one robot family: differential-drive mobile robots using Ubuntu 24.04, ROS 2 Jazzy, and Isaac Sim 4.5 Docker. The reference robot is simple_diff_robot. The supported functional path is URDF and ros2_control, navigation with Nav2 and slam_toolbox, synthetic 2D scan in Isaac Sim, and one Isaac ROS image-processing baseline.

Excluded until after M12: other robot morphologies, real hardware, Jetson deployment, multi-distro support, native Isaac Sim installation, Cosmos as a physics replacement, and training a foundation model.

## Risks and limitations

- The current RTX 2080 Ti is below the official Ampere-or-newer Isaac ROS 4.5 x86_64 support matrix. Isaac ROS results are reproducible experimental evidence, not vendor-supported performance evidence.
- Isaac Sim validation uses a kinematic robot and synthetic 2D scan for the G4 path; it is not a proof of full physical fidelity or real sensor behavior.
- Initial results on one robot and one host establish feasibility, not generalization. New hardware must be represented explicitly in the registry and separately validated.
- LLM output is untrusted until schema, compatibility, build, ROS-graph, and simulator gates pass.

## References

- Araujo, Mousavi, and Varshosaz. Testing, Validation, and Verification of Robotic and Autonomous Systems: A Systematic Review. ACM TOSEM, 2023. https://doi.org/10.1145/3542945
- NIST. On the use of simulation in robotics: Opportunities, challenges, and suggestions for moving forward. https://pmc.ncbi.nlm.nih.gov/articles/PMC7817170/
- ROS 2 composition documentation. https://github.com/ros2/ros2_documentation/blob/rolling/source/ROS-Framework/nodes/Working-with-nodes/Composition.rst
- ROS 2 managed nodes design. https://design.ros2.org/articles/node_lifecycle.html
- NVIDIA Isaac ROS 4.5 image pipeline documentation. https://nvidia-isaac-ros.github.io/v/release-4.5/repositories_and_packages/isaac_ros_image_pipeline/index.html
