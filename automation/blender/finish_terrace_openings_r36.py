"""Abre o solo nos volumes das galerias e remove barreiras nas escadas R36."""
import bpy,bmesh,json,runpy,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));scene=bpy.context.scene
assert 'opening_finish' not in r
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry'];S=Matrix(r['layout']['frame_world']);up=Vector((0,0,1));SI=S.inverted()
a=r['access_connection_correction'];center=r['layout']['palace_edge_length_m']/2;x0,x1,back,front=r['layout']['colonnade_extent_candidate'];roof=r['layout']['colonnade_roof_candidate_m'];levels=r['layout']['garden_levels_candidate_m'];floor=r['layout']['colonnade_floor_candidate_m']
col=bpy.data.collections['HERO | Terraços Rio Branco | fotografia R36'];cc=bpy.data.collections['COLLISION | Terraços Rio Branco R36'];stone=bpy.data.materials['RIO R34 | embasamento de pedra'];ivory=bpy.data.materials['RIO R34 | ornatos e cornijas marfim'];pave=bpy.data.materials['PRACA R35 | paralelepípedos métricos']
props={'boas_revision':'R30B.36','boas_role':'visual_structure','classification':'ADAPT_LOCAL','reference_status':'partial','boas_location_candidate':'palacio-rio-branco','dimensions_status':'candidatas; continuidade arquitetônica, não dimensões levantadas'}
def replace(name,g):
    o=scene.objects[name];old=o.data;tmp=g.object('TEMP | acabamento R36',col,old.materials[0],S);o.data=tmp.data;o.data.transform(wm(o).inverted()@S);bpy.data.objects.remove(tmp,do_unlink=True)
    if not old.users:bpy.data.meshes.remove(old)

# A escada superior precisa chegar ao terraço curvo por uma abertura, não
# terminar no ar nem atravessar balaústres. Patamar e proxy próprios.
sx=a['garden_flights'][0]['a'][0];entry=center-5.0;g=G();g.box(((sx+entry)/2,4.3,levels[0]-.15),(entry-sx,1.7,.30))
o=g.object('RIO R36 | Patamar de acesso ao terraço curvo',col,pave,S,props=props);r['created_objects'].append(o.name)
o=g.object('COL R36 | Patamar de acesso ao terraço curvo',cc,stone,S,props={**props,'boas_role':'static_collider'});o.hide_set(True);o.hide_render=True;r['colliders'].append(o.name)
g=G();limit=math.pi-.32
for j in range(40):
    t=j*limit/40;t2=(j+1)*limit/40;g.bar((center+5.8*math.cos(t),3.8+6.3*math.sin(t),70.84),(center+5.8*math.cos(t2),3.8+6.3*math.sin(t2),70.84),.07,8)
for j in range(28):
    t=j*limit/27;g.lathe((center+5.8*math.cos(t),3.8+6.3*math.sin(t),69.85),[(.06,0),(.06,.12),(.08,.42),(.04,.69),(.06,.92)],8)
replace('RIO R36 | Guarda do terraço curvo',g)
rail,retaining=G(),G()
def railing(p,q,z):
    p,q=Vector(p),Vector(q);u=(q-p).normalized();n=Vector((-u.y,u.x,0));L=(q-p).length
    for zz,w,hh in ((z+.12,.24,.18),(z+1.04,.30,.15)):rail.box((p+q)/2+up*zz,(L,w,hh),(u,n,up))
    count=max(2,round(L/.42))
    for j in range(count+1):v=p+(q-p)*j/count;rail.lathe((v.x,v.y,z+.2),[(.07,0),(.07,.1),(.043,.2),(.078,.38),(.056,.54),(.045,.69),(.065,.77)],8)
    for v in (p,q):rail.box((v.x,v.y,z+.60),(.36,.36,1.2));rail.box((v.x,v.y,z+1.24),(.46,.46,.13))
railing((x0,front,0),(x1,front,0),roof)
for x in (x0,x1):railing((x,back,0),(x,front,0),roof)
for j,(y,z) in enumerate(((13.7,levels[1]),(22.9,levels[2]))):
    lo=a['garden_flights'][j]['a'][0];hi=center+1.6;intervals=[(lo,hi)];railintervals=[(lo+.9,hi)]
    if j==0:
        nextx=a['garden_flights'][1]['a'][0];intervals=[(lo,nextx-.98),(nextx+.98,hi)];railintervals=[(lo+.9,nextx-.98),(nextx+.98,hi)]
    for left,right in intervals:
        if right>left:retaining.box(((left+right)/2,y+.70,z-1.2),(right-left,.42,2.4))
    for left,right in railintervals:
        if right-left>.25:railing((left,y+.75,0),(right,y+.75,0),z)
replace('RIO R36 | Balaustradas dos terraços',rail);replace('RIO R36 | Contenções dos patamares',retaining)

# Não bastava mover vértices: faces de contenções antigas ainda cruzavam os
# interiores. Subtrai faces do terreno dentro dos volumes, delimitados pela
# arquitetura e fechados pelos pisos, paredes e lajes já modelados.
rooms=[r['preserved_gallery_connection']['segment'],a['gallery_before']]
source=scene.objects[r['terrain'][0]['object']];allowed={i for i,m in enumerate(source.data.materials) if any(k in m.name.lower() for k in ('terreno','encosta','conten','solo e vegetação')) and not any(k in m.name.lower() for k in ('asfalto','passeio','pedonal','chile'))}
def road_positions():
    ids={v for f in source.data.polygons if f.material_index not in allowed for v in f.vertices};return {tuple(round(k,5) for k in source.data.vertices[i].co) for i in ids}
roads=road_positions();rows=[]
for item in r['terrain']:
    o=scene.objects[item['object']];me=o.data;M=wm(o);I=M.inverted();before=sig(o);bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();removed=0
    # A região de trabalho é pequena; evita cortes em toda a cidade.
    coords=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',coords);A=np.array(M);world=coords.reshape((-1,3))@A[:3,:3].T+A[:3,3]
    inds=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',inds);starts=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('loop_start',starts);mask=np.zeros(len(me.polygons),dtype=bool)
    for s in rooms:
        p,u,n=Vector(s['origin_world']),Vector(s['along_world']),Vector(s['outward_world']);d=world-np.array(p);xx=d@np.array(u);yy=d@np.array(n);zz=world[:,2];v=(xx>=-.2)&(xx<=s['length_from_existing_controls_m']+.2)&(yy>=-s['depth_candidate_m']-.2)&(yy<=.9)&(zz>=p.z-.3)&(zz<=p.z+s['height_candidate_m']+.1);mask|=np.logical_or.reduceat(v[inds],starts)
    if o==source:
        mi=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',mi);mask&=np.isin(mi,list(allowed))
    region={bm.faces[int(i)] for i in np.flatnonzero(mask)}
    for s in rooms:
        p,u,n=Vector(s['origin_world']),Vector(s['along_world']),Vector(s['outward_world']);L=s['length_from_existing_controls_m'];dep=s['depth_candidate_m'];z0=p.z-.18;z1=p.z+s['height_candidate_m']-.01
        for axis,value in ((u,-.10),(u,L+.10),(n,-dep-.10),(n,.8),(up,z0-p.z),(up,z1-p.z)):
            faces=[f for f in region if f.is_valid and (o!=source or f.material_index in allowed)];geom=set(faces)
            for f in faces:geom.update(f.edges);geom.update(f.verts)
            res=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(p+axis*value),plane_no=M.to_3x3().transposed()@axis,clear_inner=False,clear_outer=False)
            for e in res['geom_cut']:
                if hasattr(e,'link_faces'):region.update(e.link_faces)
        doomed=[]
        for f in region:
            if not f.is_valid or (o==source and f.material_index not in allowed):continue
            w=M@f.calc_center_median();d=w-p
            if -.10001<d.dot(u)<L+.10001 and -dep-.10001<d.dot(n)<.80001 and z0-.00001<w.z<z1+.00001:doomed.append(f)
        removed+=len(doomed);bmesh.ops.delete(bm,geom=doomed,context='FACES')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();item['after']=sig(o);rows.append({'object':o.name,'before':before,'after':item['after'],'intersecting_soil_faces_removed':removed})
assert not roads-road_positions(),'Vias mudaram'
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items()),'Componente protegido mudou'
r['opening_finish']={'classification':'ADAPT_LOCAL','reason':'Faces de terreno/contenção antigas dentro das galerias removidas em recorte volumétrico; piso/laje próprios permanecem. Patamar de acesso e aberturas em guarda-corpo/contenção evitam escadas terminando no ar ou atravessando barreiras.','terrain':rows,'upper_access_height_delta_m':.03,'road_positions_preserved':len(roads),'road_width_xy_dem_changed':False,'visual_review':'pending'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':r['source_after'],'removed_soil_faces':[t['intersecting_soil_faces_removed'] for t in rows]},ensure_ascii=False))
