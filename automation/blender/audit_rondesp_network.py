"""Audita toda a rede registrada com quatro apoios reais da Rondesp, sem editar."""
import bpy, json, math, runpy, numpy as np
from pathlib import Path
from collections import Counter
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

r=Path(__file__).resolve().parents[2];s=bpy.context.scene
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
registry_source=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['authoring_source']
source=globals().get('BOAS_SOURCE_OVERRIDE') or registry_source
assert Path(bpy.data.filepath).resolve()==(r/source['file']).resolve()
wm=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['world_matrix']
g=json.loads((r/c['staging']['roads']).read_text(encoding='utf8'));ways={w['osm_way_id']:w for w in g['ways']}
vehicle=next(v for v in json.loads((r/'world/vehicles/catalog.json').read_text(encoding='utf8'))['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')['authoring_base']

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

def edge_profile(ob,way,k,tol=.02):
    """Extrai a polilinha do helper entre os nós OSM k e k+1, preservando orientação."""
    flat=[wm(ob)@Vector(p.co[:3]) for sp in ob.data.splines for p in sp.points]
    if len(flat)==len(way['node_refs']):
        return [flat[k],flat[k+1]]
    a=Vector((float(way['blender_xy'][k][0]),float(way['blender_xy'][k][1])))
    b=Vector((float(way['blender_xy'][k+1][0]),float(way['blender_xy'][k+1][1])))
    found=[]
    for sp in ob.data.splines:
        pts=[wm(ob)@Vector(p.co[:3]) for p in sp.points]
        ia=[i for i,p in enumerate(pts) if (p.to_2d()-a).length<tol]
        ib=[i for i,p in enumerate(pts) if (p.to_2d()-b).length<tol]
        for i in ia:
            for j in ib:
                if i<j:found.append(pts[i:j+1])
                elif j<i:found.append(list(reversed(pts[j:i+1])))
    unique=[]
    for poly in found:
        key=tuple((round(p.x,5),round(p.y,5),round(p.z,5)) for p in poly)
        if key not in [u[0] for u in unique]:unique.append((key,poly))
    return unique[0][1] if len(unique)==1 else None

def sample_profile(poly,spacing=1.0):
    lens=[(poly[i+1]-poly[i]).to_2d().length for i in range(len(poly)-1)]
    total=sum(lens)
    if total<.01:return total,[]
    cum=[0.0]
    for L in lens:cum.append(cum[-1]+L)
    steps=math.ceil(total/spacing);out=[]
    seg=0
    for i in range(steps+1):
        d=total*i/steps
        while seg<len(lens)-1 and d>cum[seg+1]+1e-9:seg+=1
        L=lens[seg]
        t=0.0 if L<1e-9 else max(0.0,min(1.0,(d-cum[seg])/L))
        q=poly[seg].lerp(poly[seg+1],t)
        f=(poly[seg+1]-poly[seg]).to_2d()
        if f.length<1e-9:continue
        f.normalize()
        out.append((i/steps,d,q,f))
    return total,out

roads={int(o['boas_osm_way_id']):o for o in s.objects if o.name.startswith('R30A7 | ROAD |') and 'boas_osm_way_id' in o}
records=[];metrics=Counter();poses=[];junctions={};max_proxy=0.;wheel_samples=0
halfbase=(max(p[1] for p in contacts)-min(p[1] for p in contacts))/2
midy=(max(p[1] for p in contacts)+min(p[1] for p in contacts))/2

for e in g['edges']:
    way=ways[e['osm_way_id']];ob=roads.get(e['osm_way_id']);k=int(e['id'].rsplit('-',1)[-1]);issues=Counter();samples=[]
    if ob is None:
        records.append({'edge_id':e['id'],'osm_way_id':e['osm_way_id'],'name':way.get('name'),'classification':'SOURCE_LIMITATION','issues':{'scene_binding_missing':1},'approved':False});metrics['scene_binding_missing']+=1;continue
    poly=edge_profile(ob,way,k)
    if poly is None:
        records.append({'edge_id':e['id'],'osm_way_id':e['osm_way_id'],'classification':'NEEDS_REVIEW','issues':{'unresolved_endpoint_binding':1},'approved':False});metrics['unresolved_endpoint_binding']+=1;continue
    length,profile_samples=sample_profile(poly,1.0)
    if not profile_samples:continue
    prior=None;prior_distance=None;clear_run=[]
    for fraction,distance,q,f in profile_samples:
        sx=Vector((-f.y,f.x));center=hit(q.x,q.y,q.z)
        datum={'fraction':fraction,'point':list(q),'issues':[]}
        if center is None:datum['issues'].append('center_support_missing')
        elif mats[center[1]] not in slots:datum['issues'].append('center_outside_pavement')
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
            if prior is not None and prior_distance is not None and abs(z-prior)>(distance-prior_distance)*.4+.08:datum['issues'].append('vertical_discontinuity')
            prior=z;prior_distance=distance
            up=Vector((-sx.x*bank-f.x*grade,-sx.y*bank-f.y*grade,1)).normalized()
            fw=Vector((f.x,f.y,grade)).normalized();right=up.cross(fw).normalized();up=fw.cross(right).normalized()
            rotation=Matrix((right,-fw,up)).transposed().to_quaternion()
            datum.update({'grade':float(grade),'bank':float(bank),'wheel_residual_m':residual,'max_proxy_difference_m':max(proxy_diffs,default=None)})
            datum['pose']={'location':[q.x-f.x*midy,q.y-f.y*midy,float(z-floor)],'rotation':list(rotation)}
            if not datum['issues'] and e.get('access')!='restricted':
                clear_run.append({'edge_id':e['id'],'osm_way_id':e['osm_way_id'],'name':way.get('name'),'fraction':fraction,**datum['pose']})
        if len(supports)!=4 or not all(v is not None for v in supports):prior=None;prior_distance=None
        for kind in set(datum['issues']):issues[kind]+=1;metrics[kind]+=1
        samples.append(datum)
    if clear_run:poses.append({'edge_id':e['id'],'direction':e['direction'],'samples':clear_run,'full_segment_clear':not issues})
    record={'edge_id':e['id'],'osm_way_id':e['osm_way_id'],'name':way.get('name'),'direction':e['direction'],'access':e.get('access'),
            'length_m':length,'classification':'NEEDS_REVIEW' if issues else 'KEEP_GAMEPLAY','issues':dict(issues),'samples':samples,'approved':False}
    if len(poly)>2:
        record['profile_points']=len(poly)
    records.append(record)
    for nid,p in [(e['from'],poly[0]),(e['to'],poly[-1])]:junctions.setdefault(nid,[]).append((e['id'],list(p)))

layer_conflicts=[]
for node,entries in junctions.items():
    zs=[p[2] for _,p in entries]
    if max(zs)-min(zs)>.25:layer_conflicts.append({'node_id':node,'height_spread_m':max(zs)-min(zs),'bindings':entries,'classification':'NEEDS_REVIEW'})
report={'source_before':source,'vehicle':vehicle,'method':'Todos os segmentos do grafo registrado; helper ligado por mesma OSM ID e nós fonte. Perfis densificados são seguidos pela polilinha derivada, sem voltar a ligar endpoints em linha reta. Passos <=1 m; quatro apoios extraídos do asset. Raios locais ±2 m não saltam automaticamente à pista superior.',
        'dynamic_physics_tested':False,'approved':False,'obstacle_sweep_pending':True,'driver_view_pending':True,'terrain_changed':False,
        'vehicle_contacts_asset_local':contacts,'wheelbase_measured_m':2*halfbase,'vehicle_floor_z':floor,'graph_edges':len(g['edges']),
        'segments':records,'poses':poses,'wheel_samples':wheel_samples,'issue_counts':dict(metrics),'layer_conflicts':layer_conflicts,
        'max_collision_visual_difference_m':max_proxy,'geometric_clear_segments':sum(not row['issues'] for row in records),
        'thresholds_candidate':{'spacing_m':1,'proxy_difference_m':.05,'wheel_twist_m':.08,'grade':.30,'crossfall':.15},
        'coverage_scope':'Rede registrada do recorte; não representa todas as ruas de Salvador nem todos os itinerários possíveis.'}
out=r/globals().get('BOAS_REPORT_PATH','docs/reports/blender/rondesp_network_audit_b38.json')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:report[k] for k in ['graph_edges','wheel_samples','issue_counts','geometric_clear_segments','max_collision_visual_difference_m']}))
