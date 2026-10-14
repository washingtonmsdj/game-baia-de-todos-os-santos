"""Controles XY e borda real da B73; nenhuma geometria alterada."""
import bpy,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];folder=root/'docs/reports/blender/centro-expansion'
fit=json.loads((root/'artifacts/structural-pipeline/centro-lapa-tororo-fontenova/georef_fit.json').read_text(encoding='utf8'))['robust_fit']
anchors=fit['anchors'];chosen=[]
for fx in (lambda a:a['blender_xy'][0],lambda a:-a['blender_xy'][0],lambda a:a['blender_xy'][1],lambda a:-a['blender_xy'][1],lambda a:a['residual_blender_units']):
    a=min(anchors,key=fx)
    if a not in chosen:chosen.append(a)
chosen += [a for a in anchors if a['osm_id']==402383814]
rows=[]
for a in chosen:
    points=[]
    for name in a['object_names']:
        o=bpy.data.objects.get(name)
        if o is None:continue
        corners=[o.matrix_world@Vector(c) for c in o.bound_box]
        points.append([(min(p[i] for p in corners)+max(p[i] for p in corners))/2 for i in range(2)])
    actual=np.median(points,axis=0)
    rows.append({'osm_id':a['osm_id'],'objects':a['object_names'],'source_xy':a['predicted_blender_xy'],'live_xy':actual.tolist(),'residual_blender_units':float(np.linalg.norm(actual-a['predicted_blender_xy'])),'cached_center_difference':float(np.linalg.norm(actual-a['blender_xy'])),'classification':'KEEP_REAL_REFERENCE'})
o=bpy.context.scene.objects['MVP | terreno corrigido | colisão estática']
co=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',co);co=co.reshape(-1,3)
M=np.array(o.matrix_world);world=co@M[:3,:3].T+M[:3,3]
lo=world[:,:2].min(axis=0);hi=world[:,:2].max(axis=0)
boundary={}
for name,axis,coordinate in [('east',0,hi[0]),('south',1,lo[1])]:
    selected=world[np.abs(world[:,axis]-coordinate)<.005]
    selected=selected[np.argsort(selected[:,1-axis])]
    boundary[name]=selected.tolist()
np.savez_compressed(root/'artifacts/structural-pipeline/centro-lapa-tororo-fontenova/core_boundary.npz',east=np.array(boundary['east']),south=np.array(boundary['south']),bounds=np.array([*lo,*hi]))
report={'source_file':Path(bpy.data.filepath).relative_to(root).as_posix(),'controls':rows,'xy_extent_blender_units':[float(hi[i]-lo[i]) for i in range(2)],'units':bpy.context.scene.unit_settings.scale_length,'boundary_counts':{k:len(v) for k,v in boundary.items()},'boundary_bounds':[float(x) for x in [*lo,*hi]],'absolute_georeference_verified':False,'geometry_changed':False}
(folder/'live_controls.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
from collections import defaultdict
domains=[]
for name in ['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa']:
    ob=bpy.context.scene.objects[name];me=ob.data
    edge_ids=np.empty(len(me.loops),np.int32);me.loops.foreach_get('edge_index',edge_ids)
    count=np.bincount(edge_ids,minlength=len(me.edges));edges=np.empty(len(me.edges)*2,np.int32);me.edges.foreach_get('vertices',edges);edges=edges.reshape(-1,2)[count==1]
    positions=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',positions);positions=positions.reshape(-1,3);mat=np.array(ob.matrix_world);positions=positions@mat[:3,:3].T+mat[:3,3]
    adjacency=defaultdict(list)
    for a,b in edges:adjacency[int(a)].append(int(b));adjacency[int(b)].append(int(a))
    irregular=[i for i,v in adjacency.items() if len(v)!=2]
    remaining={tuple(sorted(map(int,e))) for e in edges};rings=[];rejected=[]
    while remaining:
        a,b=min(remaining);remaining.remove((a,b));path=[a,b];previous=a;current=b
        while current!=a:
            options=[n for n in adjacency[current] if n!=previous and tuple(sorted((current,n))) in remaining]
            if len(options)!=1:break
            nxt=options[0];remaining.remove(tuple(sorted((current,nxt))));path.append(nxt);previous,current=current,nxt
        if current==a and len(path)>3:rings.append(positions[path].tolist())
        else:rejected.append(len(path))
    domains.append({'object':name,'rings':rings,'irregular_boundary_vertices':len(irregular),'open_chains':rejected,'source_vertices':len(me.vertices)})
(folder/'existing_ground_boundaries.json').write_text(json.dumps({'source':report['source_file'],'domains':domains},ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps({'domains':[{'object':d['object'],'rings':len(d['rings']),'irregular':d['irregular_boundary_vertices'],'open_chains':len(d['open_chains'])} for d in domains]}))
