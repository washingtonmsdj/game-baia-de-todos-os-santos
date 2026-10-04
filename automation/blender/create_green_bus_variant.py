"""Cria a variante verde na janela Blender visível."""
from pathlib import Path
script = Path(__file__).with_name("bus_color_variant.py")
exec(compile(script.read_text(encoding="utf-8"), str(script), "exec"), {"__file__": str(script), "color": "verde"})
