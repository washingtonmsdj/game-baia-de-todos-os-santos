"""Confere a revisão salva e a folga das folhas após corrigir a espessura."""
import bpy,ast,json,hashlib,bmesh,collections,struct,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
r=Path(__file__).resolve().parents[2]
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_chapa_v20.blend'
bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
s=bpy.context.scene;body=s.objects['HILUX | CARROCERIA PRINCIPAL']
for fn in ast.parse((r/'automation/blender/audit_hilux_doors_v18.py').read_text(encoding='utf8')).body:
 if isinstance(fn,ast.FunctionDef) and fn.name in {'fingerprint','mesh_review','triangles','intersections'}:
  exec(compile(ast.Module(body=[fn],type_ignores=[]),'auditoria-folgas','exec'),globals())
rp=r/'docs/reports/blender/hilux_chapa_v20.json';report=json.loads(rp.read_text(encoding='utf8'))
changed=[n for n,h in report['base_mesh_hashes'].items() if fingerprint(s.objects[n])!=h]
assert not changed
old=json.loads((r/'artifacts/vehicles/rondesp/v19-mesh-after.json').read_text(encoding='utf8'))['geometry']
h=hashlib.sha256()
for v in old['vertices']:h.update(struct.pack('<3d',*v))
for f in old['faces']:
 vs=f[1:];h.update(struct.pack('<I',len(vs)));h.update(struct.pack('<'+'I'*len(vs),*vs))
assert h.hexdigest()==fingerprint(body),'Malha base diferente da V19'
d=json.loads((r/'docs/reports/blender/hilux_portas_v18.json').read_text(encoding='utf8'))['door_assemblies']
pivots=[s.objects[x['pivot']] for x in d];shells=[s.objects[x['shell']] for x in d];angles=[p['abertura_graus'] for p in pivots]
audit={'scope':'Conferência das quatro folhas contra Mirror, espessura interna e normais finais, em três poses. Ferragens de contato excluídas. Sem certificação de varredura contínua.','samples':[],'body_mesh':mesh_review(body),'base_geometry_matches_v19':True,'all_saved_base_meshes_match':True}
try:
 for angle in [0,5,70]:
  for p in pivots:p['abertura_graus']=float(angle);p.update_tag(refresh={'OBJECT'})
  s.frame_set(s.frame_current);bpy.context.view_layer.update()
  bt=triangles(body,True);dt=[triangles(o) for o in shells]
  sample={'degrees':angle,'door_body':{o.name:len(intersections(t,bt)) for o,t in zip(shells,dt)},'door_pairs':sum(len(intersections(dt[i],dt[j])) for i in range(4) for j in range(i+1,4))}
  audit['samples'].append(sample)
finally:
 for p,a in zip(pivots,angles):p['abertura_graus']=a;p.update_tag(refresh={'OBJECT'})
 s.frame_set(s.frame_current);bpy.context.view_layer.update()
audit['door_body_intersections']=sum(sum(t['door_body'].values()) for t in audit['samples']);audit['door_pair_intersections']=sum(t['door_pairs'] for t in audit['samples'])
report['geometry_review']=audit;report['source_reopened']=True;report['sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'reopened':True,'body_base_matches_v19':True,'door_body_intersections':audit['door_body_intersections'],'door_pair_intersections':audit['door_pair_intersections'],'mesh_review':audit['body_mesh']}))
