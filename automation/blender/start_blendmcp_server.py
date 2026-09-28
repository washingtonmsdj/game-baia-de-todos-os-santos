from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import bpy


def args_after_separator() -> list[str]:
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1 :]


parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=9877)
args = parser.parse_args(args_after_separator())

addon_dir = Path(os.environ["APPDATA"]) / "Blender Foundation" / "Blender" / "5.2" / "scripts" / "addons"
if str(addon_dir) not in sys.path:
    sys.path.append(str(addon_dir))

import blendmcp_addon

if not hasattr(bpy.types.Scene, "blendermcp_port"):
    blendmcp_addon.register()
bpy.context.scene.blendermcp_port = args.port
server = blendmcp_addon.BlendMCPServer(host="localhost", port=args.port)
server.start()
bpy.types.blendermcp_server = server
if hasattr(bpy.context.scene, "blendermcp_server_running"):
    bpy.context.scene.blendermcp_server_running = True
version = ".".join(str(part) for part in blendmcp_addon.bl_info.get("version", ()))
print(f"BLENDMCP_FALLBACK_READY port={args.port} version={version}")
