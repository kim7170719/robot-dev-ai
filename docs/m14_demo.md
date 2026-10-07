# M14 GUI MVP demo

The M14 demo is a same-origin FastAPI application and a build-less browser
interface. It presents virtual-only evidence; it does not contain an Isaac
viewport and it does not command physical hardware.

## Start

```bash
cd ~/dev/robot-dev-ai
.venv/bin/pip install -e .
bash scripts/run_m14_demo.sh
```

Open <http://127.0.0.1:8000> on the Ubuntu host.

## Safe walkthrough

1. **Dashboard** → inspect the latest-run timeline and live simulation health.
   Choose **Run full pipeline** to parse, resolve, generate in a temporary
   workspace, perform the restricted build, and collect runtime evidence. The
   temporary workspace is removed before the result returns. Select the
   validation checkbox only when the fixed simulation goal is intended.
2. **Requirement** → parse the supplied Chinese differential-drive, LiDAR,
   Camera, and navigation request.
3. **Robot Configuration** → resolve the bundled validated differential-drive
   example or preview its template in memory.
4. **Runtime** → collect only the fixed read-only ROS evidence. The launcher
   sources Jazzy and the repository workspace before starting the API. If ROS
   is not running, the command evidence reports that condition; the GUI does
   not infer a healthy runtime.
5. **Validation / Experience** → inspect the sample repair proposal. The
   frozen `m4-navigation` virtual validator remains behind a checkbox and an
   explicit API confirmation; it is the only action that may send the
   pre-approved goal to a running Isaac/ROS simulation.

## Acceptance evidence

On 2026-10-07 the local demo served all five views over HTTP. Project summary,
requirement parsing, and the non-mutating repair proposal were exercised
against the live server. The automated suite passed with 60 tests. No runtime
collection or navigation-validation request was issued during this demo.

The v0.2 visual pass was rendered and inspected in local Chrome at 1440px and
390px viewport widths. It adds the control-room shell, status cards, guided
workflow, focused evidence panels, keyboard focus styling, reduced-motion
support, and a mobile single-column card layout. Formal axe-core auditing is
not configured in this repository yet.

Template-preview errors are returned as typed HTTP 422 JSON evidence. The GUI
demo provides the complete differential-drive template values, so its template
preview renders eight files rather than returning a server-error page.

## Full Run evidence

On 2026-10-07, `POST /api/v1/mvp/full-run` executed the frozen Chinese
differential-drive + LiDAR + Camera + navigation request without requesting
simulation validation. It parsed all four capabilities, returned
`build-succeeded`, cleaned the temporary workspace, and observed 25 ROS nodes,
80 topics, and 3 TF edges. One `/tf_static --once` inspection timed out, so the
dashboard truthfully presents the runtime as **Partial**.
