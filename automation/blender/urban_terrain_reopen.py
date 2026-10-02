"""Reabre a revisão salva, confirma malhas e atualiza a conferência da cena."""
import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(root/c['world_source']['file']))
game=bpy.data.collections['41 GAMEPLAY | URBAN SLICE'];assert len(game.objects)==2
assert {o.get('boas_role') for o in game.objects}=={'road','walkable'}
p=root/'docs/reports/blender/urban_terrain_partition.json';r=json.loads(p.read_text(encoding='utf8'));r.update(reopened=True,scene_meshes={o.name:{'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in game.objects});p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'revision':c['world_source']['revision'],'reopened':True}))
