## Correct Kit invocation for scripting

```bash
/isaac-sim/kit/kit \
  /isaac-sim/apps/isaacsim.exp.full.streaming.kit \
  --ext-folder /isaac-sim/apps \
  --ext-folder /isaac-sim/extscache \
  --no-window \
  --allow-root \
  --exec /root/script.py
```

Key flags:
- `--ext-folder /isaac-sim/apps` — finds isaasim experiences/extensions
- `--ext-folder /isaac-sim/extscache` — finds cached extensions like `isaacsim.asset.importer.urdf`
- `--no-window` — headless Docker (no GLFW required)
- `--allow-root` — container runs as root
- `--exec` — script runs AFTER `app ready`

**Do NOT use `--/app/auto_exit_after_exec=1`** — causes dependency solver to run before extensions load.

## URDF import

```python
import omni.kit.commands
from omni.isaac.core.utils.extensions import enable_extension

enable_extension("isaacsim.asset.importer.urdf")
for _ in range(10): app.update()  # let extension initialize

status, cfg = omni.kit.commands.execute("URDFCreateImportConfig")
status2, prim = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path="/root/simple_diff_robot.urdf",
    import_config=cfg,
    get_articulation_root=True,
)
omni.usd.get_context().save_as_stage("/root/Documents/simple_diff_robot.usd")
```

Script: `simulator/worlds/import_urdf.py`
