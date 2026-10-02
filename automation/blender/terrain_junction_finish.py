"""Unifica a plataforma do encontro e corrige seu proxy sem mudar limites XY."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text())
if c['world_source']['revision']!='R30B.24':raise RuntimeError('Revisão esperada R30B24')
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():bpy.ops.wm.open_mainfile(filepath=str(root/c['world_source']['file']))
scene=bpy.context.scene;o=scene.objects[c['export']['road_object']];mesh=o.data;mesh.calc_loop_triangles();ps=[o.matrix_world@v.co for v in mesh.vertices];xy=[tuple(v.co[:2]) for v in mesh.vertices]
slots={i for i,m in enumerate(mesh.materials) if m and m.name in c['export']['road_materials']};ids={i for f in mesh.polygons if f.material_index in slots for i in f.vertices};inverse=o.matrix_world.inverted();center=Vector((-169.42958068847656,-177.65443420410156,57.752227783203125));changed=0;maxdelta=0;targets={}
for id in ids:
    p=ps[id];d=math.hypot(p.x-center.x,p.y-center.y)
    if d>=18 or not 53<p.z<63:continue
    blend=max(0,min(1,(18-d)/8));blend=blend*blend*(3-2*blend);z=p.z+(center.z-p.z)*blend
    targets[id]=z;maxdelta=max(maxdelta,abs(z-p.z))
seams={}
for id,z in targets.items():p=ps[id];seams.setdefault((round(p.x,5),round(p.y,5)),[]).append((p.z,z))
for id,p in enumerate(ps):
    z=targets.get(id)
    if z is None:
        near=[v for v in seams.get((round(p.x,5),round(p.y,5)),[]) if abs(v[0]-p.z)<.02]
        if near:z=sum(v[1] for v in near)/len(near)
    if z is not None and abs(z-p.z)>1e-5:mesh.vertices[id].co.z=(inverse@Vector((p.x,p.y,z))).z;changed+=1
mesh.update();assert all(tuple(v.co[:2])==xy[v.index] for v in mesh.vertices)
# The proxy is demonstrably stale (~3.56 m above the authored surface). Correct
# existing XY vertices by individual samples of the visible source. This is
# not a guessed global Z offset or a dense visual mesh used as collider.
mesh.calc_loop_triangles();tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in mesh.vertices],[list(t.vertices) for t in mesh.loop_triangles],all_triangles=True)
proxy=scene.objects[c['export']['terrain_proxy']];pinv=proxy.matrix_world.inverted();proxychanged=0;proxymax=0;missing=[];proxyxy=[tuple(v.co[:2]) for v in proxy.data.vertices]
for v in proxy.data.vertices:
    p=proxy.matrix_world@v.co
    q=tree.ray_cast(Vector((p.x,p.y,160)),Vector((0,0,-1)),350)[0]
    if q is None:missing.append(v.index);continue
    delta=abs(q.z-p.z);proxymax=max(proxymax,delta)
    if delta>1e-5:v.co.z=(pinv@Vector((p.x,p.y,q.z))).z;proxychanged+=1
proxy.data.update();assert all(tuple(v.co[:2])==proxyxy[v.index] for v in proxy.data.vertices)
proxy['boas_support_source']=o.name;proxy['boas_proxy_status']='Reprojeção individual Z sobre fonte visual; sem suporte em '+str(len(missing))+' vértices, revisar bordas antes de exportar'
report={'source_before':c['world_source'].copy(),'classification':'ADAPT_LOCAL','purpose':'plataforma comum do encontro para retirar torção transversal residual; patamares externos e larguras preservados','center_from_authored_osm_junction':list(center),'core_radius_m':10,'transition_end_radius_m':18,'radius_is_road_width':False,'changed_vertices':changed,'max_height_change_m':maxdelta,'xy_changed':False,'widths_changed':False,'materials_changed':False,'topology_changed':False,'changed_proxy_vertices':proxychanged,'maximum_stale_proxy_correction_m':proxymax,'proxy_missing_support_vertices':len(missing),'proxy_missing_support_ids':missing,'proxy_method':'individual source mesh samples at unchanged XY; no global Z fit/offset','vehicle_retest':'pending','runtime_exported':False,'visual_review':'pending'}
out=root/'blender/salvador_lacerda_r30b25_encontro_continuo.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));c['world_source'].update(file=out.relative_to(root).as_posix(),sha256=hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),revision='R30B.25',selection_reason='Derivada da R30B23; plataforma contínua do encontro Montanha/Pau da Bandeira e proxy local, sem alterar larguras ou XY. Revisão parcial do terreno.');cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8');report['source_after']=c['world_source'];(root/'docs/reports/blender/terrain_junction_finish.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
