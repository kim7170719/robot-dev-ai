# M14 GUI MVP demo

The M14 demo is a same-origin FastAPI application and a build-less browser
interface. It presents virtual-only evidence; it does not contain an Isaac
viewport and it does not command physical hardware.

## Start

```bash
cd ~/dev/robot-dev-ai
.venv/bin/pip install -e .
.venv/bin/uvicorn api.app:create_app --factory --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000> on the Ubuntu host.

## Safe walkthrough

1. **Dashboard** → refresh the frozen project metadata.
2. **Requirement** → parse the supplied Chinese differential-drive, LiDAR,
   Camera, and navigation request.
3. **Robot Configuration** → resolve the bundled validated differential-drive
   example or preview its template in memory.
4. **Runtime** → collect only the fixed read-only ROS evidence. If ROS is not
   running, the command evidence reports that condition; the GUI does not
   infer a healthy runtime.
5. **Validation / Experience** → inspect the sample repair proposal. The
   frozen `m4-navigation` virtual validator remains behind a checkbox and an
   explicit API confirmation; it is the only action that may send the
   pre-approved goal to a running Isaac/ROS simulation.

## Acceptance evidence

On 2026-10-07 the local demo served all five views over HTTP. Project summary,
requirement parsing, and the non-mutating repair proposal were exercised
against the live server. The automated suite passed with 59 tests. No runtime
collection or navigation-validation request was issued during this demo.

The v0.2 visual pass was rendered and inspected in local Chrome at 1440px and
390px viewport widths. It adds the control-room shell, status cards, guided
workflow, focused evidence panels, keyboard focus styling, reduced-motion
support, and a mobile single-column card layout. Formal axe-core auditing is
not configured in this repository yet.
