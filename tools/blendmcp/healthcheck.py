from __future__ import annotations

import argparse
import json
import socket
import sys
from typing import Any


def request(host: str, port: int, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(data)
        buffer = bytearray()
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            buffer.extend(chunk)
            try:
                return json.loads(buffer.decode("utf-8"))
            except json.JSONDecodeError:
                continue
    raise RuntimeError("BlendMCP closed connection without a complete JSON response")


def normalize_version(value: Any) -> str | None:
    if isinstance(value, (list, tuple)):
        return ".".join(str(part) for part in value)
    if isinstance(value, str):
        return value.strip() or None
    return None


def addon_version(host: str, port: int, timeout: float) -> tuple[str | None, str]:
    direct = request(host, port, {"type": "get_addon_version", "params": {}}, timeout)
    if direct.get("status") == "success":
        result = direct.get("result") or {}
        return normalize_version(result.get("version")), "get_addon_version"

    code = (
        "import blendmcp_addon; "
        "print('.'.join(str(x) for x in blendmcp_addon.bl_info.get('version', ())))"
    )
    fallback = request(host, port, {"type": "execute_code", "params": {"code": code}}, timeout)
    if fallback.get("status") != "success":
        return None, "unavailable"
    result = fallback.get("result") or {}
    output = str(result.get("result") or "").strip()
    return output or None, "execute_code_fallback"


def scene_file(host: str, port: int, timeout: float) -> str | None:
    code = "import bpy; print(bpy.data.filepath)"
    response = request(host, port, {"type": "execute_code", "params": {"code": code}}, timeout)
    if response.get("status") != "success":
        return None
    result = response.get("result") or {}
    return str(result.get("result") or "").strip() or None


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the local BlendMCP Blender bridge.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9876)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--expect-version")
    parser.add_argument("--expect-scene-contains")
    args = parser.parse_args()

    try:
        scene = request(args.host, args.port, {"type": "get_scene_info", "params": {}}, args.timeout)
        version, version_method = addon_version(args.host, args.port, args.timeout)
        blend_file = scene_file(args.host, args.port, args.timeout)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    scene_result = scene.get("result") if scene.get("status") == "success" else None
    ok = isinstance(scene_result, dict)
    checks: dict[str, bool] = {}
    if args.expect_version:
        checks["version"] = version == args.expect_version
        ok = ok and checks["version"]
    if args.expect_scene_contains:
        checks["scene"] = bool(blend_file and args.expect_scene_contains in blend_file)
        ok = ok and checks["scene"]

    output = {
        "ok": ok,
        "host": args.host,
        "port": args.port,
        "addon_version": version,
        "version_method": version_method,
        "blend_file": blend_file,
        "scene": scene_result,
        "checks": checks,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
