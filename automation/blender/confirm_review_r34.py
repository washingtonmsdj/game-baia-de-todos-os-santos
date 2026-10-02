"""Fecha a conferência após ajustes só de material/vista e nova reabertura."""
import bpy,json,hashlib,runpy
from pathlib import Path

root=Path(__file__).resolve().parents[2];path=root/'docs/reports/blender/palacio_rio_branco_r30b34.json'
r=json.loads(path.read_text(encoding='utf8'));scene=bpy.context.scene
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
with (root/r['source_after']['file']).open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
assert proof['load_post_completed'] and proof['sha256']==sha==r['source_after']['sha256']
assert Path(bpy.data.filepath).resolve()==(root/proof['file']).resolve()
signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
terrain=r['retaining_profile_refinement']['geometry'];names={g['object'] for g in terrain}
assert all(signature(scene.objects[n])==s for n,s in r['protected_signatures'].items() if n not in names)
assert all(signature(scene.objects[g['object']])==g['after'] for g in terrain)
assert r['localized_scene_review']['road_mesh_review']['missing_vertices']==0
r['localized_scene_review']['file_reopened']=proof
r['localized_scene_review']['road_mesh_review']['final_geometry_same_as_reviewed']=True
images=['artifacts/palacio-rio-branco/r30b34_'+s+'.png' for s in ('frente','lateral','galeria_palacio','galeria_prefeitura')]
assert all((root/p).is_file() for p in images)
r['visual_review']={'status':'reviewed_modeling_candidate','source_sha256':sha,'views':images,'method':'Renders CPU na janela MCP e comparação com as nove capturas locais; sem revisão de gameplay.','limits':'Estatuária/águias e interior não produzidos; implantação da colunata branca da encosta pendente. Alturas/profundidades proporcionais às fotos; não medidas.'}
lim='Materiais procedurais revisados no Blender; bake PBR e revisão de LOD/colisão antes da futura exportação glTF.'
if lim not in r['limitations']:r['limitations'].append(lim)
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':proof['file'],'sha256':sha,'reopened':True,'protected_components_unchanged':len(r['protected_signatures'])-len(names),'geometry_same_as_reviewed':True,'views':images},ensure_ascii=False))
