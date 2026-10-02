"""Vertical slice urbana: geometria derivada do OSM e suporte da cena, via MCP.

Não altera DEM/XY. Substitui os trechos legados conflitantes, mantém referência
e cria superfícies/colisores separados para o runtime.
"""
import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
contract_path=ROOT/'world/areas/mvp-centro-lacerda/production.json'
contract=json.loads(contract_path.read_text())
if Path(bpy.data.filepath).resolve() != (ROOT/contract['world_source']['file']).resolve():
    raise RuntimeError('Abrir a fonte ativa antes da modelagem')
if bpy.data.collections.get('40 VISUAL | URBAN SLICE'):
    raise RuntimeError('Slice já aplicada; editar a revisão existente, não duplicar')
scene=bpy.context.scene
graph=json.loads((ROOT/contract['staging']['roads']).read_text())
nodes={n['id']:n for n in graph['nodes']}
edges={(e['from'],e['to']):e for e in graph['edges']}
ways={w['osm_way_id']:w for w in graph['ways']}
common=['34592721','13304581716','13348016139','34592712','13348016147','4002451307','4007759713','13304581715','4007759718','13304581714','1703474642','1703474645']
routes=[common+['34592721'],common+['6939750290','6939750291','34592721']]

def collection(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
visual=collection('40 VISUAL | URBAN SLICE')
gameplay=collection('41 GAMEPLAY | URBAN SLICE')
collision=collection('41.1 COLLISION | URBAN SLICE')
terrain=bpy.data.objects[contract['export']['road_object']]
ev=terrain.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles()
tree=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True);ev.to_mesh_clear()
def h(x,y):
    hit=tree.ray_cast(Vector((x,y,140)),Vector((0,0,-1)),300)[0]
    if hit is None:raise RuntimeError('Fonte de chão ausente')
    return hit.z

# O proxy anterior ficou obsoleto após edição da superfície-fonte. Reprojetar
# cada vértice sobre a fonte atual; não aplicar offset/escala vertical global.
proxy=bpy.data.objects[contract['export']['terrain_proxy']]
changes=[];inverse=proxy.matrix_world.inverted()
for v in proxy.data.vertices:
    p=proxy.matrix_world@v.co;hit=tree.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),300)[0]
    if hit:
        changes.append(abs(p.z-hit.z));v.co=inverse@Vector((p.x,p.y,hit.z))
proxy.data.update();proxy['boas_support_source']=terrain.name
proxy['boas_adaptation']='ERROR: proxy obsoleto; reprojeção sobre a geometria-fonte atual, sem escala Z'

def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bsdf=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if bsdf is None:
        bsdf=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');out=next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL');m.node_tree.links.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=.88;return m
asphalt=mat('SLICE | pavimento',(.105,.12,.13));stone=mat('SLICE | passeio de pedra',(.46,.46,.43));white=mat('SLICE | marcação provisória',(.88,.9,.85));black=mat('SLICE | sinal estrutura',(.07,.08,.08))
def mesh(name,verts,faces,material,coll=visual,role=None):
    if role:faces=[tuple(reversed(f)) if (Vector(verts[f[1]])-Vector(verts[f[0]])).cross(Vector(verts[f[2]])-Vector(verts[f[0]])).z<0 else f for f in faces]
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);coll.objects.link(o)
    if material:o.data.materials.append(material)
    o['boas_area_id']=contract['area_id'];o['boas_generated_revision']='R30C.1'
    if role:o['boas_role']=role
    return o
def box(name,p,d,material,coll=visual):
    x,y,z=p;dx,dy,dz=[v/2 for v in d]
    vs=[(x+a*dx,y+b*dy,z+c*dz) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material,coll)

grade={id:h(*nodes[id]['blender_xy'])+.035 for r in routes for id in r}
segments=[];seen=set();surface_objects=[]
for r in routes:
    for a,b in zip(r,r[1:]):
        if (a,b) in seen:continue
        seen.add((a,b));e=edges[(a,b)];w=ways[e['osm_way_id']]
        p=Vector((*nodes[a]['blender_xy'],grade[a]));q=Vector((*nodes[b]['blender_xy'],grade[b]));v=(q-p);v.z=0;length=v.length;v.normalize();n=Vector((-v.y,v.x,0))
        width=w.get('width_m_tagged') or (6.4 if w['highway']=='secondary' else 4.2)
        segments.append({'a':p,'b':q,'n':n,'width':width,'edge':e})
        # Continuous strip, generous miter at joins; corners have separate patches.
        for role,lo,hi,material,dz in [('road',-width/2,width/2,asphalt,0),('walkable',-width/2-1.7,-width/2,stone,.12),('walkable',width/2,width/2+1.7,stone,.12)]:
            vs=[];fs=[];steps=max(1,math.ceil(length/2))
            for j in range(steps+1):
                c=p.lerp(q,j/steps)
                for offset in [lo,hi]:vs.append(tuple(c+n*offset+Vector((0,0,dz))))
            for j in range(steps):fs.append((2*j,2*j+1,2*j+3,2*j+2))
            o=mesh('SLICE | '+role+' | '+e['id']+(' L' if hi<0 else ' R' if lo>0 else ''),vs,fs,material,role=role)
            o['boas_osm_way_id']=e['osm_way_id'];o['boas_source_edge_id']=e['id'];o['boas_width_source']='OSM' if w.get('width_m_tagged') else 'ADAPT_LOCAL: envelope de teste; não levantado'
            gameplay.objects.link(o);surface_objects.append(o)

# Triangulated joins eliminate holes at bends; explicit local adaptation in the
# contract. Surface stays on the node elevation derived from the scene.
for id in set(i for r in routes for i in r):
    connected=[s for s in segments if id in (s['edge']['from'],s['edge']['to'])]
    p=Vector((*nodes[id]['blender_xy'],grade[id]));pts=[]
    for s in connected:
        for sign in [-1,1]:pts.append(p+s['n']*sign*(s['width']/2+1.7))
    pts.sort(key=lambda q:math.atan2(q.y-p.y,q.x-p.x))
    if len(pts)<3:continue
    o=mesh('SLICE | transição passeio | '+id,[tuple(p+Vector((0,0,.12)))]+[tuple(q+Vector((0,0,.12))) for q in pts],[(0,j+1,(j+1)%len(pts)+1) for j in range(len(pts))],stone,role='walkable')
    gameplay.objects.link(o);surface_objects.append(o)
    # Recessed crossing/junction roadway through the middle of the join.
    radius=max(s['width']/2 for s in connected)
    points=[tuple(p)]+[tuple(p+Vector((math.cos(t*math.tau/16)*radius,math.sin(t*math.tau/16)*radius,0.002))) for t in range(16)]
    o=mesh('SLICE | ligação pista | '+id,points,[(0,i+1,(i+1)%16+1) for i in range(16)],asphalt,role='road');gameplay.objects.link(o);surface_objects.append(o)

def distance(p,s):
    a=s['a'];b=s['b'];d=b-a;d.z=0;t=max(0,min(1,Vector((p.x-a.x,p.y-a.y,0)).dot(d)/d.length_squared));q=a+d*t;return Vector((p.x-q.x,p.y-q.y,0)).length
# Remove overlapping legacy road/walkway faces in this bounded corridor.
# References remain untouched. No overlay to hide disagreeing old surfaces.
removed={}
for name in ['OSM | pistas do centro','OSM | calçadas indicativas','OSM | caminhos e escadarias','VIAS | guias contínuas com aberturas nas travessias']:
    o=bpy.data.objects.get(name)
    if not o or o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data);faces=[]
    for f in bm.faces:
        p=o.matrix_world@f.calc_center_median()
        if any(distance(p,s)<s['width']/2+1.85 and abs(p.z-(s['a'].z+s['b'].z)/2)<12 for s in segments):faces.append(f)
    removed[name]=len(faces);bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(o.data);bm.free();o.data.update()

# Crossing on the Chile exit, connected to the OSM pedestrian corridor 1321755864.
junction=Vector((*nodes['34592721']['blender_xy'],grade['34592721']))
forward=segments[0]['b']-segments[0]['a'];forward.z=0;forward.normalize();normal=Vector((-forward.y,forward.x,0));center=junction+forward*11
cross_y=grade['34592721']+(grade['13348016139']-grade['34592721'])*11/(Vector((*nodes['13348016139']['blender_xy'],0))-Vector((*nodes['34592721']['blender_xy'],0))).length
center.z=cross_y+.005
ped_a=center+normal*5;ped_b=center-normal*5
# Accessible landing ramps connect both curbs to the same crossing elevation.
for sign in [-1,1]:
    a=center+normal*sign*3.05;b=center+normal*sign*5.0
    vs=[tuple(a-forward*2),tuple(a+forward*2),tuple(b+forward*2+Vector((0,0,.12))),tuple(b-forward*2+Vector((0,0,.12)))]
    o=mesh('SLICE | rebaixo acessível '+str(sign),vs,[(0,1,2,3)],stone,role='crossing');gameplay.objects.link(o);surface_objects.append(o)
for i in range(9):
    c=center+normal*((i-4)*.7);vs=[tuple(c+normal*a+forward*b+Vector((0,0,.008))) for a,b in [(-.23,-1.65),(.23,-1.65),(.23,1.65),(-.23,1.65)]]
    mesh('SLICE | faixa pedestre '+str(i),vs,[(0,1,2,3)],white)

# Signal housings are authored in Blender; only lamp emission is controlled by
# the runtime state machine. Two independent approaches and one pedestrian phase.
signals=[]
for group,from_id,distance_m in [('main','6939750291',12),('side','1703474645',12)]:
    a=Vector((*nodes[from_id]['blender_xy'],grade[from_id]));direction=junction-a;direction.z=0;direction.normalize();n=Vector((-direction.y,direction.x,0));stop=junction-direction*distance_m
    stop.z=h(stop.x,stop.y)+.035
    half=3.2 if group=='main' else 2.1
    mesh('SLICE | linha parada '+group,[tuple(stop+n*x+direction*y+Vector((0,0,.008))) for x,y in [(-half,-.18),(half,-.18),(half,.18),(-half,.18)]],[(0,1,2,3)],white)
    pole=stop+n*(half+1.15);box('SLICE | poste '+group,(pole.x,pole.y,stop.z+2.4),(.12,.12,4.8),black)
    body=box('SLICE | semáforo '+group,(pole.x,pole.y,stop.z+4.0),(.45,.28,1.1),black)
    body.rotation_euler.z=math.atan2(direction.y,direction.x)-math.pi/2
    for k,color in enumerate(['red','amber','green']):
        m=mat('SLICE | luz '+group+' '+color,{'red':(.7,.01,.01),'amber':(.8,.4,.01),'green':(.01,.65,.12)}[color]);p=Vector((pole.x,pole.y,stop.z+4.35-k*.34))-direction*.17
        o=box('SLICE_LAMP_'+group+'_'+color,p,(.24,.12,.24),m);o.rotation_euler.z=body.rotation_euler.z;o['boas_signal_group']=group;o['boas_signal_color']=color
    signals.append({'group':group,'stop_position':list(stop),'position':list(pole)})
for i,p in enumerate([ped_a,ped_b]):
    box('SLICE | sinal pedestre poste '+str(i),(p.x,p.y,p.z+1.4),(.1,.1,2.8),black)
    for k,color in enumerate(['red','green']):
        m=mat('SLICE | pedestre '+str(i)+' '+color,{'red':(.7,.01,.01),'green':(.01,.65,.12)}[color]);o=box('SLICE_LAMP_ped_'+color+'_'+str(i),(p.x,p.y,p.z+2.5-k*.3),(.23,.2,.23),m);o['boas_signal_group']='ped';o['boas_signal_color']=color

# Simplified obstacle proxies, using actual source footprints within the corridor.
# Boxes only for compact existing building meshes; no detailed visual mesh in physics.
obstacles=[]
for o in list(scene.objects):
    if o.type!='MESH' or not o.visible_get() or o.name.startswith('SLICE'):continue
    if not any('20 MVP' in c.name for c in o.users_collection):continue
    bb=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in bb) for i in range(3)];hi=[max(v[i] for v in bb) for i in range(3)];p=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]))
    if min(distance(p,s) for s in segments)>40 or hi[2]-lo[2]<2:continue
    obstacles.append({'name':o.name,'bounds':[lo,hi],'source':'visual-footprint candidate'})

def runtime(p):return [round(p[0],5),round(p[2],5),round(-p[1],5)]
config={'schema':'boas/urban-slice-v1','id':'chile-ajuda-vassouras','status':'gameplay_candidate','coordinate_space':'X,Z,-Y','source_graph':'r30a7/road_graph','source_fit':'candidate_only','routes':[],'signals':[{**s,'stop_position':runtime(s['stop_position']),'position':runtime(s['position'])} for s in signals], 'junction':runtime(junction),'crossing':{'id':'slice-crossing-chile','source_pedestrian_way_id':1321755864,'classification':'ADAPT_LOCAL','reason':'travessia controlada provisória conectando passeios; localização semafórica real não verificada','points':[runtime(ped_a),runtime(ped_b)]},'spawn':runtime(ped_a+forward*5+Vector((0,0,.16))),'heading':math.atan2(normal.x,-normal.y),'obstacles':[], 'surfaces':[], 'bounds':{'minX':-44,'maxX':103,'minZ':-9,'maxZ':152}, 'phases':[{'name':'Chile','group':'main','seconds':14},{'name':'Amarelo Chile','group':'mainAmber','seconds':3},{'name':'Limpeza','group':'allRed','seconds':2},{'name':'Vassouras','group':'side','seconds':12},{'name':'Amarelo Vassouras','group':'sideAmber','seconds':3},{'name':'Limpeza','group':'allRed','seconds':2},{'name':'Travessia','group':'ped','seconds':10},{'name':'Limpeza pedonal','group':'allRed','seconds':3}], 'adaptations':[{'classification':'ERROR','description':'Proxy de suporte reprojetado sobre a fonte visual atual; sem offset global.'},{'classification':'ADAPT_LOCAL','description':'Corredor rodoviário 6,4 m secondary / 4,2 m residencial; passeios 1,7 m, rampas e raios locais para circulação. Não são medidas levantadas.','width_m_verified':None},{'classification':'SOURCE_LIMITATION','description':'Fit XY candidate_only e DEM vertical insuficiente; não afirmar precisão cartográfica.'}], 'bus_stops':[], 'limitations':['Só este circuito urbano é validado. Ligação à Cidade Baixa e funcionamento do Lacerda fora desta slice.','Sem ponto de ônibus verificado no trecho; rota de ônibus pendente.']}
for i,r in enumerate(routes):
    config['routes'].append({'id':['vassouras','chile'][i],'signal_group':['side','main'][i], 'node_ids':r,'edge_ids':[edges[(a,b)]['id'] for a,b in zip(r,r[1:])], 'osm_way_ids':list(dict.fromkeys(edges[(a,b)]['osm_way_id'] for a,b in zip(r,r[1:]))),'points':[runtime((*nodes[id]['blender_xy'],grade[id]+.13)) for id in r], 'loop':True,'speed_m_s':5})
for o in surface_objects:
    me=o.data;me.calc_loop_triangles();config['surfaces'].append({'name':o.name,'role':o['boas_role'],'positions':[c for v in me.vertices for c in runtime(o.matrix_world@v.co)],'indices':[v for t in me.loop_triangles for v in t.vertices]})
for item in obstacles:
    lo,hi=item['bounds'];item['bounds']=[[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]];config['obstacles'].append(item)
public=ROOT/'prototypes/threejs-water-lab/public/data/urban_slice.json';public.write_text(json.dumps(config,ensure_ascii=False,separators=(',',':')),encoding='utf8')
# Store the same gameplay contract inside the .blend and versioned area metadata.
text=bpy.data.texts.new('BOAS_URBAN_SLICE.json');text.write(json.dumps({k:v for k,v in config.items() if k!='surfaces'},ensure_ascii=False,indent=2))
area=ROOT/'world/areas/mvp-centro-lacerda/urban_slice.json';area.write_text(json.dumps({k:v for k,v in config.items() if k not in ('surfaces','obstacles')},ensure_ascii=False,indent=2),encoding='utf8')
scene['boas_urban_slice_id']=config['id']
output=ROOT/'blender/salvador_lacerda_mvp_r30c1_urban_slice.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
contract['world_source'].update(file=output.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),revision='R30C.1')
contract['export']['visual_collection_ids'].append('40')
contract['runtime']['spawn']={'x':config['spawn'][0],'z':config['spawn'][2],'headingDeg':0}
contract['runtime']['streaming'].update(load_radius_m=160,unload_radius_m=230)
contract_path.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report={'schema':'boas/urban-slice-blender-review-v1','source':contract['world_source'],'proxy_reprojected_vertices':len(changes),'proxy_max_previous_error_m':max(changes),'removed_legacy_faces':removed,'surface_objects':len(surface_objects),'obstacles':len(obstacles),'adaptations':config['adaptations']}
p=ROOT/'docs/reports/blender/urban_slice_scene.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
