"""A* sobre superfícies existentes e obstáculos avaliados; somente leitura."""
import bpy,json,math,heapq
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-corridor'
dg=bpy.context.evaluated_depsgraph_get();scene=bpy.context.scene
floor_names=['MVP | terreno corrigido | colisão estática','INFERIOR | piso do saguão','SUPERIOR | piso saguão','CALIBRADO | passarela piso 28.71 x 6.00m','CALIBRADO | piso superior torre','CALIBRADO | piso desembarque baixo','FUNCIONAL | soleira inferior','INFERIOR R21 | passeio da entrada','INFERIOR R21 | rebaixo acessível','TÉRREO | laje','LAC R30B | Passarela | piso paginado visual','PRAÇA | OSM 1263035782','FUNCIONAL | 3 soleira superior','FUNCIONAL | 3 soleira inferior','TORRE | cornija galeria']
floor_names.append('ESTAÇÃO INFERIOR | plataforma')
def center(ob):
    points=[ob.matrix_world@Vector(p) for p in ob.bound_box]
    return Vector([sum(p[i] for p in points)/8 for i in range(3)])
cabin=scene.objects['FUNCIONAL | 3 piso'];c=center(cabin)
low=scene.objects['FUNCIONAL | 3 porta estação lower -1'];high=scene.objects['FUNCIONAL | 3 porta estação upper -1']
lower_z=min((low.matrix_world@Vector(p)).z for p in low.bound_box);upper_z=min((high.matrix_world@Vector(p)).z for p in high.bound_box)
travel=upper_z-lower_z
def triangles(ob,dz=0):
    evaluated=ob.evaluated_get(dg);mesh=evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles();v=[evaluated.matrix_world@p.co+Vector((0,0,dz)) for p in mesh.vertices]
        return v,[tuple(t.vertices) for t in mesh.loop_triangles]
    finally:evaluated.to_mesh_clear()
floors=[];export=[]
for name in floor_names:
    ob=bpy.data.objects.get(name)
    if ob is None or not ob.visible_get():continue
    v,p=triangles(ob);floors.append((name,BVHTree.FromPolygons(v,p,all_triangles=True)))
    if name!='MVP | terreno corrigido | colisão estática':
        # Somente faces superiores; normal corrigida no derivado, fonte intacta.
        faces=[];source_tree=BVHTree.FromPolygons(v,p,all_triangles=True);top=max(point.z for point in v)
        for face in p:
            pts=[v[i] for i in face];normal=(pts[1]-pts[0]).cross(pts[2]-pts[0])
            if abs(normal.z)<1e-8:continue
            if abs(normal.z)/normal.length<.7:continue
            midpoint=sum(pts,Vector())/3
            highest=source_tree.ray_cast(Vector((midpoint.x,midpoint.y,top+1)),Vector((0,0,-1)),top-min(point.z for point in v)+2)[0]
            if highest is None or abs(highest.z-midpoint.z)>.0002:continue
            faces.append(list(face) if normal.z>0 else list(reversed(face)))
        export.append({'source':name,'vertices':[list(p) for p in v],'faces':faces})
virtual=[]
for dz in (0,-travel):
    v,p=triangles(cabin,dz);virtual.append(BVHTree.FromPolygons(v,p,all_triangles=True))
# Meio-fio é transição de circulação, não parede infinita. Usar seus topos reais.
for ob in scene.objects:
    if ob.type=='MESH' and ob.visible_get() and ob.name.startswith('B63 | VISUAL | meios-fios'):
        v,p=triangles(ob);floors.append((ob.name,BVHTree.FromPolygons(v,p,all_triangles=True)))
verts=[];faces=[];names=[];moving=[[],[]]
for ob in scene.objects:
    if ob.type!='MESH' or not ob.visible_get() or ob.hide_render:continue
    if ob.name=='OSM | 1263035777':
        # Exclusão candidata de massing, não identificação automática de Hero.
        # Volume sem altura OSM certificada sobre o saguão já modelado.
        assert any(c.name=='20 MVP | edifícios OSM do Aleph' for c in ob.users_collection)
        continue
    if ob.name.startswith(('NAV |','QA |','R30A','B74 |','B75 |')) or any(col.name.startswith(('SOURCE_GEOREF','33.','34.','37.','QA |')) for col in ob.users_collection):continue
    if ob.get('elevator_id') in (3,4) and ob.get('elevator_role') in ('cabin_door','landing_door'):
        if ob.get('elevator_id')==3 and ob.get('elevator_role')=='cabin_door':
            for stage,side,dz in ((0,-1,0),(1,1,-travel)):
                if ob.get('door_side')==side:
                    v,p=triangles(ob,dz);moving[stage].append((ob.name,BVHTree.FromPolygons(v,p,all_triangles=True)))
        continue
    points=[ob.matrix_world@Vector(p) for p in ob.bound_box]
    if max(p.x for p in points)<-142 or min(p.x for p in points)>25 or max(p.y for p in points)<-18 or min(p.y for p in points)>180:continue
    if ob.get('elevator_id')==3 and ob.get('elevator_role')=='cabin':
        for i,dz in enumerate((0,-travel)):
            v,p=triangles(ob,dz);moving[i].append((ob.name,BVHTree.FromPolygons(v,p,all_triangles=True)))
        continue
    # Filhos visuais do conjunto móvel acompanham seu ancestral.
    ancestor=ob.parent;mobile=False
    while ancestor:
        if ancestor.get('elevator_id') in (3,4) and ancestor.get('elevator_role') in ('cabin','cabin_door','landing_door'):mobile=True;break
        ancestor=ancestor.parent
    if mobile:continue # decoração não é colisor; estrutura móvel acima é considerada
    v,p=triangles(ob);base=len(verts);verts.extend(v);faces.extend(tuple(base+i for i in f) for f in p);names.extend([ob.name]*len(p))
static=BVHTree.FromPolygons(verts,faces,all_triangles=True)
radius=.3;height=1.8;step=.25;spacing=.4;contact=.015
def raw_support(x,y,stage):
    expected=upper_z if stage==0 else lower_z;hits=[]
    for name,tree in [*floors,('FUNCIONAL | 3 piso',virtual[stage])]:
        hit=tree.ray_cast(Vector((x,y,expected+.26)),Vector((0,0,-1)),1.2)
        if hit[0] is not None and abs(hit[1].z)>.7:hits.append((hit[0].z,name))
    return max(hits) if hits else None
def support(x,y,stage):
    hit=raw_support(x,y,stage)
    if hit:return hit
    # Só no embarque medido: uma cápsula pode tocar as bordas da soleira
    # mesmo quando uma única sondagem vertical central passa pelo vão.
    leaf=scene.objects['FUNCIONAL | 3 porta estação '+('upper' if stage==0 else 'lower')+' 1']
    portal=(center(high if stage==0 else low)+center(leaf))/2
    if math.dist((x,y),(portal.x,portal.y))>.45:return None
    contacts=[raw_support(x+dx,y+dy,stage) for dx,dy in ((radius,0),(-radius,0),(0,radius),(0,-radius))]
    if any(h is None for h in contacts) or max(h[0] for h in contacts)-min(h[0] for h in contacts)>step:return None
    expected=upper_z if stage==0 else lower_z;candidates=[]
    for name,tree in [*floors,('FUNCIONAL | 3 piso',virtual[stage])]:
        for p,normal,index,d in tree.find_nearest_range(Vector((x,y,expected+radius)),radius+.15):
            horizontal=math.hypot(p.x-x,p.y-y)
            if abs(normal.z)<.7 or horizontal>=radius or abs(p.z-expected)>step:continue
            z=p.z-radius+math.sqrt(radius**2-horizontal**2)
            if expected-z<=.03:candidates.append((z,name))
    return max(candidates) if candidates else None
def blocked(x,y,z,stage,check_moving=True):
    for j in range(9):
        point=Vector((x,y,z+radius+j*(height-2*radius)/8))
        for hit in static.find_nearest_range(point,radius):
            if hit[3]>=radius-contact:continue
            name=names[hit[2]]
            if (name in floor_names or name.startswith('B63 | VISUAL | meios-fios')) and hit[0].z<=z+step:continue
            return name
        for name,tree in (moving[stage] if check_moving else []):
            hit=tree.find_nearest(point,radius)
            if hit[0] is not None and hit[3]<radius-contact:
                if name=='FUNCIONAL | 3 piso' and hit[0].z<=z+step:continue
                return name
    return None
def route(start,end,stage):
    lo=(math.floor(min(start[0],end[0])-14),math.floor(min(start[1],end[1])-14));hi=(max(start[0],end[0])+14,max(start[1],end[1])+14)
    cache={};rejects={}
    def point(key):return (lo[0]+key[0]*spacing,lo[1]+key[1]*spacing)
    def cell(key):
        if key in cache:return cache[key]
        x,y=point(key)
        if x<lo[0] or y<lo[1] or x>hi[0] or y>hi[1]:return None
        h=support(x,y,stage)
        reason=None
        if h:
            reason=blocked(x,y,h[0],stage)
            if not reason:
                for dx,dy in ((radius,0),(-radius,0),(0,radius),(0,-radius)):
                    lateral=support(x+dx,y+dy,stage)
                    if not lateral or abs(lateral[0]-h[0])>step:reason='unsupported_capsule_edge';break
        if reason:rejects[reason]=rejects.get(reason,0)+1
        cache[key]=h if h and not reason else None;return cache[key]
    def near(p):
        k=(round((p[0]-lo[0])/spacing),round((p[1]-lo[1])/spacing));choices=[]
        for dx in range(-2,3):
            for dy in range(-2,3):
                q=(k[0]+dx,k[1]+dy)
                if cell(q):choices.append((math.dist(point(q),p[:2]),q))
        return min(choices)[1] if choices else None
    a,b=near(start),near(end)
    if a is None or b is None:return {'status':'pending','reason':'endpoint_obstructed','start':start,'end':end,'rejects':rejects}
    queue=[(0,a)];cost={a:0};previous={};found=False
    while queue and len(cost)<65000:
        _,key=heapq.heappop(queue)
        if key==b:found=True;break
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            q=(key[0]+dx,key[1]+dy);h=cell(q)
            if not h or abs(h[0]-cell(key)[0])>step:continue
            if dx and dy and (not cell((key[0]+dx,key[1])) or not cell((key[0],key[1]+dy))):continue
            # Validar também o meio do segmento; reduz passagem entre obstáculos.
            px,py=point(key);qx,qy=point(q);m=support((px+qx)/2,(py+qy)/2,stage)
            if not m or blocked((px+qx)/2,(py+qy)/2,m[0],stage):continue
            new=cost[key]+spacing*math.hypot(dx,dy)
            if new<cost.get(q,float('inf')):
                cost[q]=new;previous[q]=key;heapq.heappush(queue,(new+math.dist(point(q),point(b)),q))
    if not found:
        closest=min(cost,key=lambda key:math.dist(point(key),point(b)))
        return {'status':'pending','reason':'no_clear_route_on_existing_geometry','evaluated_cells':len(cache),'closest_reachable_xy':point(closest),'remaining_distance':math.dist(point(closest),point(b)),'start_snapped':point(a),'end_snapped':point(b),'rejects':rejects}
    keys=[b]
    while keys[-1]!=a:keys.append(previous[keys[-1]])
    keys.reverse();poses=[[*point(k),cell(k)[0]] for k in keys]
    return {'status':'sampled_clear','points':poses,'length_design_units':cost[b],'evaluated_cells':len(cache),'rejects':rejects,'support_sources':sorted({cell(k)[1] for k in keys}),'max_step':max(abs(a[2]-b[2]) for a,b in zip(poses,poses[1:]))}
reference=json.loads((ROOT/'artifacts/structural-pipeline/centro-lapa-tororo-fontenova/structural_reference.json').read_text(encoding='utf8'))
way=next(f for f in reference['features'] if f['osm_type']=='way' and f['osm_id']==1429934820)
start=way['blender_xy'][-1];market=center(scene.objects['ACESSO | fachada Praça Cairu | verga'])
portal_only=globals().get('BOAS_ONLY_PORTAL_PROBE',False);upper_only=globals().get('BOAS_ONLY_UPPER_ROUTE',False);lower_only=globals().get('BOAS_ONLY_LOWER_ROUTE',False)
routes={} if portal_only else {'upper':json.loads((OUT/'walkability_candidate_b77.json').read_text(encoding='utf8'))['routes']['upper'] if lower_only else route(start,list(c),0),'lower':json.loads((OUT/'walkability_candidate_b77.json').read_text(encoding='utf8'))['routes']['lower'] if upper_only else route(list(c),list(market),1)}
if not portal_only and not upper_only and not lower_only:
    routes['upper_plaza_bridge']=route(start,[-25.6478,29.88745],0)
    routes['upper_bridge_cabin']=route([-25.6478,29.88745],list(c),0)
result={'schema':'boas/lacerda-walkability-candidate-v1','character_design':{'radius':radius,'height':height,'maximum_step':step,'grid_spacing':spacing,'contact_tolerance':contact,'boarding_capsule_contact_max_drop':.03,'boarding_contact_radius':.45},'elevator':{'id':3,'source':'FUNCIONAL | 3 piso','upper_z':upper_z,'lower_z':lower_z,'travel_design_units':travel,'source_dimensions_status':'aproximação existente, sem datum/levantamento certificado','door_state_for_audit':'open; navegação deve ser bloqueada quando fechada'},'routes':routes,'collision_sources':floor_names,'method':'A* no chão existente; cápsula por nove esferas, laterais e meio de segmento. Embarque permite contato geométrico da semiesfera inferior nas bordas reais, com quatro apoios laterais e descida máxima 3 cm; não gera superfície no vão. Estado inferior usa translação vertical medida da cabine existente. Sem física/sweep contínuo/validação de maré ou datum absoluto.','lower_route_reused_same_b76':upper_only}
if portal_only:
    entrance=(center(high)+center(scene.objects['FUNCIONAL | 3 porta estação upper 1']))/2
    probes=[]
    for i in range(25):
        p=entrance+(c-entrance)*i/24;h=support(p.x,p.y,0)
        probes.append({'xy':[p.x,p.y],'support':h,'blocker':blocked(p.x,p.y,h[0],0) if h else 'unsupported'})
    result['portal_probes']=probes
    entrance=(center(low)+center(scene.objects['FUNCIONAL | 3 porta estação lower 1']))/2
    probes=[]
    for i in range(25):
        p=entrance+(c-entrance)*i/24;h=support(p.x,p.y,1)
        probes.append({'xy':[p.x,p.y],'support':h,'blocker':blocked(p.x,p.y,h[0],1) if h else 'unsupported'})
    result['lower_portal_probes']=probes
    sweep=[]
    for i in range(math.ceil(travel/.25)+1):
        z=upper_z-travel*i/math.ceil(travel/.25)
        # No poço a cabine acompanha o personagem: não consultar seu teto em uma parada fixa.
        sweep.append({'z':z,'blocker':blocked(c.x,c.y,z,0 if i==0 else 1,check_moving=False)})
    result['shaft_character_sweep']=sweep
    result['shaft_character_blocked']=sum(p['blocker'] is not None for p in sweep)
(OUT/('portal_probe_b77.json' if portal_only else 'walkability_candidate_b77.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
artifact=ROOT/'artifacts/lacerda-corridor';artifact.mkdir(parents=True,exist_ok=True)
(artifact/'floor_collision_candidate_b77.json').write_text(json.dumps(export,ensure_ascii=False),encoding='utf8')
print(json.dumps({'routes':{k:{j:v.get(j) for j in ('status','reason','length_design_units','evaluated_cells')} for k,v in routes.items()},'portal_probes':result.get('portal_probes'),'travel':travel},ensure_ascii=False))
