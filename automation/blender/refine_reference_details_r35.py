"""Vãos do apoio, pé da encosta e escavação do proxy na janela adotada.

Proporções fotográficas candidatas; controles XY/la​​je e vias preservados.
"""
import bpy,bmesh,json,hashlib,runpy,math
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];path=root/'docs/reports/blender/torre_galerias_r30b35.json';r=json.loads(path.read_text(encoding='utf8'));scene=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(root/r['source_after']['file']).resolve()
assert 'reference_detail_refinement' not in r
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix']
G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry']
R=Matrix(r['tower_alignment']['rotation_world']);RI=R.inverted();up=Vector((0,0,1));rx,ry=R@Vector((1,0,0)),R@Vector((0,1,0))
rear=r['tower_alignment']['sea_face_x_from_upper_wall_m'];cy=r['tower_alignment']['center_y_from_upper_floor_m'];rings=r['tower_alignment']['rings_local'];base=rings[0][4];shoulder=rings[-2][4];land=rings[0][1];half=(rings[0][3]-rings[0][2])/2
before={n:sig(scene.objects[n]) for n in [r['tower_alignment']['objects'][0]]+r['terrain_names']}
new=[]
def replace(o,g):
    old=o.data;me=bpy.data.meshes.new(o.name+' | R35 revisão de vãos');me.from_pydata(g.v,[],g.f);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    for m in old.materials:me.materials.append(m)
    o.data=me
    if not old.users:bpy.data.meshes.remove(old)
def v(x,y,z):return R@Vector((x,y,z))
body=scene.objects[r['tower_alignment']['objects'][0]];cream=body.data.materials[0];col=body.users_collection[0]
width=2*half*.58;sill=base+(shoulder-base)*.52;head=shoulder-.7;h0,h1=cy-width/2,cy+width/2;y0,y1=cy-half,cy+half
g=G()
# Casca contínua: a face marítima tem um vão real, não vidro sobre concreto.
for pts in [[(rear,y0,base),(land,y0,base),(land,y1,base),(rear,y1,base)],[(land,y0,base),(land,y0,shoulder),(land,y1,shoulder),(land,y1,base)],[(rear,y0,base),(rear,y0,shoulder),(land,y0,shoulder),(land,y0,base)],[(rear,y1,base),(land,y1,base),(land,y1,shoulder),(rear,y1,shoulder)],[(rear,y0,base),(rear,h0,base),(rear,h0,sill),(rear,h0,head),(rear,h0,shoulder),(rear,y0,shoulder)],[(rear,h1,base),(rear,y1,base),(rear,y1,shoulder),(rear,h1,shoulder),(rear,h1,head),(rear,h1,sill)],[(rear,h0,base),(rear,h1,base),(rear,h1,sill),(rear,h0,sill)],[(rear,h0,head),(rear,h1,head),(rear,h1,shoulder),(rear,h0,shoulder)]]:
    g.poly([v(*p) for p in pts])
for pts in [[(rear,h0,sill),(rear,h0,head),(rear+.32,h0,head),(rear+.32,h0,sill)],[(rear,h1,sill),(rear+.32,h1,sill),(rear+.32,h1,head),(rear,h1,head)],[(rear,h0,sill),(rear+.32,h0,sill),(rear+.32,h1,sill),(rear,h1,sill)],[(rear,h0,head),(rear,h1,head),(rear+.32,h1,head),(rear+.32,h0,head)]]:
    g.poly([v(*p) for p in pts])
# Consolo superior herdado: encaixe permanece na mesma laje.
lower=[v(x,y,shoulder) for x,y in [(rear,y0),(land,y0),(land,y1),(rear,y1)]]
last=rings[-1];upper=[v(x,y,last[4]) for x,y in [(last[0],last[2]),(last[1],last[2]),(last[1],last[3]),(last[0],last[3])]]
for j in range(4):g.poly([lower[j],lower[(j+1)%4],upper[(j+1)%4],upper[j]])
g.poly(upper);replace(body,g)
body['r35_window_evidence']='elevador-lacerda-detail-2ab9cfcbccc1; faixa envidraçada vertical observada sob a passarela'
body['r35_window_status']='Proporção fotográfica candidata; medidas reais não levantadas'
body['r35_shaft_profile']='Faces laterais retilíneas; removida oscilação de largura entre anéis legados'
glass=bpy.data.materials.new('LAC R35 | vidro da faixa vertical do apoio');glass.use_nodes=True;bs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.18,.22,.21,1);bs.inputs['Roughness'].default_value=.17;bs.inputs['Transmission Weight'].default_value=.65;bs.inputs['IOR'].default_value=1.48;bs.inputs['Alpha'].default_value=.72;glass.diffuse_color=(.18,.22,.21,.72);glass.surface_render_method='DITHERED'
props={'boas_location_id':'elevador-lacerda','boas_revision':'R30B.35','boas_role':'visual_architecture','classification':'ADAPT_LOCAL','reference_status':'partial','reference_media_id':'elevador-lacerda-detail-2ab9cfcbccc1','real_measurements':None}
frame=G();panes=G();columns=3;rows=4;mullion=.12;transom=.19
for j in range(columns+1):frame.box(v(rear-.035,h0+j*width/columns,(sill+head)/2),(.16,mullion,head-sill+.18),(rx,ry,up))
for k in range(rows+1):frame.box(v(rear-.035,cy,sill+k*(head-sill)/rows),(.16,width+.12,transom),(rx,ry,up))
for j in range(columns):
    for k in range(rows):panes.box(v(rear+.13,h0+(j+.5)*width/columns,sill+(k+.5)*(head-sill)/rows),(.018,width/columns-mullion,(head-sill)/rows-transom),(rx,ry,up))
for title,buf,mat in [('Caixilhos verticais do apoio',frame,cream),('Vidros da faixa vertical do apoio',panes,glass)]:
    o=buf.object('LAC R35 | '+title,col,mat,props=props);new.append(o.name)
details=G()
for y in (h0-.20,h1+.20):details.box(v(rear-.055,y,(base+shoulder)/2),(.11,.16,shoulder-base),(rx,ry,up))
details.box(v(rear-.16,cy,sill-.24),(.42,2*half+.12,.34),(rx,ry,up))
o=details.object('LAC R35 | Pilastras e faixa sob os vãos',col,cream,props=props);new.append(o.name)

source=scene.objects[r['terrain_names'][0]];me=source.data
allowed={i for i,m in enumerate(me.materials) if any(k in m.name.lower() for k in ('terreno','conten','encosta')) and not any(k in m.name.lower() for k in ('asfalto','pedonal','percurso','passeio','calçada','calcada','chile'))}
def road_points(me):
    ids={v for p in me.polygons if p.material_index not in allowed for v in p.vertices}
    return {tuple(round(c,5) for c in me.vertices[i].co) for i in ids}
roads=road_points(me)
def coords(o):
    a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a);m=np.array(wm(o));return a.reshape((-1,3))@m[:3,:3].T+m[:3,3]
me.calc_loop_triangles();tri=list(me.loop_triangles);bvh=BVHTree.FromPolygons([wm(source)@v.co for v in me.vertices],[list(t.vertices) for t in tri],all_triangles=True);tm=[me.polygons[t.polygon_index].material_index for t in tri]
anchors=r['terrain_refinement']['support_profile_anchors'];transition=r['terrain_refinement']['support_lateral_transition'];a0,a1=transition['limits_y_from_upper_floor_m'];b0,b1=transition['full_weight_y_from_support_m']
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def weight(y):
    if y<b0:return ease((y-a0)/(b0-a0))
    if y>b1:return ease((a1-y)/(a1-b1))
    return 1
def az(y,key):
    if y<=anchors[0]['y']:return anchors[0][key]
    if y>=anchors[-1]['y']:return anchors[-1][key]
    for a,b in zip(anchors,anchors[1:]):
        if a['y']<=y<=b['y']:return a[key]+(b[key]-a[key])*(y-a['y'])/(b['y']-a['y'])
ground_rows=[]
for name in r['terrain_names']:
    o=scene.objects[name];mesh=o.data;M=wm(o);I=M.inverted();world=coords(o);local=world@np.array(RI)[:3,:3].T
    ids=np.flatnonzero((local[:,0]>=-22)&(local[:,0]<=rear+.2501)&(local[:,1]>=a0)&(local[:,1]<=a1));locked=set()
    if o==source:locked={v for p in mesh.polygons if p.material_index not in allowed for v in p.vertices}
    moved=0
    for idx in ids:
        if int(idx) in locked:continue
        w=Vector(world[idx]);p=RI@w
        if o!=source:
            hit=bvh.ray_cast(Vector((w.x,w.y,150)),Vector((0,0,-1)),250)
            if hit[0] is None or tm[hit[2]] not in allowed:continue
        delta=(az(p.y,'z22')-az(p.y,'z20'))*min(1,(p.x+22)/(rear+22))*weight(p.y)
        if p.x>rear:delta*=1-ease((p.x-rear)/.25)
        if abs(delta)<.00001:continue
        w.z+=delta;mesh.vertices[int(idx)].co=I@w;moved+=1
    mesh.update();ground_rows.append({'object':name,'changed_vertices':moved})

# O proxy simplificado tinha triângulos grandes cruzando os interiores.
# Corta pelo volume arquitetônico, independentemente do centro do triângulo.
# O piso da praça é sustentado pelos colliders de laje separados existentes.
proxy=scene.objects[r['terrain_names'][1]];mesh=proxy.data;M=wm(proxy);I=M.inverted();world=coords(proxy)
loops=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('vertex_index',loops);starts=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('loop_start',starts)
regions=[]
for s in r['galleries']['segments']:
    delta=world-np.array(s['origin_world']);x=delta@np.array(s['along_world']);y=delta@np.array(s['outward_world']);L=s['length_from_existing_controls_m'];depth=s['depth_candidate_m']+.15
    mask=(np.maximum.reduceat(x[loops],starts)>-.01)&(np.minimum.reduceat(x[loops],starts)<L+.01)&(np.maximum.reduceat(y[loops],starts)>-depth-.01)&(np.minimum.reduceat(y[loops],starts)<.01)
    regions.append(np.flatnonzero(mask))
bm=bmesh.new();bm.from_mesh(mesh);bm.faces.ensure_lookup_table();regions=[{bm.faces[int(i)] for i in ids} for ids in regions];room_rows=[]
for s,region in zip(r['galleries']['segments'],regions):
    p,u,n=Vector(s['origin_world']),Vector(s['along_world']),Vector(s['outward_world']);L=s['length_from_existing_controls_m'];depth=s['depth_candidate_m']+.15
    for axis,val in ((u,0),(u,L),(n,0),(n,-depth)):
        faces=[f for f in region if f.is_valid];geom=set(faces)
        for f in faces:geom.update(f.edges);geom.update(f.verts)
        cut=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(p+axis*val),plane_no=M.to_3x3().transposed()@axis,clear_inner=False,clear_outer=False)
        for item in cut['geom_cut']:
            if hasattr(item,'link_faces'):region.update(item.link_faces)
    changed=0
    for vertex in {v for f in region if f.is_valid for v in f.verts}:
        w=M@vertex.co;delta=w-p;x,y=delta.dot(u),delta.dot(n)
        if -.0001<=x<=L+.0001 and -depth-.0001<=y<=.0001 and w.z>p.z-.22:
            w.z=p.z-.22;vertex.co=I@w;changed+=1
    room_rows.append({'segment':s['name'],'changed_vertices':changed,'domain_local':[0,L,-depth,0],'plaza_collision':'Laje superior separada, mesma cota herdada'})
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
assert not roads-road_points(source.data),'Pista alterada'

# Classifica visualmente solo e rocha apenas na encosta corrigida.
# Não desloca a superfície, não altera materiais de circulação.
world=coords(source);local=world@np.array(RI)[:3,:3].T;values=np.zeros(len(world),dtype=np.float32)
for idx in np.flatnonzero((local[:,0]>=-30)&(local[:,0]<=rear+.25)&(local[:,1]>=a0)&(local[:,1]<=a1)):
    x,y=local[idx,:2];values[idx]=weight(y)*ease((x+30)/3)*(1-ease((x-rear)/.25) if x>rear else 1)
for s in r['galleries']['segments']:
    delta=world-np.array(s['origin_world']);x=delta@np.array(s['along_world']);y=delta@np.array(s['outward_world']);L=s['length_from_existing_controls_m']
    region=(x>0)&(x<L)&(y>0)&(y<20);v=np.clip(np.minimum(x,L-x)/1.5,0,1)*np.clip(1-np.maximum(0,y-8)/12,0,1)
    values=np.maximum(values,np.where(region,v,0).astype(np.float32))
values*=np.clip((world[:,2]-az(cy,'z22'))/6,0,1).astype(np.float32)
attr=source.data.attributes.new('boas_r35_solo_encosta','FLOAT','POINT');attr.data.foreach_set('value',values);materials=[]
for idx in sorted(allowed):
    old=source.data.materials[idx]
    if 'pedra irregular da conten' not in old.name.lower():continue
    mat=old.copy();mat.name='ENV R35 | terreno e rocha junto ao apoio';source.data.materials[idx]=mat;nt=mat.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');original=out.inputs['Surface'].links[0].from_socket
    pos=nt.nodes.new('ShaderNodeNewGeometry').outputs['Position'];noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.55;noise.inputs['Detail'].default_value=3;nt.links.new(pos,noise.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.13,.10,.055,1);ramp.color_ramp.elements[1].color=(.17,.26,.075,1);nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    soil=nt.nodes.new('ShaderNodeBsdfPrincipled');soil.inputs['Roughness'].default_value=.9;nt.links.new(ramp.outputs['Color'],soil.inputs['Base Color'])
    grain=nt.nodes.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=65;nt.links.new(pos,grain.inputs['Vector']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.2;bump.inputs['Distance'].default_value=.009;nt.links.new(grain.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],soil.inputs['Normal'])
    mask=nt.nodes.new('ShaderNodeAttribute');mask.attribute_name=attr.name;mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(mask.outputs['Fac'],mix.inputs[0]);nt.links.new(original,mix.inputs[1]);nt.links.new(soil.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface']);materials.append(mat.name)
assert all(sig(scene.objects[n])==v for n,v in r['protected_signatures'].items()),'Componente fora do escopo alterado'
refs=json.loads((root/'artifacts/palacio-rio-branco/reference_detail_r35.json').read_text(encoding='utf8'))['media_ids'];r['reference_media_ids']=list(dict.fromkeys(r['reference_media_ids']+refs));r['created_objects']+=new
r['reference_detail_refinement']={'before':before,'after':{n:sig(scene.objects[n]) for n in before},'new_objects':new,'reference_media_ids':refs,'support_glazing':{'columns_candidate':columns,'rows_candidate':rows,'width_fraction_of_shaft_candidate':.58,'sill_z_candidate_m':sill,'head_z_candidate_m':head,'glazing_width_candidate_m':width,'verified_real_dimensions':None,'real_opening':True,'shaft_faces_straightened':True},'terrain_foot':{'changes':ground_rows,'classification':'ADAPT_LOCAL','method':'Pé do apoio pelo patamar local amostrado em X=-22, cota próxima à contenção da ladeira; remove rampa residual que encobria a base. Sem largura/traçado inventados.','real_survey':False},'proxy_room_cut':room_rows,'localized_ground_material':{'materials':materials,'masked_vertices':int(np.count_nonzero(values)),'attribute':attr.name,'physical_displacement':False,'photos_used_as_textures':False},'source_road_positions_preserved':len(roads),'source_DEM_changed':False,'review':'pending'}
for row in r['terrain_refinement']['geometry']:row['after']=sig(scene.objects[row['object']])
r['terrain_refinement']['visual_review']='pending';r.pop('localized_scene_review',None)
scene['architecture_revision']='R30B.35 | apoio alinhado e vazado; galerias escavadas; encosta estrutural'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'source_after':r['source_after'],'windows':columns*rows,'new':new,'proxy':room_rows},ensure_ascii=False))
