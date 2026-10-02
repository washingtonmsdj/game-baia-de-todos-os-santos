"""Recompõe superfície única de altura no talude frontal, retirando dobras legadas."""
import bpy,bmesh,json,runpy,hashlib,math
import numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));scene=bpy.context.scene
assert 'gallery_slope_joint' in r and 'gallery_slope_surface' not in r
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];source=scene.objects[r['terrain'][0]['object']]
allowed={i for i,m in enumerate(source.data.materials) if m and any(k in m.name.lower() for k in ('terreno','encosta','conten','solo e vegetação')) and not any(k in m.name.lower() for k in ('asfalto','passeio','pedonal','chile'))}
def roadcoords():
    ids={v for f in source.data.polygons if f.material_index not in allowed for v in f.vertices}
    return {tuple(round(k,5) for k in source.data.vertices[i].co) for i in ids}
roads=roadcoords();segments=[r['preserved_gallery_connection']['segment'],r['access_connection_correction']['gallery_before']];tangent=math.tan(r['gallery_slope_joint']['angle_radians']);rows=[]
for item in r['terrain']:
    o=scene.objects[item['object']];me=o.data;M=wm(o);A=np.array(M);I=np.array(M.inverted());before=sig(o);raw=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',raw);co=raw.reshape((-1,3));world=co@A[:3,:3].T+A[:3,3];target=world[:,2].copy();nearest=np.full(len(co),np.inf);movable=np.ones(len(co),dtype=bool)
    if o==source:movable[sorted({v for f in me.polygons if f.material_index not in allowed for v in f.vertices})]=False
    for j,(s,c) in enumerate(zip(segments,r['final_slope_profile']['road_edge_controls'])):
        a=np.array(c['anchors_local_t_distance_z']);p=np.array(s['origin_world']);u=np.array(s['along_world']);n=np.array(s['outward_world']);d=world-p;xx=d@u;yy=d@n;L=s['length_from_existing_controls_m'];edge=np.interp(xx,a[:,0],a[:,1]);edgez=np.interp(xx,a[:,0],a[:,2]);split=np.maximum(1,edge-3.2);upper=p[2]-.22;low=edgez+5.5
        desired=np.where(yy<=.7,upper,np.where(yy<=split,upper+(low-upper)*(yy-.7)/np.maximum(.1,split-.7),low+(edgez-low)*(yy-split)/np.maximum(.1,edge-split)))
        extension=np.maximum(0,yy)*tangent+.35
        mask=((xx>=0)&(xx<=L+extension)) if j==0 else ((xx>=-extension)&(xx<=L))
        # Escolher o perfil mais próximo, em vez de acumular mínimos das
        # correções antigas: todos os pontos devem pertencer à mesma superfície.
        dist=np.hypot(yy,xx-np.clip(xx,0,L));mask&=movable&(yy>=0)&(yy<edge-.001)&(dist<nearest)
        target[mask]=desired[mask];nearest[mask]=dist[mask]
    changed=np.flatnonzero((np.abs(target-world[:,2])>1e-5)&np.isfinite(nearest));world[changed,2]=target[changed];co[changed]=world[changed]@I[:3,:3].T+I[:3,3];me.vertices.foreach_set('co',co.astype(np.float32).ravel());me.update()
    # Paredes verticais do terreno antigo colapsam no mesmo plano. Remover
    # exclusivamente arestas degeneradas desse recorte, sem remalhar vias.
    bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();affected={bm.verts[int(i)] for i in changed};edges={e for v in affected for e in v.link_edges if all(q in affected for q in e.verts)};oldfaces=len(bm.faces)
    bmesh.ops.dissolve_degenerate(bm,dist=1e-5,edges=list(edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();item['after']=sig(o);rows.append({'object':o.name,'before':before,'after':item['after'],'changed_vertices':len(changed),'degenerate_faces_removed':oldfaces-len(me.polygons)})
assert roadcoords()==roads,'Via alterada'
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
r['gallery_slope_surface']={'classification':'ADAPT_LOCAL','reason':'Talude passa a superfície de altura contínua entre os controles arquitetônicos e a borda real da pista. Acumular apenas rebaixamentos deixava dobras do terreno legado; coordenadas recompostas pelo perfil mais próximo e degenerações locais removidas. Não acrescentada outra malha para encobrir o erro.','terrain':rows,'road_positions_preserved':len(roads),'road_width_xy_dem_changed':False,'real_survey':None,'visual_review':'pending'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'changed':[t['changed_vertices'] for t in rows],'saved':r['source_after']},ensure_ascii=False))
