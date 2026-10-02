"""Perfil escalonado do apoio e encontro contínuo encosta/ladeira.

Controles das estruturas e circulação existentes; proporções fotográficas
candidatas. Sem alterar DEM, larguras, traçado ou nível da praça.
"""
import bpy,bmesh,json,runpy,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];path=root/'docs/reports/blender/torre_galerias_r30b35.json';r=json.loads(path.read_text(encoding='utf8'));scene=bpy.context.scene
assert 'context_structure_refinement' not in r
assert Path(bpy.data.filepath).resolve()==(root/r['source_after']['file']).resolve()
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm,sig=h['world_matrix'],h['signature'];G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry']
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items()),'Alteração externa à sessão; revisar antes de editar'
R=Matrix(r['tower_alignment']['rotation_world']);RI=R.inverted();rx,ry,up=R@Vector((1,0,0)),R@Vector((0,1,0)),Vector((0,0,1));ring=r['tower_alignment']['rings_local'][0]
rear,land,y0,y1,base=ring;front=r['tower_alignment']['rings_local'][-1][1];cy=(y0+y1)/2;shoulder=65.4000015258789
body=scene.objects[r['tower_alignment']['objects'][0]];body_before=sig(body);glass=r['reference_detail_refinement']['support_glazing'];sill,head=glass['sill_z_candidate_m'],glass['head_z_candidate_m'];w=glass['glazing_width_candidate_m'];h0,h1=cy-w/2,cy+w/2
def v(x,y,z):return R@Vector((x,y,z))
# A face marítima permanece no controle arquitetônico. A face de encosta
# tem ressaltos em vez de um prisma reto; todas as medidas são candidatas.
steps=[(base,land),(39.,land),(39.,land+(front-land)*.28),(58.,land+(front-land)*.28),(58.,land+(front-land)*.68),(shoulder,land+(front-land)*.68),(68.85,front)]
g=G()
for pts in [[(rear,y0,base),(land,y0,base),(land,y1,base),(rear,y1,base)],[(rear,y0,base),(rear,h0,base),(rear,h0,sill),(rear,h0,head),(rear,h0,shoulder),(rear,y0,shoulder)],[(rear,h1,base),(rear,y1,base),(rear,y1,shoulder),(rear,h1,shoulder),(rear,h1,head),(rear,h1,sill)],[(rear,h0,base),(rear,h1,base),(rear,h1,sill),(rear,h0,sill)],[(rear,h0,head),(rear,h1,head),(rear,h1,shoulder),(rear,h0,shoulder)]]:g.poly([v(*p) for p in pts])
for (za,xa),(zb,xb) in zip(steps,steps[1:]):
    if abs(zb-za)<.0001:g.poly([v(xa,y0,za),v(xb,y0,zb),v(xb,y1,zb),v(xa,y1,za)])
    else:
        g.poly([v(xa,y0,za),v(xb,y0,zb),v(xb,y1,zb),v(xa,y1,za)])
        for yy in (y0,y1):g.poly([v(rear,yy,za),v(xa,yy,za),v(xb,yy,zb),v(rear,yy,zb)])
g.poly([v(rear,y0,shoulder),v(rear,y1,shoulder),v(rear,y1,68.85),v(rear,y0,68.85)])
g.poly([v(rear,y0,68.85),v(front,y0,68.85),v(front,y1,68.85),v(rear,y1,68.85)])
for pts in [[(rear,h0,sill),(rear,h0,head),(rear+.32,h0,head),(rear+.32,h0,sill)],[(rear,h1,sill),(rear+.32,h1,sill),(rear+.32,h1,head),(rear,h1,head)],[(rear,h0,sill),(rear+.32,h0,sill),(rear+.32,h1,sill),(rear,h1,sill)],[(rear,h0,head),(rear,h1,head),(rear+.32,h1,head),(rear+.32,h0,head)]]:g.poly([v(*p) for p in pts])
old=body.data;me=bpy.data.meshes.new(body.name+' | perfil escalonado R35');me.from_pydata(g.v,[],g.f);me.update()
for m in old.materials:me.materials.append(m)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();body.data=me
body['r35_shaft_profile']='Face marítima alinhada; face de encosta escalonada conforme silhueta das fotografias. Dimensões candidatas.'
# Elementos antigos realmente coincidentes com os substitutos permaneciam
# visíveis: arquivar explicitamente, conservando nomes/geometria/dependências.
archive=bpy.data.collections.new('REFERENCE | Apoio e terreno substituídos R35');scene.collection.children.link(archive);archive.hide_render=True;archive.hide_viewport=True;archive['boas_role']='reference_only'
obsolete=[o for o in scene.objects if (o.name.startswith('TERMINAL |') and any(c.name=='16 ENCOSTA | contencao da praca' for c in o.users_collection)) or o.name in ('TERRENO | Baixo','TERRENO | Encosta','TERRENO | Alto','ENTORNO LAC | Praca | balustrada modular')]
archived=[]
for o in obsolete:
    archived.append({'object':o.name,'before':sig(o),'collections_before':[c.name for c in o.users_collection]});archive.objects.link(o)
    for c in list(o.users_collection):
        if c!=archive:c.objects.unlink(o)
    o.hide_render=True;o.hide_set(True);o['boas_archive_reason']='Geometria legada sobreposta: substituída por apoio R35, terreno autoral corrigido ou balaustradas R34. Preservada para recuperação.'
source=scene.objects[r['terrain_names'][0]];allowed={i for i,m in enumerate(source.data.materials) if any(k in m.name.lower() for k in ('terreno','conten','encosta')) and not any(k in m.name.lower() for k in ('asfalto','pedonal','percurso','passeio','calçada','calcada','chile'))}
def road_points(me):
    ids={v for p in me.polygons if p.material_index not in allowed for v in p.vertices}
    return {tuple(round(c,5) for c in me.vertices[i].co) for i in ids}
roads=road_points(source.data)
def coords(o):
    a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a);m=np.array(wm(o));world=a.reshape((-1,3))@m[:3,:3].T+m[:3,3]
    return world,world@np.array(RI)[:3,:3].T
world,local=coords(source)
roadmat={i for i,m in enumerate(source.data.materials) if m.name in ('MVP | asfalto da ladeira','VIAS | passeio mineral claro')};roadids=np.array(sorted({v for p in source.data.polygons if p.material_index in roadmat for v in p.vertices}),dtype=int);rp=local[roadids];rp=rp[(rp[:,0]>-47)&(rp[:,0]<-24)&(rp[:,1]>-38)&(rp[:,1]<60)]
anchors=[]
for yy in range(-34,57):
    nearby=rp[np.abs(rp[:,1]-yy)<1.8];assert len(nearby),'Sem borda da via para controlar a encosta'
    # Ponto mais interior da faixa existente. Não altera a sua largura.
    xx=nearby[:,0].max();edge=nearby[nearby[:,0]>xx-.28];anchors.append((float(yy),float(edge[:,0].mean()),float(edge[:,2].mean())))
ay,ax,az=np.array(anchors).T
gallery=[]
for s in r['galleries']['segments']:
    p=RI@Vector(s['origin_world']);q=RI@(Vector(s['origin_world'])+Vector(s['along_world'])*s['length_from_existing_controls_m']);gallery.append((min(p.y,q.y),max(p.y,q.y),p,q,s['origin_world'][2]-.22))
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def boundary(yy):
    if yy<cy:
        a,b,p,q,z=gallery[0];t=max(0,min(1,(yy-p.y)/(q.y-p.y)));x=p.x+(q.x-p.x)*t
        k=ease((yy-b)/(cy-b)) if yy>b else 0
    else:
        a,b,p,q,z=gallery[1];t=max(0,min(1,(yy-p.y)/(q.y-p.y)));x=p.x+(q.x-p.x)*t
        k=ease((a-yy)/(a-cy)) if yy<a else 0
    return x+(front-x)*k,z+(69.64-z)*k
def profile(x,yy):
    ex=float(np.interp(yy,ay,ax));ez=float(np.interp(yy,ay,az));tx,tz=boundary(yy);d=x-ex
    if d<=.8:z=ez+5.5*max(0,d)/.8
    elif d<=3.2:z=ez+5.5+.08*(d-.8)
    else:z=ez+5.692+(tz-ez-5.692)*max(0,min(1,(x-ex-3.2)/(tx-ex-3.2)))
    support=ease(min((yy-y0+2.8)/2.8,(y1+2.8-yy)/2.8))
    if x<=rear:z=z+(min(z,ez+5.7)-z)*support
    return z,ex,tx,ez
rows=[]
for name in r['terrain_names']:
    o=scene.objects[name];before=sig(o);mesh=o.data;M=wm(o);inv=M.inverted();world,local=coords(o)
    locked={v for p in mesh.polygons if o==source and p.material_index not in allowed for v in p.vertices};moved=0;maximum=0
    for idx in np.flatnonzero((local[:,0]>-40)&(local[:,0]<5)&(local[:,1]>-34)&(local[:,1]<56)&(local[:,2]<69.85)):
        if int(idx) in locked:continue
        x,yy,z=local[idx];target,ex,tx,ez=profile(x,yy)
        if x<ex-.001 or x>tx+.00001:continue
        # Interiores previamente escavados não recebem terreno novamente.
        if rear-.0001<x<front+.0001 and y0-.0001<yy<y1+.0001:continue
        influence=ease(min((yy+34)/7,(56-yy)/8));newz=z+(target-z)*influence
        if abs(newz-z)<.00001:continue
        ww=Vector(world[idx]);ww.z=newz;mesh.vertices[int(idx)].co=inv@ww;moved+=1;maximum=float(max(maximum,abs(newz-z)))
    mesh.update()
    # Subtração do perfil escalonado do apoio, por intervalos de altura.
    world,local=coords(o);loops=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('vertex_index',loops);starts=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('loop_start',starts)
    mask=np.ones(len(mesh.polygons),dtype=bool)
    for axis,low,high in ((0,rear,front),(1,y0,y1),(2,base,69.795)):
        vals=local[:,axis][loops];mask&=(np.maximum.reduceat(vals,starts)>=low-.001)&(np.minimum.reduceat(vals,starts)<=high+.001)
    if o==source:
        mi=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('material_index',mi);mask&=np.isin(mi,list(allowed))
    bm=bmesh.new();bm.from_mesh(mesh);bm.faces.ensure_lookup_table();region={bm.faces[int(i)] for i in np.flatnonzero(mask)}
    planes=[(rx,rear),(ry,y0),(ry,y1),(up,base),(up,69.795)]+[(rx,x) for z,x in steps]+[(up,z) for z,x in steps]
    for axis,value in planes:
        faces=[f for f in region if f.is_valid and (o!=source or f.material_index in allowed)];geom=set(faces)
        for f in faces:geom.update(f.edges);geom.update(f.verts)
        result=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=inv@(axis*value),plane_no=M.to_3x3().transposed()@axis,clear_inner=False,clear_outer=False)
        for item in result['geom_cut']:
            if hasattr(item,'link_faces'):region.update(item.link_faces)
    removed=[]
    for f in region:
        if not f.is_valid or (o==source and f.material_index not in allowed):continue
        p=RI@M@f.calc_center_median();limit=front
        for (za,xa),(zb,xb) in zip(steps,steps[1:]):
            if za<=p.z<=zb and zb>za:limit=xa+(xb-xa)*(p.z-za)/(zb-za);break
        if rear+.00001<p.x<limit-.00001 and y0+.00001<p.y<y1-.00001 and base+.00001<p.z<69.79499:removed.append(f)
    bmesh.ops.delete(bm,geom=removed,context='FACES_ONLY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
    rows.append({'object':name,'before':before,'after':sig(o),'moved_vertices':moved,'removed_inside_support_faces':len(removed),'max_z_delta_m':maximum})
# Solo nos taludes e pedra na contenção: máscara sem deslocamento geométrico.
world,local=coords(source);attr=source.data.attributes['boas_r35_solo_encosta'];values=np.empty(len(world),dtype=np.float32);attr.data.foreach_get('value',values)
for idx in np.flatnonzero((local[:,0]>-40)&(local[:,0]<5)&(local[:,1]>-34)&(local[:,1]<56)):
    x,yy,z=local[idx];target,ex,tx,ez=profile(x,yy)
    if ex<=x<=tx:values[idx]=ease((x-ex-.65)/1.0)*ease(min((yy+34)/5,(56-yy)/5))
attr.data.foreach_set('value',values)
assert not roads-road_points(source.data),'Vértice de via mudou'
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items()),'Componente protegido mudou'
for row in rows:next(g for g in r['terrain_refinement']['geometry'] if g['object']==row['object'])['after']=row['after']
r['context_structure_refinement']={'classification':'ADAPT_LOCAL','reference_media_ids':r['reference_media_ids'],'support_before':body_before,'support_after':sig(body),'support_back_profile_local_z_x_candidate_m':steps,'support_profile_verified_real_dimensions':None,'archived_overlapping_legacy_objects':archived,'road_edge_existing_geometry_samples_y_x_z':anchors,'terrain':rows,'terrain_method':'Contenção e talude reconstituídos entre a borda interior existente da ladeira e o pé das galerias/laje; remove depressões herdadas do apoio antigo e pontas na transição. Perfil fotográfico candidato, não levantamento topográfico.','road_positions_preserved':len(roads),'road_xy_width_dem_changed':False,'visual_review':'pending'}
r.pop('localized_scene_review',None);scene['architecture_revision']='R30B.35 | apoio escalonado, galerias vazadas e encosta pela borda real da ladeira'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
