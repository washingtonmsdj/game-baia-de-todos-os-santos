"""Exportar somente a faixa terrestre dos dois encontros, sem alterar geometria."""
import bpy,json,numpy as np
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
src=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf-8'))['validation_source']
assert src['revision']=='R30B.67' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
rows={}
for name in ['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B63 | VISUAL | piso contínuo até o cais','BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro']:
 ob=s.objects[name];me=ob.data;me.calc_loop_triangles()
 a=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',a.ravel());mw=np.array(ob.matrix_world);a=a@mw[:3,:3].T+mw[:3,3]
 t=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',t.ravel())
 if name.startswith('BAÍA'):tri=a[t]
 else:
  tri=a[t];mask=(tri[:,:,0].max(axis=1)>-485)&(tri[:,:,0].min(axis=1)<-385)&(tri[:,:,1].max(axis=1)>-215)&(tri[:,:,1].min(axis=1)<-130);tri=tri[mask]
 rows[name]=tri.tolist()
p=r/'artifacts/waterfront/pier_land_region_b67.json'
p.write_text(json.dumps({'source':src,'meshes':rows},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(json.dumps({'regional_triangles':{k:len(v) for k,v in rows.items()}}))
