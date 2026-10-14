"""Sweep QA do recorte exportado. Não implementa runtime ou aprova tráfego."""
import json,math,sys
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/world'))
from slice_geometry import capsule_distances,support_hits
from character_slide import lateral_contact,project_slide
from character_support import capsule_support
OUT=ROOT/'docs/reports/world/chile-pedestrian-b82'
R,H,STEP,SKIN=.30,1.80,.25,.015

def replay(points,physical,visual,names):
    lo=physical.min(axis=1);hi=physical.max(axis=1);vlo=visual.min(axis=1);vhi=visual.max(axis=1)
    def ground(p,maximum,ts=physical,ns=names):
        low,high=(lo,hi) if ts is physical else (vlo,vhi)
        ids=np.flatnonzero((high[:,0]>=p[0]-R-SKIN)&(low[:,0]<=p[0]+R+SKIN)&(high[:,1]>=p[1]-R-SKIN)&(low[:,1]<=p[1]+R+SKIN)&(high[:,2]>=p[2]-.4)&(low[:,2]<=maximum)&(ns==0))
        return capsule_support(p[0],p[1],ts[ids],p[2]-.4,maximum,R,SKIN)
    def clear(a,b):
        mask=np.all(hi>=np.minimum(a,b)-[R+SKIN,R+SKIN,0],axis=1)&np.all(lo<=np.maximum(a,b)+[R+SKIN,R+SKIN,H],axis=1)
        ids=np.flatnonzero(mask)
        if not len(ids):return True,None
        ts=physical[ids];witness=None
        def interval(t0,t1,depth):
            nonlocal witness
            p=a+(b-a)*(t0+t1)/2;ds=capsule_distances(p,ts,R,H);k=int(np.argmin(ds))
            # Mesmo limite conservador do solver histórico: penetração > skin.
            threshold=R-SKIN
            if ds[k]<threshold:
                witness={'triangle':int(ids[k]),'object_index':int(names[ids[k]]),'penetration':float(R-ds[k]),'position':p.tolist(),'classification':'SOLID_PENETRATION'};return False
            if ds[k]-threshold>np.linalg.norm(b-a)*(t1-t0)/2+1e-8:return True
            if depth>=12:
                witness={'triangle':int(ids[k]),'classification':'NEEDS_REVIEW_CONTACT_CONVERGENCE','distance':float(ds[k]),'position':p.tolist()};return False
            return interval(t0,(t0+t1)/2,depth+1) and interval((t0+t1)/2,t1,depth+1)
        return interval(0,1,0),witness
    start=np.array([*points[0],100.]);mask=(hi[:,0]>=start[0]-R-SKIN)&(lo[:,0]<=start[0]+R+SKIN)&(hi[:,1]>=start[1]-R-SKIN)&(lo[:,1]<=start[1]+R+SKIN)&(names==0)
    level=capsule_support(start[0],start[1],physical[mask],-20,120,R,SKIN)
    if level is None:return {'status':'START_SUPPORT_UNKNOWN','moves':0}
    start[2]=level;p=start.copy();velocity=0.;events=[];stopped=None
    ok,w=clear(p,p)
    if not ok:return {'status':'START_CAPSULE_BLOCKED','moves':0,'witness':w,'position':p.tolist()}
    for target in points[1:]:
        delta=np.array(target)-p[:2];dist=np.linalg.norm(delta);steps=max(1,math.ceil(dist/(2.5/60)));increment=delta/steps
        for _ in range(steps):
            old=p.copy();velocity-=9.81/60;proposal=p.copy();proposal[:2]+=increment;proposal[2]+=velocity/60
            support=ground(proposal,p[2]+STEP)
            if support is not None and abs(support-p[2])<=STEP:proposal[2]=support;velocity=0.
            ok,w=clear(p,proposal);step_attempt=None;slide_attempt=None
            if not ok:
                raised=p+[0,0,STEP];across=raised.copy();across[:2]=proposal[:2];support=ground(across,raised[2]);drop=across.copy()
                if support is not None:drop[2]=support
                step_attempt={'support':support,'height':STEP,'raise':raised.tolist(),'forward':across.tolist(),'drop':drop.tolist()}
                a=clear(p,raised);b=clear(raised,across) if a[0] else (False,None);c=clear(across,drop) if b[0] and support is not None else (False,None)
                if support is not None and a[0] and b[0] and c[0]:proposal=drop;velocity=0.
                else:
                    mask=np.all(hi>=np.minimum(p,proposal)-[R,R,0],axis=1)&np.all(lo<=np.maximum(p,proposal)+[R,R,H],axis=1);ids=np.flatnonzero(mask)
                    contact=lateral_contact(p,proposal,np.array(w['position']) if w else proposal,physical[ids],R,H,SKIN) if len(ids) else None
                    slide_attempt={'contact_found':contact is not None}
                    if contact is not None:
                        slide=project_slide(p,proposal,contact['normal']);support=ground(slide,p[2]+SKIN)
                        if support is not None and slide[2]<=support:slide[2]=support
                        good,sw=clear(p,slide);slide_attempt.update({'normal':contact['normal'].tolist(),'support':support,'clear':good})
                        if good and np.linalg.norm(slide[:2]-p[:2])>1e-4:proposal=slide
                        else:stopped={'reason':'COLLISION_STEP_SLIDE_BLOCKED','witness':w,'step':step_attempt,'slide':slide_attempt};break
                    else:stopped={'reason':'COLLISION_NO_LATERAL_CONTACT','witness':w,'step':step_attempt,'slide':slide_attempt};break
            support=ground(proposal,proposal[2]+SKIN)
            if support is None or abs(proposal[2]-support)>.02:
                stopped={'reason':'SUPPORT_NOT_CONTINUOUS','support':support,'position':proposal.tolist()};break
            # Apoio de collider deve possuir visual correspondente, sem piso invisível.
            visible=ground(proposal,proposal[2]+STEP,visual,np.zeros(len(visual),int))
            if visible is None or abs(visible-support)>.05:stopped={'reason':'VISIBLE_SUPPORT_NOT_MATCHED','position':proposal.tolist()};break
            p=proposal;events.append({'position':p.tolist(),'support_z':support,'step':step_attempt,'slide':slide_attempt})
        if stopped:break
        if np.linalg.norm(p[:2]-np.array(target))>.06:
            stopped={'reason':'SLIDE_DID_NOT_REACH_SOURCE_CONTROL','position':p.tolist(),'control':target};break
    return {'support_solver':'finite-lower-sphere-v1-bounded-ground-snap','status':'NUMERIC_SCOPE_PASSED' if stopped is None else 'NUMERIC_SCOPE_BLOCKED','moves':len(events),'stop':stopped,
            'final':p.tolist(),'trace':events,'engine_approved':False,'gameplay_valid':False}

def main():
    meta=json.loads((OUT/'helpers.json').read_text(encoding='utf8'));data=np.load(ROOT/meta['physics_file']);physical=data['physical'];visual=data['visual']
    names=np.empty(len(physical),int)
    for i,row in enumerate(meta['physics_objects']):names[row['first']:row['first']+row['count']]=i
    features=json.loads((ROOT/'artifacts/structural-pipeline/centro-lapa-tororo-fontenova/structural_reference.json').read_text(encoding='utf8'))['features'];by={f['osm_id']:f for f in features if f['osm_type']=='way'}
    routes={'CHILE_TO_TOME_ROAD_AXIS':[258560240,231091547,30968017],
            'CHILE_SIDEWALK_OSM':[1321755864],'TOME_TOWARD_MISERICORDIA':[803899198]}
    result=[]
    for key,ids in routes.items():
        pts=[];refs=[]
        for oid in ids:
            f=by[oid];assert not refs or str(refs[-1])==str(f['node_refs'][0]),'Não ligar gap por proximidade'
            pts.extend(f['blender_xy'][1:] if pts else f['blender_xy']);refs.extend(f['node_refs'][1:] if refs else f['node_refs'])
        bounds=np.array(pts);low=bounds.min(axis=0)-1;high=bounds.max(axis=0)+1
        def crop(ts):return np.all(ts.max(axis=1)[:,:2]>=low,axis=1)&np.all(ts.min(axis=1)[:,:2]<=high,axis=1)
        mask=crop(physical);vmask=crop(visual);report=replay(pts,physical[mask],visual[vmask],names[mask])
        w=(report.get('stop') or {}).get('witness') or report.get('witness')
        if w and 'object_index' in w:w['object']=meta['physics_objects'][w['object_index']]['name']
        print(json.dumps({'route':key,'status':report['status'],'moves':report['moves']}),flush=True)
        result.append({'route':key,'osm_way_ids':ids,'node_controls':refs,'TOPOLOGY_VALID':True,
                       'SURFACE_VALID':'PARTIAL_CANDIDATE' if report['status']=='NUMERIC_SCOPE_PASSED' else False,
                       'PEDESTRIAN_CLEARANCE_VALID':None,'GAMEPLAY_VALID':False,
                       'scope':'Existing ground collider and bound candidate external obstacles; missing complete sidewalk/obstacle roles prevents approval',
                       'capsule':{'radius':R,'height':H,'step':STEP,'skin':SKIN,'gravity':9.81},'support_method':'finite lower-sphere faces and edges with radial skin; no central-ray grounding','replay':report})
    (OUT/'sweeps.json').write_text(json.dumps({'scene_changed':False,'routes':result,'barroquinha':'TOPOLOGY_ONLY_PHYSICAL_CONNECTOR_PENDING'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps([{'route':r['route'],'status':r['replay']['status'],'moves':r['replay']['moves'],'stop':r['replay'].get('stop'),'start_witness':r['replay'].get('witness')} for r in result],ensure_ascii=False))

if __name__=='__main__':main()
