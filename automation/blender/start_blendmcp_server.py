from __future__ import annotations

import os
import sys
from pathlib import Path

import bpy

PORT = int(os.environ.get("BOAS_BLENDMCP_PORT", "9877"))
addon_dir = Path(os.environ["APPDATA"]) / "Blender Foundation" / "Blender" / "5.2" / "scripts" / "addons"
if str(addon_dir) not in sys.path:
    sys.path.append(str(addon_dir))

import blendmcp_addon

if not hasattr(bpy.types.Scene, "blendermcp_port"):
    blendmcp_addon.register()

existing = getattr(bpy.types, "blendermcp_server", None)
if existing is not None and getattr(existing, "running", False):
    existing_port = int(getattr(existing, "port", PORT))
    if existing_port != PORT:
        existing.stop()
        existing = None

if existing is None or not getattr(existing, "running", False):
    bpy.context.scene.blendermcp_port = PORT
    server = blendmcp_addon.BlendMCPServer(host="localhost", port=PORT)
    server.start()
    bpy.types.blendermcp_server = server
else:
    server = existing
if hasattr(bpy.context.scene, "blendermcp_server_running"):
    bpy.context.scene.blendermcp_server_running = True

version = ".".join(str(part) for part in blendmcp_addon.bl_info.get("version", ()))
print(f"BLENDMCP_FALLBACK_READY port={PORT} version={version}")
