"""QA localizada B86 na sessão reaberta; não aprova instalação/rota completa."""
import bpy,bmesh,hashlib,json,math,os,runpy,sys
from pathlib import Path
from mathutils import Matrix,Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/reports/blender/lacerda-layout-b86'
r=json.loads((OUT/'application.json').read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(ROOT/r['file']).resolve()
assert bpy.context.scene.name==r['scene']
proof=json.loads((ROOT/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert proof['file']==r['file'] and proof['load_post_completed']
helpers=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))
wm=helpers['world_matrix'];signature=helpers['signature']
scene=bpy.context.scene
M=Matrix(json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame'])
inv=M.inverted()
checks=[]
for row in r['changes']:
    obj=scene.objects[row['object']]
    assert signature(obj)==row['after']['signature'],obj.name
    bm=bmesh.new();bm.from_mesh(obj.data)
    degenerate=sum(f.calc_area()<1e-8 for f in bm.faces)
    boundary=sum(e.is_boundary for e in bm.edges)
    nonmanifold=sum(not e.is_manifold for e in bm.edges)
    bm.free()
    assert not degenerate,obj.name
    if obj.name in ('SUPERIOR | piso saguão','SUPERIOR | cobertura saguão'):assert not boundary and not nonmanifold
    if row['superseded']:assert obj.hide_render and obj.hide_get(view_layer=scene.view_layers[0])
    checks.append({'object':obj.name,'persisted':True,'degenerate_faces':degenerate,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold})

assert hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
for path,digest in ((r['parent_file'],r['parent_sha256']),(r['file'],r['sha256'])):
    with (ROOT/path).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==digest

# Referência B85 carregada somente para comparação; não abre outra janela.
proxy_names=[o.name for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects]
protected_names=proxy_names+['MVP | terreno corrigido | colisão estática']
prior_path=OUT/'validation.json'
prior=json.loads(prior_path.read_text(encoding='utf8')) if prior_path.exists() else None
reuse=bool(prior and prior.get('revision')==r['revision'] and prior.get('reopened') and prior.get('pid')==os.getpid() and not bpy.data.is_dirty)
if reuse:
    assert prior['proxy_b82_preserved'] and prior['terrain_preserved']
else:
    baseline=helpers['inspect_file'](ROOT/r['parent_file'],protected_names)
    assert all(signature(bpy.data.objects[n])==baseline[n] for n in protected_names)

sys.path.insert(0,str(ROOT/'tools/world'))
import numpy as np
from slice_geometry import capsule_distances,support_hits
from character_support import capsule_support

def mesh_triangles(obj):
    obj.data.calc_loop_triangles()
    coordinates=np.empty(len(obj.data.vertices)*3,dtype=np.float32)
    obj.data.vertices.foreach_get('co',coordinates)
    transform=np.array(inv@wm(obj),dtype=np.float64)
    pts=coordinates.reshape((-1,3))@transform[:3,:3].T+transform[:3,3]
    ids=np.empty(len(obj.data.loop_triangles)*3,dtype=np.int32)
    obj.data.loop_triangles.foreach_get('vertices',ids)
    ids=ids.reshape((-1,3))
    return pts[ids] if len(ids) else np.empty((0,3,3))

floor=scene.objects['SUPERIOR | piso saguão']
bridge_sources=[scene.objects[row['object']] for row in r['changes'] if row['domain']=='BRIDGE' and 'piso' in row['object'].casefold() and not row['superseded'] and 'COLLISION' not in row['object']]
assert bridge_sources
floors=np.concatenate([mesh_triangles(o) for o in [floor,*bridge_sources]])
obstacles=[];owners=[]
for obj in scene.objects:
    if obj.type!='MESH' or obj.constraints or not obj.visible_get(view_layer=scene.view_layers[0]):continue
    if obj.name in proxy_names or any(c.name.startswith(('SOURCE_GEOREF','REFERENCE_','NAVIGATION')) for c in obj.users_collection):continue
    points=[inv@wm(obj)@Vector(p) for p in obj.bound_box]
    low=np.min(points,axis=0);high=np.max(points,axis=0)
    if np.any(high<[-22,-2,69]) or np.any(low>[-17,2,73]):continue
    tri=mesh_triangles(obj)
    if not len(tri):continue
    obstacles.append(tri);owners.extend([obj.name]*len(tri))
tri=np.concatenate(obstacles) if obstacles else np.empty((0,3,3))
lo=tri.min(axis=1);hi=tri.max(axis=1);owners=np.array(owners)

# Diagnóstico volumétrico local com apoio no piso real, step e skin mantidos.
# Não se trata do controller inteiro nem de prova de interior/poço.
routes=[]
for y in (-1.,0.,1.):
    samples=[];last_z=None;first_block=None;missing=[];steps=[]
    for x in np.linspace(-21.5,-17.5,81):
        supports,z=support_hits(x,y,floors,69.5,70.5)
        # Reutiliza o suporte da esfera inferior em faces/arestas finitas.
        # A projeção central isolada não cobre juntas nem contorno de degrau.
        base_z=capsule_support(x,y,floors,69.5,70.5,radius=.30,skin=.015)
        if base_z is None:missing.append([float(x),y]);continue
        top=float(base_z)-.015
        ring=[]
        for theta in np.linspace(0,2*math.pi,9)[:-1]:
            _,heights=support_hits(x+.30*math.cos(theta),y+.30*math.sin(theta),floors,top-.25,top+.25)
            ring.append(float(heights.max()) if len(heights) else None)
        if last_z is not None and abs(top-last_z)>.001:steps.append({'x':float(x),'rise':top-last_z,'within_candidate_step':abs(top-last_z)<=.25})
        last_z=top
        base=np.array([x,y,top+.015])
        near=np.all(hi>=base-[.315,.315,.015],axis=1)&np.all(lo<=base+[.315,.315,1.815],axis=1)
        minimum=None;owner=None
        if near.any():
            distance=capsule_distances(base,tri[near],.30,1.80);i=int(distance.argmin());minimum=float(distance[i]);owner=str(owners[near][i])
            if minimum<.285 and first_block is None:first_block={'position':base.tolist(),'object':owner,'penetration_beyond_skin':.285-minimum}
        samples.append({'position':base.tolist(),'support_base_z':float(base_z),'centre_vertical_hits':z.tolist(),'ring_support_z':ring,'minimum_distance':minimum,'nearest_object':owner})
    routes.append({'y':y,'samples':samples,'missing_support':missing,'steps':steps,'first_block':first_block,
                   'status':'LOCAL_FINITE_CAPSULE_SUPPORT_CLEAR' if not missing and first_block is None and all(s['within_candidate_step'] for s in steps) else 'BLOCKED_OR_REVIEW'})

result={'revision':r['revision'],'pid':os.getpid(),'reopened':True,'mesh_checks':checks,'protected_proxy_components':len(proxy_names),
        'proxy_b82_preserved':True,'terrain_preserved':True,'ssot_preserved':True,'parent_preserved':True,
        'junction_capsule_parameters':{'radius':.30,'height':1.80,'step':.25,'skin':.015,'sample_interval':.05},
        'junction_routes':routes,'scope':'Persistência, malhas e amostras volumétricas locais do encontro ponte/saguão; sem CCD/controller completo.',
        'support_source_objects':[floor.name,*[o.name for o in bridge_sources]],
        'support_method':'character_support.capsule_support: faces e arestas finitas; apoio estático esférico, não projeção central nem controller dinâmico.',
        'protected_baseline_reused_from_same_saved_session':reuse,
        'full_route_approved':False,'installed_elevators_approved':False,'production_ready':False}
(OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
r['reopened']=True;(OUT/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

window=next(w for w in bpy.context.window_manager.windows if w.screen)
eye=M@Vector((-50,-40,97));target=M@Vector((-20,0,72));direction=target-eye
for area in window.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active;space.region_3d.view_perspective='PERSP';space.region_3d.view_rotation=direction.to_track_quat('-Z','Y')
        space.region_3d.view_location=target;space.region_3d.view_distance=direction.length
        space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.overlay.show_overlays=False;area.tag_redraw()
with bpy.context.temp_override(window=window):
    runpy.run_path(str(ROOT/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b86-upper-layout.png'})
print(json.dumps({'revision':r['revision'],'persisted_meshes':len(checks),'reopened':True,'local_junction':[v['status'] for v in routes],'full_route_approved':False},ensure_ascii=False))
