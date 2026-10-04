"""Audita toda a rede registrada com quatro apoios reais da Rondesp, sem editar."""
import bpy, json, math, runpy, hashlib, numpy as np
from pathlib import Path
from collections import Counter
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
source=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['authoring_source']
assert Path(bpy.data.filepath).resolve()==(r/source['file']).resolve()
wm=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['world_matrix']
g=json.loads((r/c['staging']['roads']).read_text(encoding='utf8'));ways={w['osm_way_id']:w for w in g['ways']}
vehicle=next(v for v in json.loads((r/'world/vehicles/catalog.json').read_text(encoding='utf8'))['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')['authoring_base']
# Four pivots and tire geometry are read from the saved asset, never nominal probes.
before=set(bpy.data.objects)
with bpy.data.libraries.load(str(r/vehicle['file']),link=True) as (available,requested):
    requested.objects=[n for n in available.objects if 'Eixo giro roda' in n or 'Pneu 265 65 R17' in n]
pivots=[o for o in requested.objects if 'Eixo giro roda' in o.name]
centers=[list(wm(o).translation) for o in pivots]
tires=[o for o in requested.objects if 'Pneu 265 65 R17' in o.name]
floor=min((wm(o)@Vector(v)).z for o in tires for v in o.bound_box)
contacts=[[p[0],p[1],floor] for p in centers]
assert len(contacts)==4
for ob in set(bpy.data.objects)-before:
    if not ob.users_scene:bpy.data.objects.remove(ob,do_unlink=True)

def tree(ob):
    me=ob.data;me.calc_loop_triangles()
    a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a)
    M=np.array(wm(ob));xyz=a.reshape(-1,3)@M[:3,:3].T+M[:3,3]
    a=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',a)
    tris=a.reshape(-1,3)
    polys=np.empty(len(me.loop_triangles),dtype=np.int32);me.loop_triangles.foreach_get('polygon_index',polys)
    mats=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',mats)
    return BVHTree.FromPolygons(xyz.tolist(),tris.tolist(),all_triangles=True),mats[polys]

terrain=s.objects[c['export']['road_object']];ground,mats=tree(terrain)
proxy,pmats=tree(s.objects[c['export']['terrain_proxy']])
slots={i for i,m in enumerate(terrain.data.materials) if m and m.name in c['export']['road_materials']}
def hit(x,y,z,bvh=ground):
    p,n,idx,_=bvh.ray_cast(Vector((x,y,z+2)),Vector((0,0,-1)),4)
    return None if p is None else (float(p.z),int(idx),float(n.z))

roads={int(o['boas_osm_way_id']):o for o in s.objects if o.name.startswith('R30A7 | ROAD |') and 'boas_osm_way_id' in o}
records=[];metrics=Counter();poses=[];junctions={};max_proxy=0.;wheel_samples=0
halfbase=(max(p[1] for p in contacts)-min(p[1] for p in contacts))/2
midy=(max(p[1] for p in contacts)+min(p[1] for p in contacts))/2
for e in g['edges']:
    way=ways[e['osm_way_id']];ob=roads.get(e['osm_way_id']);k=int(e['id'].rsplit('-',1)[-1]);issues=Counter();samples=[]
    if ob is None:
        records.append({'edge_id':e['id'],'osm_way_id':e['osm_way_id'],'name':way.get('name'),'classification':'SOURCE_LIMITATION','issues':{'scene_binding_missing':1},'approved':False});metrics['scene_binding_missing']+=1;continue
    points=[wm(ob)@Vector(p.co[:3]) for sp in ob.data.splines for p in sp.points]
    bindings={i:p for i,p in enumerate(points)} if len(points)==len(way['node_refs']) else {}
    if not bindings:
        for point in points:
            matches=[i for i,xy in enumerate(way['blender_xy']) if math.dist(list(point)[:2],xy)<.01]
            if len(matches)==1:bindings[matches[0]]=point
    if k not in bindings or k+1 not in bindings:
        records.append({'edge_id':e['id'],'osm_way_id':e['osm_way_id'],'classification':'NEEDS_REVIEW','issues':{'unresolved_endpoint_binding':1},'approved':False});metrics['unresolved_endpoint_binding']+=1;continue
    a,b=bindings[k],bindings[k+1];d=(b-a).to_2d();length=d.length
    if length<.01:continue
    f=d.normalized();sx=Vector((-f.y,f.x));steps=math.ceil(length/1.0);prior=None;prior_fraction=None;clear_run=[]
    for i in range(steps+1):
        q=a.lerp(b,i/steps);center=hit(q.x,q.y,q.z)
        datum={'fraction':i/steps,'point':list(q),'issues':[]}
        if center is None:
            datum['issues'].append('center_support_missing')
        elif mats[center[1]] not in slots:
            datum['issues'].append('center_outside_pavement')
        supports=[];proxy_diffs=[]
        if center is not None:
            for px,py,pz in contacts:
                wheel_samples+=1;xy=q.to_2d()+sx*px-f*(py-midy);v=hit(xy.x,xy.y,center[0]);pv=hit(xy.x,xy.y,center[0],proxy)
                supports.append(v)
                if v is None:datum['issues'].append('wheel_support_missing')
                elif mats[v[1]] not in slots:datum['issues'].append('wheel_outside_pavement')
                if v is not None:
                    if pv is None:datum['issues'].append('collision_support_missing')
                    else:
                        diff=abs(pv[0]-v[0]);max_proxy=max(max_proxy,diff);proxy_diffs.append(diff)
                        if diff>.05:datum['issues'].append('collision_visual_difference')
        if len(supports)==4 and all(v is not None for v in supports):
            A=np.array([[1,px,-(py-midy)] for px,py,pz in contacts]);zs=np.array([v[0] for v in supports]);z,bank,grade=np.linalg.lstsq(A,zs,rcond=None)[0]
            residual=float(np.max(np.abs(A@np.array([z,bank,grade])-zs)))
            if residual>.08:datum['issues'].append('four_wheel_twist')
            if abs(bank)>.15:datum['issues'].append('crossfall_review')
            if abs(grade)>.30:datum['issues'].append('grade_review')
            if prior is not None and prior_fraction is not None and abs(z-prior)>length*(i/steps-prior_fraction)*.4+.08:datum['issues'].append('vertical_discontinuity')
            prior=z;prior_fraction=i/steps
            up=Vector((-sx.x*bank-f.x*grade,-sx.y*bank-f.y*grade,1)).normalized()
            fw=Vector((f.x,f.y,grade)).normalized();right=up.cross(fw).normalized();up=fw.cross(right).normalized()
            rotation=Matrix((right,-fw,up)).transposed().to_quaternion()
            datum.update({'grade':float(grade),'bank':float(bank),'wheel_residual_m':residual,'max_proxy_difference_m':max(proxy_diffs,default=None)})
            datum['pose']={'location':[q.x-f.x*midy,q.y-f.y*midy,float(z-floor)],'rotation':list(rotation)}
            if not datum['issues'] and e.get('access')!='restricted':
                clear_run.append({'edge_id':e['id'],'osm_way_id':e['osm_way_id'],'name':way.get('name'),'fraction':i/steps,**datum['pose']})
        if len(supports)!=4 or not all(v is not None for v in supports):
            prior=None;prior_fraction=None
        for kind in set(datum['issues']):issues[kind]+=1;metrics[kind]+=1
        samples.append(datum)
    # Runs remain separate: unsupported samples never get bridged by animation.
    if clear_run:poses.append({'edge_id':e['id'],'direction':e['direction'],'samples':clear_run,'full_segment_clear':not issues})
    records.append({'edge_id':e['id'],'osm_way_id':e['osm_way_id'],'name':way.get('name'),'direction':e['direction'],'access':e.get('access'),
                    'length_m':length,'classification':'NEEDS_REVIEW' if issues else 'KEEP_GAMEPLAY','issues':dict(issues),'samples':samples,'approved':False})
    for nid,p in [(e['from'],a),(e['to'],b)]:junctions.setdefault(nid,[]).append((e['id'],list(p)))
layer_conflicts=[]
for node,entries in junctions.items():
    zs=[p[2] for _,p in entries]
    if max(zs)-min(zs)>.25:layer_conflicts.append({'node_id':node,'height_spread_m':max(zs)-min(zs),'bindings':entries,'classification':'NEEDS_REVIEW'})
report={'source_before':source,'vehicle':vehicle,'method':'Todos os segmentos do grafo registrado, com binding por mesma OSM ID e ordem de nós; passos <=1 m; quatro apoios extraídos do asset. Raios locais ±2 m não saltam automaticamente à pista superior.',
        'dynamic_physics_tested':False,'approved':False,'obstacle_sweep_pending':True,'driver_view_pending':True,'terrain_changed':False,
        'vehicle_contacts_asset_local':contacts,'wheelbase_measured_m':2*halfbase,'vehicle_floor_z':floor,'graph_edges':len(g['edges']),
        'segments':records,'poses':[p for p in poses],'wheel_samples':wheel_samples,'issue_counts':dict(metrics),'layer_conflicts':layer_conflicts,
        'max_collision_visual_difference_m':max_proxy,'geometric_clear_segments':sum(not row['issues'] for row in records),
        'thresholds_candidate':{'spacing_m':1,'proxy_difference_m':.05,'wheel_twist_m':.08,'grade':.30,'crossfall':.15},
        'coverage_scope':'Rede registrada do recorte; não representa todas as ruas de Salvador nem todos os itinerários possíveis.'}
out=r/globals().get('BOAS_REPORT_PATH','docs/reports/blender/rondesp_network_audit_b38.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:report[k] for k in ['graph_edges','wheel_samples','issue_counts','geometric_clear_segments','max_collision_visual_difference_m']}))
