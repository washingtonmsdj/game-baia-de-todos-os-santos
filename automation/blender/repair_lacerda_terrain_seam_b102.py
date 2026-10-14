"""Reutiliza índices coincidentes só nos vértices novos do recorte local."""
import bpy,json,runpy
import numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102'
e=json.loads((out/'excavation.json').read_text());r=json.loads((out/'application.json').read_text())
o=bpy.context.scene.objects[e['source_object']];m=o.data;n=e['unchanged_source_vertex_coordinates']
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
assert sig(o)==e['after_signature']==r['terrain_after_signature']
raw=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',raw);p=raw.reshape((-1,3))
loops=np.empty(len(m.loops),dtype=np.int32);starts=np.empty(len(m.polygons),dtype=np.int32);counts=np.empty(len(m.polygons),dtype=np.int32)
m.loops.foreach_get('vertex_index',loops);m.polygons.foreach_get('loop_start',starts);m.polygons.foreach_get('loop_total',counts)
used=set(loops[loops>=n].tolist());mapping=np.arange(len(p),dtype=np.int32);changes=[]
for i in sorted(used):
 distances=np.linalg.norm(p[:i].astype(float)-p[i].astype(float),axis=1);j=int(distances.argmin())
 if distances[j]<=5e-6:
  mapping[i]=mapping[j];changes.append({'new_index':i,'source_index':int(mapping[j]),'residual_m':float(distances[j])})
assert changes and max(v['residual_m'] for v in changes)<=5e-6
newloops=mapping[loops];changed_faces=[]
for fi in np.nonzero(np.add.reduceat((newloops!=loops).astype(np.int32),starts)>0)[0]:
 ids=newloops[starts[fi]:starts[fi]+counts[fi]];assert len(set(ids))==len(ids)
 assert counts[fi]==3
 tri=p[ids].astype(float);assert np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))>1e-10
 changed_faces.append(int(fi))
old=bpy.data.meshes[o['boas_source_mesh_before_b102']];oldraw=np.empty(n*3,dtype=np.float32);old.vertices.foreach_get('co',oldraw)
assert np.array_equal(raw[:n*3],oldraw)
new=bpy.data.meshes.new('B102 | terreno com recorte documental e índices contínuos')
new.vertices.add(len(p));new.vertices.foreach_set('co',raw)
new.loops.add(len(loops));new.loops.foreach_set('vertex_index',newloops)
new.polygons.add(len(starts));new.polygons.foreach_set('loop_start',starts);new.polygons.foreach_set('loop_total',counts)
materials=np.empty(len(starts),dtype=np.int32);m.polygons.foreach_get('material_index',materials)
smooth=np.empty(len(starts),dtype=np.bool_);m.polygons.foreach_get('use_smooth',smooth)
new.polygons.foreach_set('material_index',materials);new.polygons.foreach_set('use_smooth',smooth)
for mat in m.materials:new.materials.append(mat)
for uv in m.uv_layers:
 values=np.empty(len(loops)*2,dtype=np.float32);uv.data.foreach_get('uv',values)
 new.uv_layers.new(name=uv.name).data.foreach_set('uv',values)
new.update(calc_edges=True);o.data=new
before=e['after_signature'];after=sig(o)
e['after_signature']=after;e['seam_repair']='docs/reports/blender/lacerda-exterior-b102/terrain-seam-repair.json'
r['terrain_after_signature']=after;r['reopened']=False
for row in r['changes']:
 if row['object']==o.name:row['after']['signature']=after
proof={'status':'BOUNDED_SOURCE_INDEX_REUSE','source_object':o.name,'before_signature':before,'after_signature':after,
 'mapping':changes,'changed_polygon_indices':changed_faces,'tolerance_m':5e-6,'all_vertex_coordinates_unchanged':True,
 'source_dem_unchanged':True,'uv_materials_unchanged':True,'reason':'CDT float32 criou índices novos para pontos fonte coincidentes e uma duplicata entre triângulos. Reuso limitado aos novos índices; nenhum movimento ou merge global.'}
for filename,value in [('excavation.json',e),('application.json',r),('terrain-seam-repair.json',proof)]:
 (out/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'reused_new_indices':len(changes),'affected_polygons':len(changed_faces),'max_residual_m':max(v['residual_m'] for v in changes),'all_original_coordinates_preserved':True}))
