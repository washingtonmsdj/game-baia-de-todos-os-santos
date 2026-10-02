"""Recorte local do solo no acréscimo; preserva galerias anteriores e vias."""
import bpy,bmesh,json,runpy,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));c=r['preserved_gallery_connection'];scene=bpy.context.scene
assert c['terrain_stage']=='pending'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];s=c['segment'];p,u,n=Vector(s['origin_world']),Vector(s['along_world']),Vector(s['outward_world']);L=s['length_from_existing_controls_m'];depth=s['depth_candidate_m'];z=p.z-.22
source=scene.objects[r['terrain'][0]['object']];allowed={i for i,m in enumerate(source.data.materials) if any(k in m.name.lower() for k in ('terreno','encosta','conten','solo e vegetação')) and not any(k in m.name.lower() for k in ('asfalto','passeio','pedonal','chile'))}
def road_positions():
    ids={v for f in source.data.polygons if f.material_index not in allowed for v in f.vertices};return {tuple(round(k,5) for k in source.data.vertices[i].co) for i in ids}
roads=road_positions();rows=[]
for item in r['terrain']:
    o=scene.objects[item['object']];M=wm(o);I=M.inverted();me=o.data;before=sig(o)
    v=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',v);A=np.array(M);world=v.reshape((-1,3))@A[:3,:3].T+A[:3,3];relative=world-np.array(p);x=relative@np.array(u);y=relative@np.array(n)
    idx=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',idx);starts=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('loop_start',starts);mask=np.ones(len(me.polygons),dtype=bool)
    for vals,low,high in ((x,-.12,L+.12),(y,-depth-.15,1.8)):
        vals=vals[idx];mask&=(np.maximum.reduceat(vals,starts)>low)&(np.minimum.reduceat(vals,starts)<high)
    if o==source:
        mi=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',mi);mask&=np.isin(mi,list(allowed))
    bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();region={bm.faces[int(i)] for i in np.flatnonzero(mask)}
    for normal,d in ((u,-.12),(u,L+.12),(n,-depth-.15),(n,-depth),(n,0),(n,.65),(n,1.8)):
        faces=[f for f in region if f.is_valid and (o!=source or f.material_index in allowed)];geom=set(faces)
        for f in faces:geom.update(f.edges);geom.update(f.verts)
        res=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(p+normal*d),plane_no=M.to_3x3().transposed()@normal,clear_inner=False,clear_outer=False)
        for e in res['geom_cut']:
            if hasattr(e,'link_faces'):region.update(e.link_faces)
    changed=0
    for v in {v for f in region if f.is_valid for v in f.verts}:
        if o==source and any(f.material_index not in allowed for f in v.link_faces):continue
        w=M@v.co;rel=w-p;xx,yy=rel.dot(u),rel.dot(n)
        if not(-.121<=xx<=L+.121 and -depth-.151<=yy<=1.801):continue
        weight=1 if yy<=.65 else max(0,min(1,(1.8-yy)/1.15));target=w.z+(min(w.z,z)-w.z)*weight
        if abs(target-w.z)<.00001:continue
        w.z=target;v.co=I@w;changed+=1
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();item['after']=sig(o);rows.append({'object':o.name,'before':before,'after':item['after'],'changed_vertices':changed})
assert not roads-road_positions(),'Circulação alterada'
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items()),'Componente preservado mudou'
c['terrain_stage']='applied_pending_visual_review';c['terrain_correction']={'geometry':rows,'road_positions_preserved':len(roads),'xy_road_width_dem_changed':False,'classification':'ADAPT_LOCAL'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':r['source_after'],'changed_vertices':[v['changed_vertices'] for v in rows],'roads_preserved':len(roads)},ensure_ascii=False))
