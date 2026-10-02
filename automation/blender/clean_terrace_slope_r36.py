"""Elimina cristas residuais: perfil entre galerias e borda real da ladeira."""
import bpy,bmesh,json,runpy,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));scene=bpy.context.scene
assert 'final_slope_profile' not in r
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];S=Matrix(r['layout']['frame_world']);SI=S.inverted();x0,x1,back,front=r['layout']['colonnade_extent_candidate'];floor=r['layout']['colonnade_floor_candidate_m'];a=r['access_connection_correction']
source=scene.objects[r['terrain'][0]['object']];allowed={i for i,m in enumerate(source.data.materials) if any(k in m.name.lower() for k in ('terreno','encosta','conten','solo e vegetação')) and not any(k in m.name.lower() for k in ('asfalto','passeio','pedonal','chile'))}
roadmat={i for i,m in enumerate(source.data.materials) if m and m.name=='MVP | asfalto da ladeira'};assert roadmat,'Controle da ladeira ausente'
roadids=np.array(sorted({v for f in source.data.polygons if f.material_index in roadmat for v in f.vertices}),dtype=int)
def points(o):
    v=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',v);M=np.array(wm(o));return v.reshape((-1,3))@M[:3,:3].T+M[:3,3]
roadworld=points(source)[roadids]
def road_positions():
    ids={v for f in source.data.polygons if f.material_index not in allowed for v in f.vertices};return {tuple(round(k,5) for k in source.data.vertices[i].co) for i in ids}
roads=road_positions();segments=[]
for s in [r['preserved_gallery_connection']['segment'],a['gallery_before']]:
    p,u,n=Vector(s['origin_world']),Vector(s['along_world']),Vector(s['outward_world']);L=s['length_from_existing_controls_m'];d=roadworld-np.array(p);xx=d@np.array(u);yy=d@np.array(n);anchors=[]
    for t in np.linspace(0,L,12):
        ids=np.flatnonzero((np.abs(xx-t)<2.5)&(yy>5)&(yy<70));assert len(ids),'Sem controle de pista na banda da galeria'
        nearest=float(yy[ids].min());chosen=ids[yy[ids]<nearest+.35];anchors.append([float(t),float(yy[chosen].mean()),float(roadworld[chosen,2].mean())])
    segments.append((s,p,u,n,np.array(anchors)))
knots=r['garden_profile_refinement']['profile_candidate_y_z'];ky,kz=np.array(knots).T
def step_height(x,y):
    p=Vector((x,y))
    for f in a['garden_flights']:
        aa,bb=Vector(f['a'][:2]),Vector(f['b'][:2]);d=bb-aa;L=d.length;u=d/L;t=(p-aa).dot(u)
        if -.30<=t<=L+.30 and abs((p-aa).cross(u))<=f['width_candidate_m']/2+.10:return f['a'][2]+(f['b'][2]-f['a'][2])*max(0,min(1,t/L))-.42
    return None
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
rows=[]
for item in r['terrain']:
    o=scene.objects[item['object']];M=wm(o);I=M.inverted();me=o.data;world=points(o);before=sig(o);regionmask=np.zeros(len(me.vertices),dtype=bool)
    local=(world-np.array(S.col[3].xyz))@np.array(S.to_3x3())
    regionmask|=(local[:,0]>x0-2)&(local[:,0]<x1+2)&(local[:,1]>3.8)&(local[:,1]<35.55)
    for s,p,u,n,anchors in segments:
        d=world-np.array(p);xx=d@np.array(u);yy=d@np.array(n);regionmask|=(xx>-.3)&(xx<s['length_from_existing_controls_m']+.3)&(yy>=0)&(yy<anchors[:,1].max())
    idx=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',idx);starts=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('loop_start',starts);mask=np.logical_or.reduceat(regionmask[idx],starts)
    if o==source:
        mi=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',mi);mask&=np.isin(mi,list(allowed))
    bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();region={bm.faces[int(i)] for i in np.flatnonzero(mask)}
    # Contornos simples na frente dos arcos; não remalhar nem recortar ruas.
    for s,p,u,n,anchors in segments:
        for normal,value in ((u,0),(u,s['length_from_existing_controls_m']),(n,0),(n,.7),(n,4),(n,8)):
            faces=[f for f in region if f.is_valid and (o!=source or f.material_index in allowed)];geom=set(faces)
            for f in faces:geom.update(f.edges);geom.update(f.verts)
            res=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(p+normal*value),plane_no=M.to_3x3().transposed()@normal,clear_inner=False,clear_outer=False)
            for e in res['geom_cut']:
                if hasattr(e,'link_faces'):region.update(e.link_faces)
    changed=0
    for v in {v for f in region if f.is_valid for v in f.verts}:
        if o==source and any(f.material_index not in allowed for f in v.link_faces):continue
        w=M@v.co;lp=SI@w;target=w.z
        if x0-2<=lp.x<=x1+2 and 3.8<lp.y<=35.55:
            weight=ease((lp.x-x0+2)/2)*ease((x1+2-lp.x)/2)*ease((lp.y-3.8)/1.2)
            desired=float(np.interp(lp.y,ky,kz));step=step_height(lp.x,lp.y)
            # Não erguer cones de solo para sustentar escadas; manter o talude
            # contínuo e escavar apenas quando há interpenetração.
            if step is not None:desired=min(desired,step)
            if back-.36<=lp.y<=front+.2 and x0-.001<=lp.x<=x1+.001:desired=floor-.27;weight=1
            target=w.z+(desired-w.z)*weight
        for s,p,u,n,anchors in segments:
            d=w-p;xx,yy=d.dot(u),d.dot(n);L=s['length_from_existing_controls_m'];edge=float(np.interp(xx,anchors[:,0],anchors[:,1]));edgez=float(np.interp(xx,anchors[:,0],anchors[:,2]))
            if not(-.3<=xx<=L+.3 and -.001<=yy<edge-.001):continue
            upper=p.z-.22;low=edgez+5.5;split=max(1,edge-3.2)
            if yy<=.7:desired=upper
            elif yy<=split:desired=upper+(low-upper)*(yy-.7)/max(.1,split-.7)
            else:desired=low+(edgez-low)*(yy-split)/max(.1,edge-split)
            weight=ease((xx+.3)/.3)*ease((L+.3-xx)/.3)
            target=min(target,w.z+(min(w.z,desired)-w.z)*weight)
        if abs(target-w.z)<.00001:continue
        w.z=target;v.co=I@w;changed+=1
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();item['after']=sig(o);rows.append({'object':o.name,'before':before,'after':item['after'],'changed_vertices':changed})
assert not roads-road_positions(),'Via alterada'
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
r['final_slope_profile']={'classification':'ADAPT_LOCAL','reason':'Remover cristas altas residuais em frente aos arcos e cones de solo criados sob escadas. Recompõe talude contínuo até a borda real da ladeira, extraída da malha existente. Mantém ruas e galerias preservadas.','terrain':rows,'road_edge_controls': [{'segment':s['name'],'anchors_local_t_distance_z':anchors.tolist()} for s,p,u,n,anchors in segments],'road_positions_preserved':len(roads),'actual_terrain_survey':None,'xy_road_width_dem_changed':False,'visual_review':'pending'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':r['source_after'],'changed_vertices':[t['changed_vertices'] for t in rows]},ensure_ascii=False))
