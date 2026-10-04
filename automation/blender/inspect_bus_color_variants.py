"""Inspeção limitada da fonte amarela, sem modificar a cena."""
import bpy, json
from pathlib import Path

scene = bpy.context.scene
rows = []
for obj in scene.objects:
    if obj.type not in {'MESH', 'CURVE', 'FONT'}:
        continue
    mats = [m.name if m else None for m in obj.data.materials]
    if any(m and 'Amarelo' in m for m in mats) or obj.type == 'FONT':
        rows.append({'object': obj.name, 'materials': mats,
                     'collections': [c.name for c in obj.users_collection],
                     'text': obj.data.body if obj.type == 'FONT' else None})
result = {'file': Path(bpy.data.filepath).name, 'scene': scene.name,
                  'dirty': bpy.data.is_dirty, 'objects': len(scene.objects),
                  'yellow_users_and_text': rows}
repo = Path(__file__).resolve().parents[2]
out = repo / 'artifacts/vehicles/torino-color-inspection.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
