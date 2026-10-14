"""B66: auditoria local somente de leitura de água, píeres e interfaces."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];sc=bpy.context.scene
cat=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf-8-sig'));source=cat['validation_source']
assert source['revision']=='R30B.66'
assert Path(bpy.data.filepath).resolve()==(r/source['file']).resolve()
with (r/source['file']).open('rb') as h: assert hashlib.file_digest(h,'sha256').hexdigest()==source['sha256']
ref=json.loads((r/'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json').read_text(encoding='utf-8-sig'))
wanted=[]
for f in ref['features']:
 xy=f.get('blender_xy',[])
 if not xy or not any(-1200<x<150 and -1100<y<700 for x,y in xy):continue
 tags=f.get('tags',{})
 if tags.get('man_made') in ('pier','breakwater','groyne','quay') or tags.get('bridge')=='yes' or tags.get('natural') in ('beach','coastline'):
  wanted.append({'osm_id':f['osm_id'],'osm_type':f['osm_type'],'layer':f['layer'],'closed':f['closed'],'tags':tags,'xy':xy,'metrics':f.get('metrics')})
objects=[]
for o in sc.objects:
 if not any(w in o.name.upper() for w in ('PIER','PÍER','CAIS','TERMINAL','BAÍA','FOAM','SUBMERS','COSTEIR','ENCOSTA')):continue
 if o.type in ('MESH','CURVE'):
  bb=[o.matrix_world@Vector(v) for v in o.bound_box]
  bounds=[[min(p[i] for p in bb) for i in range(3)],[max(p[i] for p in bb) for i in range(3)]]
 else:bounds=None
 props={}
 for k,v in o.items():
  if k.startswith('boas_'):
   try:json.dumps(v);props[k]=v
   except TypeError:props[k]=str(v)
 objects.append({'name':o.name,'type':o.type,'visible':o.visible_get(),'hide_render':o.hide_render,'bounds':bounds,'properties':props,'materials':[m.name if m else None for m in o.data.materials] if o.type in ('MESH','CURVE') else [],'modifiers':[{'name':m.name,'type':m.type,'visible':m.show_viewport} for m in o.modifiers]})
contract=json.loads((r/'docs/reports/blender/r30a8/water_runtime_contract.json').read_text(encoding='utf-8-sig'))
wa=sc.objects[contract['surface_object']]
waters=[wa.matrix_world@v.co for v in wa.data.vertices]
out={'schema':'boas/water-piers-b66-local-inspection-v1','source':source,'water_mesh_z_range':[min(p.z for p in waters),max(p.z for p in waters)],'contract_water_level':contract['water_level_m'],'pier_reference_deck_z':7.255664825439453,'reference_freeboard_candidate':7.255664825439453-contract['water_level_m'],'absolute_vertical_verified':False,'objects':objects,'real_source_features':wanted,'geometry_changed':False}
(r/'docs/reports/blender/water_piers_b66_inspection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'objects':len(objects),'features':len(wanted),'reference_freeboard':out['reference_freeboard_candidate']}))
