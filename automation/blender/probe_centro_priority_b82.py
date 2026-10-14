"""Sondagem read-only de apoios no cluster Tomé/Chile; não certifica controller."""
import bpy,json,runpy,math,traceback
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/reports/world/centro-structural-triage'
wm=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['world_matrix']
scene=bpy.data.scenes['SALVADOR | ESBOCO OFICIAL']
contract=json.loads((ROOT/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
try:
    objects=[scene.objects[contract['export'][key]] for key in ('road_object','terrain_proxy')]
    features=json.loads((ROOT/'artifacts/structural-pipeline/centro-lapa-tororo-fontenova/structural_reference.json').read_text(encoding='utf8'))['features']
    targets=[30968017,231091547,258560240,312006925,1423065746]
    selection=[p for f in features if f['osm_type']=='way' and f['osm_id'] in targets for p in f['blender_xy']]
    roi=[min(p[i] for p in selection)-2 for i in range(2)]+[max(p[i] for p in selection)+2 for i in range(2)]
    trees=[]
    for ob in objects:
        m=np.array(wm(ob));mesh=ob.data;mesh.calc_loop_triangles()
        buf=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',buf)
        xyz=buf.reshape(-1,3)@m[:3,:3].T+m[:3,3]
        ids=np.empty(len(mesh.loop_triangles)*3,dtype=np.int32);mesh.loop_triangles.foreach_get('vertices',ids)
        tris=ids.reshape(-1,3);points=xyz[tris]
        low=points.min(axis=1);high=points.max(axis=1)
        mask=(low[:,0]<roi[2])&(high[:,0]>roi[0])&(low[:,1]<roi[3])&(high[:,1]>roi[1])
        tris=tris[mask];used,remap=np.unique(tris,return_inverse=True)
        trees.append(BVHTree.FromPolygons(xyz[used].tolist(),remap.reshape(-1,3).tolist(),all_triangles=True))
    rows=[]
    for f in features:
        if f['osm_type']!='way' or f['osm_id'] not in targets:continue
        samples=[]
        for segment,(a,b) in enumerate(zip(f['blender_xy'],f['blender_xy'][1:])):
            length=math.dist(a,b);count=max(1,math.ceil(length/2));dx=(b[0]-a[0])/length if length else 0;dy=(b[1]-a[1])/length if length else 0
            for i in range(count+1):
                t=i/count;x=a[0]+t*(b[0]-a[0]);y=a[1]+t*(b[1]-a[1]);contacts=[]
                for offset in (0.,-.30,.30):
                    xy=[x-dy*offset,y+dx*offset];hits=[]
                    for tree in trees:
                        p,n,index,d=tree.ray_cast(Vector((*xy,120)),Vector((0,0,-1)),200)
                        hits.append({'z':p.z,'normal_z':n.z} if p is not None else None)
                    contacts.append({'offset':offset,'visual':hits[0],'collider':hits[1],
                                     'difference':abs(hits[0]['z']-hits[1]['z']) if all(hits) else None})
                samples.append({'segment':segment,'fraction':t,'xy':[x,y],'contacts':contacts})
        supported=[c for s in samples for c in s['contacts'] if c['visual'] and c['collider']]
        gaps=[s for s in samples if any(not c['visual'] or not c['collider'] for c in s['contacts'])]
        rows.append({'osm_way_id':f['osm_id'],'name':f.get('tags',{}).get('name'),'samples':len(samples),
                     'support_missing_samples':len(gaps),'max_visual_collider_difference':max((c['difference'] for c in supported),default=None),
                     'differences_over_005':sum(c['difference']>.05 for c in supported),'samples_detail':samples,
                     'classification':'NEEDS_REVIEW','controller_approved':False})
    helpers=[o for o in scene.objects if 'boas_osm_way_id' in o and o.name.startswith('R30A7 | ROAD |')]
    report={'scene_changed':False,'source':'B82 historical layer','source_surfaces':[o.name for o in objects],
            'roi':roi,'scope':'Legacy MVP visual/collider only; missing support may indicate layer coverage, not absence of all scene floors',
            'rows':rows,'helper_metadata':[{'osm_way_id':int(o['boas_osm_way_id']),'unresolved_nodes':o.get('boas_unresolved_nodes'),
                                         'partial_source':o.get('boas_partial_source'),'runtime_role':o.get('boas_runtime_role')} for o in helpers],
            'sweep_character_done':False,'physical_route_certified':False}
    (OUT/'priority_support_b82.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps([{k:v for k,v in r.items() if k!='samples_detail'} for r in rows],ensure_ascii=False))
except Exception:
    (OUT/'priority_support_error.txt').write_text(traceback.format_exc(),encoding='utf8')
    raise
