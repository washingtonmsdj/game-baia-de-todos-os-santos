"""Recompõe a malha local em torno da ligação, escadas e aberturas R36."""
import bpy,bmesh,json,runpy,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));a=r['access_connection_correction'];scene=bpy.context.scene
assert a['terrain_stage']=='pending';assert Path(bpy.data.filepath).resolve()==(root/r['source_after']['file']).resolve()
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];S=Matrix(r['layout']['frame_world']);SI=S.inverted();U,N,P=S.col[0].xyz,S.col[1].xyz,S.col[3].xyz
x0,x1,back,front=r['layout']['colonnade_extent_candidate'];floor=r['layout']['colonnade_floor_candidate_m'];roof=r['layout']['colonnade_roof_candidate_m'];levels=r['layout']['garden_levels_candidate_m'];center=r['layout']['palace_edge_length_m']/2
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())

# A foto situa a descida do jardim no lado oposto aos três arcos, contornando
# o bastião. Troca o lado dos componentes novos, sem escala negativa no objeto.
names=['RIO R36 | '+n for n in ('Escadas laterais do jardim','Guardas das escadas','Passeios dos patamares','Contenções dos patamares','Balaustradas dos terraços')]+['COL R36 | Passeios dos patamares']+['COL R36 | Rampa jardim '+str(j) for j in (1,2,3)]
flip=Matrix(((-1,0,0,2*center),(0,1,0,0),(0,0,1,0),(0,0,0,1)))
for name in names:
    o=scene.objects[name];before=sig(o);o.data.transform(wm(o).inverted()@S@flip@SI@wm(o));bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    a['updated_objects'][name]['after']=sig(o);o['r36_lateral_control']='Escadaria no lado oposto da galeria, conforme foto oblíqua; objeto mantém escala positiva.'
for f in a['garden_flights']:
    for key in ('a','b'):f[key][0]=2*center-f[key][0]
for link in a['garden_landings']:
    for key in ('a','b'):link[key][0]=2*center-link[key][0]
a['garden_side_correction']='Lanços recuados no interior do jardim, no lado oposto aos arcos. Último lanço transversal desemboca atrás da laje; a escada da colunata está dentro do vão central.'

source=scene.objects[r['terrain'][0]['object']];allowed={i for i,m in enumerate(source.data.materials) if any(s in m.name.lower() for s in ('terreno','encosta','conten','solo e vegetação')) and not any(s in m.name.lower() for s in ('asfalto','passeio','pedonal','chile'))}
soilidx=next(i for i,m in enumerate(source.data.materials) if m.name=='RIO R36 | solo e vegetação baixa')
def road_points():
    ids={v for p in source.data.polygons if p.material_index not in allowed for v in p.vertices};return {tuple(round(c,5) for c in source.data.vertices[i].co) for i in ids}
roads=road_points();gal=a['gallery_after'];gp=SI@Vector(gal['origin_world']);gx0,gx1=gp.x,gp.x+gal['length_from_existing_controls_m'];gy=gp.y;depth=gal['depth_candidate_m'];gz=gp.z-.22
knots=a.get('profile',r['garden_profile_refinement']['profile_candidate_y_z'])
def profile(d):
    return float(np.interp(d,[p[0] for p in knots],[p[1] for p in knots]))
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def staircase(x,y):
    p=Vector((x,y));chosen=None
    for f in a['garden_flights']:
        aa,bb=Vector(f['a'][:2]),Vector(f['b'][:2]);u=(bb-aa).normalized();L=(bb-aa).length;t=(p-aa).dot(u);side=abs((p-aa).cross(u))
        if -.50<=t<=L+.50 and side<=f['width_candidate_m']/2+.08:
            z=f['a'][2]+(f['b'][2]-f['a'][2])*max(0,min(1,t/L));chosen=z-.40
    for link in a['garden_landings']:
        aa,bb=Vector(link['a']),Vector(link['b']);u=(bb-aa).normalized();L=(bb-aa).length;t=(p-aa).dot(u)
        if -.40<=t<=L+.40 and abs((p-aa).cross(u))<=link['width']/2+.08:chosen=link['z']-.31
    return chosen

rows=[]
for item in r['terrain']:
    o=scene.objects[item['object']];me=o.data;M=wm(o);I=M.inverted();before=sig(o)
    v=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',v);T=np.array(SI@M);local=v.reshape((-1,3))@T[:3,:3].T+T[:3,3]
    idx=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',idx);starts=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('loop_start',starts)
    mask=np.ones(len(me.polygons),dtype=bool)
    for axis,lo,hi in ((0,x0-2,gx1+1),(1,gy-depth-.5,35.55)):
        values=local[:,axis][idx];mask&=(np.maximum.reduceat(values,starts)>lo)&(np.minimum.reduceat(values,starts)<hi)
    if o==source:
        mi=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',mi);mask&=np.isin(mi,list(allowed))
    bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();region={bm.faces[int(i)] for i in np.flatnonzero(mask)}
    # Cortes no local exato da estrutura/lanços. Sem o corte, o limite de altura
    # antigo deixava vértices altos intocados e criava dentes no mesmo talude.
    xs={x0-2,x0,x1,x1+2,gx0,gx1,gx1+1,center-5.8,center,center+5.8}
    ys={gy-depth,gy,3.8,5,9,13.2,14.1,14.55,18.5,22.4,23.3,23.75,26.8,26.98,front+.15,35.55}
    for f in a['garden_flights']:
        for p in (f['a'],f['b']):
            xs.update((p[0]-.93,p[0]+.93));ys.update((p[1]-.93,p[1]+.93))
    for axis,value in [(U,x) for x in sorted(xs)]+[(N,y) for y in sorted(ys)]:
        faces=[f for f in region if f.is_valid and (o!=source or f.material_index in allowed)];geom=set(faces)
        for f in faces:geom.update(f.edges);geom.update(f.verts)
        result=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(P+axis*value),plane_no=M.to_3x3().transposed()@axis,clear_inner=False,clear_outer=False)
        for e in result['geom_cut']:
            if hasattr(e,'link_faces'):region.update(e.link_faces)
    moved=0;maxdelta=0;painted=0
    for vert in {v for f in region if f.is_valid for v in f.verts}:
        if o==source and any(f.material_index not in allowed for f in vert.link_faces):continue
        p=SI@M@vert.co;target=p.z
        if x0-2-.001<=p.x<=x1+2+.001 and 3.799<=p.y<=35.551:
            weight=ease((p.x-(x0-2))/2)*ease((x1+2-p.x)/2)
            desired=profile(p.y);step=staircase(p.x,p.y)
            if step is not None:desired=step
            if p.y<5:weight*=ease((p.y-3.8)/1.2)
            if back-.02<=p.y<=front+.15 and x0-.001<=p.x<=x1+.001:desired=floor-.22;weight=1
            target=p.z+(desired-p.z)*weight
        # Cavidades da galeria expostas, laje/colisor preservam o chão superior.
        if gx0-.001<=p.x<=gx1+.001 and gy-depth-.001<=p.y<=gy+.55:target=min(target,gz)
        if gx0<=p.x<=gx1 and gy+.55<p.y<=gy+6:
            w=1-ease((p.y-gy-.55)/5.45);target=target+(min(target,gz)-target)*w
        if abs(target-p.z)<.00001:continue
        w=M@vert.co;maxdelta=max(maxdelta,abs(target-w.z));w.z=target;vert.co=I@w;moved+=1
    if o==source:
        for f in region:
            if not f.is_valid or f.material_index not in allowed:continue
            p=SI@M@f.calc_center_median()
            if x0-1<=p.x<=x1+1 and 4.5<p.y<26.5:f.material_index=soilidx;painted+=1
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();item['after']=sig(o)
    o['r36_profile_correction']='Solo ajustado ao encontro das galerias, escadas internas e terraço, sem limiar Z deixando picos; vias/XY preservados.'
    rows.append({'object':o.name,'before':before,'after':item['after'],'changed_vertices':moved,'max_z_delta_candidate_m':maxdelta,'painted_faces':painted})
assert not roads-road_points(),'Mudança de circulação fora do escopo'
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
a['terrain_stage']='applied_pending_visual_review';a['terrain_correction']={'classification':'ADAPT_LOCAL','geometry':rows,'source_road_positions_preserved':len(roads),'dem_xy_road_width_changed':False,'reason':'A malha cede aos volumes reais da modelagem; cortes locais nos limites dos lanços e salas, removendo pontas deixadas pelo limiar de Z anterior. Não usar decoração para cobrir erros.'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':r['source_after'],'terrain':[(t['object'],t['changed_vertices']) for t in rows],'roads_preserved':len(roads)},ensure_ascii=False))
