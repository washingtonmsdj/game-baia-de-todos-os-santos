"""Inspeção read-only da frente externa na janela B80 recuperada."""
import bpy, json, os, hashlib, runpy
import numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/reports/blender/cairu-market-b81';OUT.mkdir(parents=True,exist_ok=True)
expected=ROOT/'blender/salvador_lacerda_r30b80_piso_e_embarque_superior.blend'
assert Path(bpy.data.filepath).resolve()==expected.resolve() and not bpy.data.is_dirty
assert os.getpid()==json.loads((ROOT/'artifacts/blender-sessions/current-session.json').read_text())['pid']
binding=json.loads((ROOT/'docs/reports/world/cairu-market-pedestrian/osm_crossing_binding.json').read_text(encoding='utf8'))
ways={w['osm_id']:w for w in binding['ways']}
chain=list(reversed(ways[312006925]['nodes']))+ways[395865976]['nodes'][1:]+list(reversed(ways[1423065746]['nodes']))[1:]
hits=json.loads((ROOT/'docs/reports/world/cairu-market-pedestrian/character_sweep_crossing_collision_roles.json').read_text(encoding='utf8'))['routes'][0]['penetrations']
dg=bpy.context.evaluated_depsgraph_get();sources=[];physical=[]
distance_fn=runpy.run_path(str(ROOT/'tools/world/slice_geometry.py'))['capsule_distances']
for name in ['INFERIOR | piso do saguão','INFERIOR R21 | passeio da entrada','INFERIOR R21 | rebaixo acessível','B63 | VISUAL | meios-fios das vias existentes','MVP | terreno corrigido | colisão estática','LAC R30B06 | fundo verde travessia 3178050253']:
 ob=bpy.data.objects.get(name)
 if ob is None:continue
 ev=ob.evaluated_get(dg);mesh=ev.to_mesh()
 try:
  mesh.calc_loop_triangles();verts=[ev.matrix_world@v.co for v in mesh.vertices]
  sources.append({'object':name,'properties':{k:ob[k] for k in ob.keys() if isinstance(ob[k],(str,float,int,bool))},'parent':ob.parent.name if ob.parent else None,'bounds':{'min':[min(v[i] for v in verts) for i in range(3)],'max':[max(v[i] for v in verts) for i in range(3)]},'triangles':len(mesh.loop_triangles)})
  if name in ['INFERIOR R21 | passeio da entrada','INFERIOR R21 | rebaixo acessível']:
   physical.append({'name':name,'collections':[c.name for c in ob.users_collection],'parent':None,'dynamic':False,'cabin_member':False,'elevator_role':None,'landing':None,'door_side':None,'walkable':True,'properties':sources[-1]['properties'],'geometry':{'vertices':[list(v) for v in verts],'triangles':[list(t.vertices) for t in mesh.loop_triangles],'complete_mesh':True,'bounds':sources[-1]['bounds']}})
  if name.startswith('B63'):
   triangles=[[list(verts[i]) for i in t.vertices] for t in mesh.loop_triangles]
   witnesses=[]
   for hit in hits:
    p=np.asarray(hit['foot']);alltri=np.asarray(triangles);lo=alltri.min(axis=1);hi=alltri.max(axis=1)
    indices=np.flatnonzero(np.all(hi>=p-[.3,.3,0],axis=1)&np.all(lo<=p+[.3,.3,1.8],axis=1))
    distances=distance_fn(p,alltri[indices],.3,1.8);index=int(indices[int(np.argmin(distances))]);best=(float(distances.min()),index,triangles[index])
    witnesses.append({**hit,'source_object':name,'surface_triangle':best[1],'surface_vertices':best[2],'capsule_distance':best[0],'role':'CURB_STEP_PHYSICAL','action':'step_solver_candidate; não remover collider; bloquear se apoio/clearance falhar','maximum_step_candidate':.25,'live_source_confirmed':True,'collider_binding':'fonte visual usada na pré-validação; reconciliação derivada pendente'})
 finally:ev.to_mesh_clear()
report={'file':expected.relative_to(ROOT).as_posix(),'pid':os.getpid(),'objects':len(bpy.context.scene.objects),'dirty':bpy.data.is_dirty,'frame':bpy.context.scene.frame_current,'SSOT':binding['parent_ssot'],'sources':sources,'six_witnesses':witnesses,'route_controls':chain,'market_entrance_verified':False,'terminus':'node/12229090827; não declarar entrada Mercado','scene_changed':False}
(OUT/'live_inspection_b80.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(ROOT/'artifacts/lacerda-controller/external_live_supports_b80.json').write_text(json.dumps(physical,ensure_ascii=False),encoding='utf8')
print(json.dumps({'B80_visible_confirmed':True,'pid':os.getpid(),'six_witnesses':len(witnesses),'control_nodes':[n['id'] for n in chain],'sources':len(sources),'scene_changed':False}))
