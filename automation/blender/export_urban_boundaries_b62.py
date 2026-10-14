import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
water=scene.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'];quay=scene.objects['CAIS | contenção costeira alinhada à linha de costa']
v=[list(water.matrix_world@x.co) for x in water.data.vertices];boundary=[]
for e in water.data.edges:
 a,b=[v[i] for i in e.vertices]
 if abs(a[2]-.35)<1e-4 and abs(b[2]-.35)<1e-4 and a[0]>-1300 and b[0]>-1300:boundary.append([a,b])
rows=[]
for o in scene.objects:
 if o.type=='MESH' and (o.name.startswith('B62 |') or (o.visible_get() and any(t in o.name.lower() for t in ('terrain','terreno','cais','encosta','b57 | pier')))):
  bb=[o.matrix_world@Vector(p) for p in o.bound_box];rows.append({'name':o.name,'visible':o.visible_get(),'bbox':[[min(p[i] for p in bb) for i in range(3)],[max(p[i] for p in bb) for i in range(3)]],'materials':[m.name if m else None for m in o.data.materials]})
for key,name in [('core','MVP | terreno corrigido | colisão estática'),('hq','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa')]:
 o=scene.objects[name];me=o.data
 xyz=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',xyz);xyz=xyz.reshape(-1,3)
 mat=np.array(o.matrix_world);xyz=xyz@mat[:3,:3].T+mat[:3,3]
 indices=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',indices)
 starts=np.empty(len(me.polygons),np.int32);counts=starts.copy();mi=starts.copy()
 me.polygons.foreach_get('loop_start',starts);me.polygons.foreach_get('loop_total',counts);me.polygons.foreach_get('material_index',mi)
 edges=np.empty(len(me.edges)*2,np.int32);me.edges.foreach_get('vertices',edges);edges=edges.reshape(-1,2)
 lei=np.empty(len(me.loops),np.int32);me.loops.foreach_get('edge_index',lei)
 np.savez_compressed(root/f'artifacts/waterfront/urban_{key}_b62.npz',vertices=xyz,indices=indices,starts=starts,counts=counts,materials=mi,edges=edges,loop_edges=lei)
q={'source_file':bpy.data.filepath,'objects':rows,'water_top_edges':boundary,'quay_vertices':[list(quay.matrix_world@p.co) for p in quay.data.vertices],'quay_faces':[list(p.vertices) for p in quay.data.polygons]}
(root/'artifacts/waterfront/urban_scene_b62.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'surfaces':rows,'water_edges':len(boundary)},ensure_ascii=False))
