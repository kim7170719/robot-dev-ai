"""
M3-02: URDF import via official isaacsim.asset.importer.urdf API.
Run via: kit --ext-folder /isaac-sim/apps --ext-folder /isaac-sim/extscache --no-window --allow-root --exec
"""
import sys, os

print("[M3-02] Script started", flush=True)

import omni.kit.app
import omni.kit.commands
import omni.usd

app = omni.kit.app.get_app()
print(f"[M3-02] App version: {app.get_build_version()}", flush=True)

try:
    from omni.isaac.core.utils.extensions import enable_extension
    enable_extension("isaacsim.asset.importer.urdf")
    print("[M3-02] URDF extension enabled", flush=True)
except Exception as e:
    # Fallback: try direct import
    print(f"[M3-02] enable_extension fallback: {e}", flush=True)
    import omni.kit.app
    manager = omni.kit.app.get_app().get_extension_manager()
    manager.set_extension_enabled_immediate("isaacsim.asset.importer.urdf", True)
    print("[M3-02] URDF extension enabled via manager", flush=True)

# Update to let extension initialize
for _ in range(10):
    app.update()

print("[M3-02] Creating import config...", flush=True)
status, import_config = omni.kit.commands.execute("URDFCreateImportConfig")
print(f"[M3-02] Config status: {status}", flush=True)

import_config.merge_fixed_joints = False
import_config.import_inertia_tensor = True
import_config.fix_base = False
import_config.distance_scale = 1.0

URDF = "/root/simple_diff_robot.urdf"
USD  = "/root/Documents/simple_diff_robot.usd"

print(f"[M3-02] Importing URDF: {URDF}", flush=True)
status2, prim_path = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path=URDF,
    import_config=import_config,
    get_articulation_root=True,
)
print(f"[M3-02] Import status={status2} prim={prim_path}", flush=True)

if status2:
    ctx = omni.usd.get_context()
    ctx.save_as_stage(USD)
    print(f"[M3-02] USD saved: {USD}", flush=True)

os.makedirs("/root/Documents", exist_ok=True)
with open("/root/Documents/m3_status.txt", "w") as f:
    f.write(f"import_status={status2}\n")
    f.write(f"prim={prim_path}\n")
    f.write("=== M3-02 COMPLETE ===\n")

print("=== M3-02 COMPLETE ===", flush=True)
app.post_quit()
