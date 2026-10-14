"""Caracterização read-only das paradas; não autoriza mudança de cena."""
import json
import numpy as np
from audit_chile_pedestrian_routes import ROOT, OUT, R, H, SKIN
from character_support import capsule_support
from slice_geometry import capsule_distances


def main():
    meta=json.loads((OUT/'helpers.json').read_text(encoding='utf8'))
    data=np.load(ROOT/meta['physics_file'])
    physical,visual=data['physical'],data['visual']
    features=json.loads((ROOT/'artifacts/structural-pipeline/centro-lapa-tororo-fontenova/structural_reference.json').read_text(encoding='utf8'))['features']
    by={f['osm_id']:f for f in features if f['osm_type']=='way'}
    routes=json.loads((OUT/'sweeps.json').read_text(encoding='utf8'))['routes']
    records=[]
    for route in routes:
        stop=route['replay'].get('stop')
        if not stop:continue
        p=np.array(stop.get('position') or stop['witness']['position'])
        def nearby(ts):
            return ts[(ts.max(axis=1)[:,0]>=p[0]-R-SKIN)&(ts.min(axis=1)[:,0]<=p[0]+R+SKIN)&(ts.max(axis=1)[:,1]>=p[1]-R-SKIN)&(ts.min(axis=1)[:,1]<=p[1]+R+SKIN)&(ts.max(axis=1)[:,2]>=p[2]-.4)&(ts.min(axis=1)[:,2]<=p[2]+.25)]
        ground=physical[:meta['physics_objects'][0]['count']]
        a,b=nearby(ground),nearby(visual)
        ps=capsule_support(*p[:2],a,p[2]-.4,p[2]+.25,R,SKIN)
        vs=capsule_support(*p[:2],b,p[2]-.4,p[2]+.25,R,SKIN)
        row={'route':route['route'],'stop_reason':stop['reason'],'position':p.tolist(),'physical_capsule_support_z':ps,'visual_capsule_support_z':vs,'difference':None if ps is None or vs is None else ps-vs,'visual_min_capsule_distance':None if not len(b) else float(capsule_distances(p,b,R,H).min()),'classification':'NEEDS_REVIEW','scene_change_authorized':False}
        witness=stop.get('witness')
        if witness:
            pts=np.array([xy for oid in route['osm_way_ids'] for xy in by[oid]['blender_xy']]);lo=pts.min(axis=0)-1;hi=pts.max(axis=0)+1
            mask=np.all(physical.max(axis=1)[:,:2]>=lo,axis=1)&np.all(physical.min(axis=1)[:,:2]<=hi,axis=1)
            tri=physical[mask][witness['triangle']];normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);normal/=np.linalg.norm(normal)
            row.update({'witness_triangle':tri.tolist(),'witness_normal':normal.tolist(),'source_collider':witness['object'],'penetration':witness['penetration'],'architectural_function':'Terrain proxy triangle; permanent curb/step identity not established'})
        records.append(row)
    report={'scene_changed':False,'records':records,'conclusion':'Local support/clearance discrepancies; no independently proven architectural correction. Keep routes blocked.'}
    (OUT/'contact_diagnosis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
