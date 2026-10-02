"""Ajuste após comparação: jardim inclinado, caminhos estreitos e colunata exposta."""
import bpy,bmesh,json,runpy,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));scene=bpy.context.scene
assert 'garden_profile_refinement' not in r and Path(bpy.data.filepath).resolve()==(root/r['source_after']['file']).resolve()
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry']
S=Matrix(r['layout']['frame_world']);SI=S.inverted();U=S.col[0].xyz;N=S.col[1].xyz;P=S.col[3].xyz;UP=Vector((0,0,1))
x0,x1,back,front=r['layout']['colonnade_extent_candidate'];levels=r['layout']['garden_levels_candidate_m'];floor=r['layout']['colonnade_floor_candidate_m'];roof=r['layout']['colonnade_roof_candidate_m'];center=r['layout']['palace_edge_length_m']/2;stairx=x1-1.05;walkstart=center-1.6
col=bpy.data.collections['HERO | Terraços Rio Branco | fotografia R36'];ivory=bpy.data.materials['RIO R34 | ornatos e cornijas marfim'];stone=bpy.data.materials['RIO R34 | embasamento de pedra'];pave=bpy.data.materials['PRACA R35 | paralelepípedos métricos'];wallmat=bpy.data.materials['RIO R36 | cantaria dos terraços'];soil=bpy.data.materials['RIO R36 | solo e vegetação baixa']
changes={}
def replace(name,g):
    o=scene.objects[name];before=sig(o);m=o.data.materials[0];tmp=g.object('TEMP | terraço',col,m,S);o.data=tmp.data;o.data.transform(wm(o).inverted()@S);bpy.data.objects.remove(tmp,do_unlink=True);changes[name]={'before':before,'after':sig(o)}
def prism(g,outline,bottom,top):
    g.poly([(x,y,top) for x,y in outline]);g.poly([(x,y,bottom) for x,y in reversed(outline)])
    for a,b in zip(outline,outline[1:]+outline[:1]):g.poly([(*a,bottom),(*b,bottom),(*b,top),(*a,top)])
outline=[(center-5.8,3.8),(center+5.8,3.8)]+[(center+5.8*math.cos(j*math.pi/40),3.8+6.3*math.sin(j*math.pi/40)) for j in range(41)]
g=G();prism(g,outline,levels[2]-.3,69.67);replace('RIO R36 | Bastião curvo sob o pórtico',g)
g=G()
for z in np.arange(levels[2],69.5,.72):
    for a,b in zip(outline[2:],outline[3:]):g.bar((*a,float(z)),(*b,float(z)),.025,6)
replace('RIO R36 | Juntas horizontais da cantaria',g)
walk=G();retaining=G();rail=G()
def railing(a,b,z):
    a,b=Vector(a),Vector(b);d=(b-a).normalized();normal=Vector((-d.y,d.x,0));L=(b-a).length
    for zz,w,hh in ((z+.12,.24,.18),(z+1.04,.30,.15)):rail.box((a+b)/2+UP*zz,(L,w,hh),(d,normal,UP))
    count=max(2,round(L/.42))
    for j in range(count+1):
        v=a+(b-a)*j/count;rail.lathe((v.x,v.y,z+.2),[(.07,0),(.07,.1),(.043,.2),(.078,.38),(.056,.54),(.045,.69),(.065,.77)],8)
    for v in (a,b):rail.box((v.x,v.y,z+.60),(.36,.36,1.20));rail.box((v.x,v.y,z+1.24),(.46,.46,.13))
railing((x0,front,0),(x1,front,0),roof)
for x in (x0,x1):railing((x,back,0),(x,front,0),roof)
for d,z in ((13.7,levels[1]),(22.9,levels[2])):
    walk.box(((walkstart+stairx)/2,d,z-.13),(stairx-walkstart,1.05,.26))
    retaining.box(((walkstart+stairx)/2,d+.7,z-1.2),(stairx-walkstart,.42,2.4))
    railing((walkstart,d+.75,0),(stairx-.9,d+.75,0),z)
replace('RIO R36 | Passeios dos patamares',walk);replace('RIO R36 | Contenções dos patamares',retaining);replace('RIO R36 | Balaustradas dos terraços',rail)
replace('COL R36 | Passeios dos patamares',walk)

# Perfil contínuo de jardim; retenções pequenas e taludes entre patamares.
source=scene.objects[r['terrain'][0]['object']];allowed={i for i,m in enumerate(source.data.materials) if any(s in m.name.lower() for s in ('terreno','encosta','conten')) and not any(s in m.name.lower() for s in ('asfalto','passeio','pedonal','chile'))}
def road_positions():return {tuple(round(v,5) for v in source.data.vertices[i].co) for p in source.data.polygons if p.material_index not in allowed for i in p.vertices}
roads=road_positions();soilidx=len(source.data.materials);source.data.materials.append(soil);allowed.add(soilidx)
knots=[(3.8,69.64),(5.,levels[1]+3.5),(13.2,levels[1]-.20),(14.1,levels[1]-.20),(14.55,levels[1]-2.4),(22.4,levels[2]-.20),(23.3,levels[2]-.20),(23.75,levels[2]-2.4),(26.80,roof-.25),(26.98,floor-.22),(33.15,floor-.22),(35.55,38.9)]
def profile(d):
    for (a,za),(b,zb) in zip(knots,knots[1:]):
        if a<=d<=b:return za+(zb-za)*(d-a)/(b-a)
    return knots[0][1] if d<knots[0][0] else knots[-1][1]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
rows=[]
for item in r['terrain']:
    o=scene.objects[item['object']];me=o.data;M=wm(o);I=M.inverted();before=sig(o)
    a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);A=np.array(SI@M);local=a.reshape((-1,3))@A[:3,:3].T+A[:3,3]
    idx=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',idx);starts=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('loop_start',starts);mask=np.ones(len(me.polygons),dtype=bool)
    for axis,low,high in ((0,x0-2,x1+2),(1,3.8,35.55),(2,-100,69.86)):
        vals=local[:,axis][idx];mask&=(np.maximum.reduceat(vals,starts)>low)&(np.minimum.reduceat(vals,starts)<high)
    if o==source:
        mi=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',mi);mask&=np.isin(mi,list(allowed))
    bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();region={bm.faces[int(i)] for i in np.flatnonzero(mask)}
    for axis,val in [(U,v) for v in (x0-2,x0,x1,x1+2,walkstart,stairx-.99,stairx+.99)]+[(N,v) for v,z in knots]:
        faces=[f for f in region if f.is_valid and (o!=source or f.material_index in allowed)];geom=set(faces)
        for f in faces:geom.update(f.edges);geom.update(f.verts)
        cut=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(P+axis*val),plane_no=M.to_3x3().transposed()@axis,clear_inner=False,clear_outer=False)
        for element in cut['geom_cut']:
            if hasattr(element,'link_faces'):region.update(element.link_faces)
    moved=0
    for v in {v for f in region if f.is_valid for v in f.verts}:
        if o==source and any(f.material_index not in allowed for f in v.link_faces):continue
        p=SI@M@v.co
        if not(x0-2.001<=p.x<=x1+2.001 and 3.799<=p.y<=35.551 and p.z<69.86):continue
        target=profile(p.y)
        # Ajusta o solo ao intradorso das escadas existentes, mantendo o jardim adjacente.
        if abs(p.x-stairx)<.98:
            for f in r['layout']['flights']:
                if f['start_d']<=p.y<=f['end_d']+1:target=min(target,f['from_z']+(f['to_z']-f['from_z'])*min(1,(p.y-f['start_d'])/(f['end_d']-f['start_d']))-.48)
        # Colunata escavada até o piso; fora de seus limites o solo transita lateralmente.
        weight=ease((p.x-(x0-2))/2)*ease((x1+2-p.x)/2)
        if back-.02<=p.y<=front+.15 and x0-.001<=p.x<=x1+.001:weight=1;target=floor-.22
        if p.y<26.8:weight*=ease((p.y-3.8)/1.2)
        newz=p.z+(target-p.z)*weight
        if abs(newz-p.z)<.00001:continue
        w=M@v.co;w.z=newz;v.co=I@w;moved+=1
    painted=0
    if o==source:
        for f in region:
            if not f.is_valid or f.material_index not in allowed:continue
            p=SI@M@f.calc_center_median()
            if x0-1<=p.x<=x1+1 and 4.5<p.y<26.5:f.material_index=soilidx;painted+=1
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();after=sig(o);item['after']=after
    rows.append({'object':o.name,'before':before,'after':after,'changed_vertices':moved,'garden_material_faces':painted})
assert not roads-road_positions(),'Via existente mudou'
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
r['garden_profile_refinement']={'reason':'Comparação com oblíqua de 2022: solo cobria os vãos, patamares largos e embasamento curvo curto. Reperfilamento local, caminhos menores e base prolongada.','classification':'ADAPT_LOCAL','updated_objects':changes,'terrain':rows,'profile_candidate_y_z':knots,'road_positions_preserved':len(roads),'road_width_xy_dem_changed':False,'verified_real_dimensions':None,'visual_review':'pending'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
