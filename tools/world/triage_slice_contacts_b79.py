"""Triagem: testemunhas de penetração sólida e travessias OSM, sem inferir arquitetura."""
import json,itertools,collections
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--geometry',type=Path,default=ROOT/'artifacts/lacerda-controller/geometry_b77b.json')
parser.add_argument('--output-dir',type=Path,default=ROOT/'docs/reports/blender/lacerda-controller');parser.add_argument('--suffix',default='b77b');parser.add_argument('--report-name',default='triage_b79.json');args=parser.parse_args()
OUT=args.output_dir;OUT.mkdir(parents=True,exist_ok=True)
d=json.loads(args.geometry.read_text(encoding='utf8'))
rows={r['name']:r for r in d['objects']};sweep=json.loads((OUT/f'cabin_sweep_{args.suffix}.json').read_text(encoding='utf8'))
def convex_solid(g):
    if not g['complete_mesh']:return None
    v=np.asarray(g['vertices']);f=np.asarray(g['triangles']);edges=collections.Counter(tuple(sorted((int(a),int(b)))) for face in f for a,b in zip(face,np.roll(face,-1)))
    if any(n!=2 for n in edges.values()):return None
    tri=v[f];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm=np.linalg.norm(n,axis=1);sel=norm>1e-10
    n=n[sel]/norm[sel,None];origin=tri[sel,0];centroid=v.mean(axis=0)
    n*=np.where(np.sum((centroid-origin)*n,axis=1)>0,-1,1)[:,None]
    offset=np.sum(n*origin,axis=1)
    if np.max(v@n.T-offset)>1e-5:return None
    return n,offset
delta=np.asarray(sweep['motion']['translation']);confirmed=[]
for contact in sweep['contacts']:
    target=rows[contact['obstacle']];moving=rows[contact['cabin_component']]
    target_planes=convex_solid(target['geometry']);moving_planes=convex_solid(moving['geometry'])
    if target_planes is None or moving_planes is None:continue
    mv=np.asarray(moving['geometry']['vertices']);tv=np.asarray(target['geometry']['vertices'])
    for t in np.linspace(contact['t_first'],contact['t_last'],21)[1:-1]:
        n,offset=target_planes;inside=np.max((mv+delta*t)@n.T-offset,axis=1)<-1e-4
        mn,mo=moving_planes;reverse=np.max((tv-delta*t)@mn.T-mo,axis=1)<-1e-4
        if inside.any() or reverse.any():
            confirmed.append({'component':contact['cabin_component'],'obstacle':contact['obstacle'],
                'classification':'ERROR','t_witness':float(t),'floor_z':d['qa']['elevator']['upper_z']+float(t*delta[2]),
                'evidence':'vertex strictly inside watertight convex solid by all oriented face halfspaces',
                'minimum_interior_threshold':.0001,'architectural_correction':'pending verified dimensions; do not resize to fit'})
            break
ref=json.loads((ROOT/'artifacts/structural-pipeline/centro-lapa-tororo-fontenova/structural_reference.json').read_text(encoding='utf8'))
route=np.asarray(d['qa']['routes']['lower']['points'])[:,:2];crossings=[];intersections=[]
def intersection(a,b,c,e):
    ab=b-a;ce=e-c;det=ab[0]*ce[1]-ab[1]*ce[0]
    if abs(det)<1e-10:return None
    rel=c-a;t=(rel[0]*ce[1]-rel[1]*ce[0])/det;u=(rel[0]*ab[1]-rel[1]*ab[0])/det
    return (a+t*ab).tolist() if 0<=t<=1 and 0<=u<=1 else None
for f in ref['features']:
    tags=f.get('tags',{});pts=np.asarray(f['blender_xy'])
    if tags.get('footway')=='crossing':
        near=min(float(np.linalg.norm(p-q)) for p in route for q in pts)
        if near<20:crossings.append({'osm_id':f['osm_id'],'coordinates':pts.tolist(),'nearest_route_vertex_to_source_vertex':near,'source_classification':'KEEP_REAL_REFERENCE','route_alignment':'NEEDS_REVIEW'})
    if tags.get('highway') not in ('primary','secondary','tertiary','residential','service'):continue
    if not (np.all(pts.max(axis=0)>=route.min(axis=0)) and np.all(pts.min(axis=0)<=route.max(axis=0))):continue
    for index,(a,b) in enumerate(zip(route,route[1:])):
        for c,e in zip(pts,pts[1:]):
            hit=intersection(a,b,c,e)
            if hit:intersections.append({'segment':index,'road_osm_id':f['osm_id'],'name':tags.get('name'),
                'point':hit,'traffic_permission':None,'marked_crossing_match':None,'classification':'NEEDS_REVIEW'})
report={'solid_penetration_witnesses':confirmed,'continuous_surface_contacts':len(sweep['contacts']),
        'other_contacts':'NEEDS_REVIEW; includes tangency/non-convex/source uncertainty',
        'source_crossings':crossings,'route_road_intersections':intersections,
        'traffic_gate':'blocked until source crossing binding and runtime traffic permission verified',
        'full_solid_containment_approved':False,'physical_dimensions_verified':False}
(OUT/args.report_name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'confirmed_solid_penetrations':len(confirmed),'road_intersections':len(intersections),'nearby_source_crossings':len(crossings)}))
