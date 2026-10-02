"""Planeja ligação de gameplay sobre asfalto existente; não altera a referência OSM."""
import bpy, json, runpy, math, numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
source=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['authoring_source']
assert Path(bpy.data.filepath).resolve()==(root/source['file']).resolve()
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
g=json.loads((root/c['staging']['roads']).read_text(encoding='utf8'));nodes={n['id']:n for n in g['nodes']}
way=next(w for w in g['ways'] if w['osm_way_id']==421206045)
xy=np.array(way['blender_xy']);lo=xy.min(axis=0)-8;hi=xy.max(axis=0)+8
terrain=scene.objects[c['export']['road_object']]
def local_tree(o,material=False):
    me=o.data;me.calc_loop_triangles();raw=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',raw)
    M=np.array(wm(o));world=raw.reshape(-1,3)@M[:3,:3].T+M[:3,3]
    raw=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',raw);tri=raw.reshape(-1,3)
    p=world[tri];mask=np.all(p[:,:,:2].max(axis=1)>=lo,axis=1)&np.all(p[:,:,:2].min(axis=1)<=hi,axis=1)
    tids=np.flatnonzero(mask);polys=np.empty(len(me.loop_triangles),dtype=np.int32);me.loop_triangles.foreach_get('polygon_index',polys)
    mats=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',mats)
    local=tri[tids];ids=np.unique(local);mapping=np.full(len(world),-1,dtype=np.int32);mapping[ids]=np.arange(len(ids))
    tree=BVHTree.FromPolygons(world[ids].tolist(),mapping[local].tolist(),all_triangles=True)
    return tree,mats[polys[tids]],tids,world,tri
tree,mats,_,_,_=local_tree(terrain)
proxy=scene.objects[c['export']['terrain_proxy']];ptree,_,_,_,_=local_tree(proxy)
roadslots={i for i,m in enumerate(terrain.data.materials) if m and m.name in c['export']['road_materials']}
def hit(p):
    q,n,idx,_=tree.ray_cast(Vector((p[0],p[1],150)),Vector((0,0,-1)),350)
    if q is None:return None
    return q.z,idx,mats[idx] in roadslots,n.z
def sample(poly,d):
    lengths=np.linalg.norm(np.diff(poly,axis=0),axis=1);cumulative=np.r_[0,np.cumsum(lengths)]
    k=min(len(lengths)-1,max(0,int(np.searchsorted(cumulative,d,side='right')-1)))
    t=np.clip((d-cumulative[k])/lengths[k],0,1)
    return poly[k]*(1-t)+poly[k+1]*t,k,t
length=float(np.linalg.norm(np.diff(xy,axis=0),axis=1).sum());spacing=.75
distances=np.linspace(3,length-3,math.ceil((length-6)/spacing)+1)
stations=[];offsets=np.arange(-3,3.001,.15);missing=[]
vehicle=json.loads((root/'docs/reports/blender/terrain_vehicle_replay_r30b29.json').read_text(encoding='utf8'))
halfbase=vehicle['wheelbase_measured_m']/2;track=.84;halfwidth=vehicle['vehicle_dimensions_measured_m'][0]/2;halflength=vehicle['vehicle_dimensions_measured_m'][1]/2
for index,d in enumerate(distances):
    p,k,t=sample(xy,d);front=sample(xy,min(length,d+2))[0];rear=sample(xy,max(0,d-2))[0]
    forward=(front-rear)/np.linalg.norm(front-rear);side=np.array([-forward[1],forward[0]]);candidates=[]
    for offset in offsets:
        center=p+side*offset;h=hit(center)
        if h is None or not h[2] or h[3]<.65:continue
        for angle in (-20,-10,0,10,20):
            theta=math.radians(angle);f=np.array([forward[0]*math.cos(theta)-forward[1]*math.sin(theta),forward[0]*math.sin(theta)+forward[1]*math.cos(theta)])
            sx=np.array([-f[1],f[0]])
            wheel=[hit(center+f*u+sx*v) for u,v in [(-halfbase,-track),(-halfbase,track),(halfbase,-track),(halfbase,track)]]
            if any(q is None or not q[2] or q[3]<.65 for q in wheel):continue
            zs=[q[0] for q in wheel];back=(zs[0]+zs[1])/2;fr=(zs[2]+zs[3])/2;left=(zs[0]+zs[2])/2;right=(zs[1]+zs[3])/2;mean=sum(zs)/4
            slope=(fr-back)/(2*halfbase);bank=(right-left)/(2*track)
            if abs(slope)>.40 or abs(bank)>.20:continue
            residual=max(abs(z-(mean+u*slope+v*bank)) for z,(u,v) in zip(zs,[(-halfbase,-track),(-halfbase,track),(halfbase,-track),(halfbase,track)]))
            if residual>.12:continue
            body=[hit(center+f*u+sx*v) for u,v in [(-halflength,-halfwidth),(-halflength,halfwidth),(halflength,-halfwidth),(halflength,halfwidth)]]
            if any(q is None or abs(q[0]-(mean+u*slope+v*bank))>.30 for q,(u,v) in zip(body,[(-halflength,-halfwidth),(-halflength,halfwidth),(halflength,-halfwidth),(halflength,halfwidth)])):continue
            candidates.append({'offset':float(offset),'point':[float(center[0]),float(center[1]),mean],'forward':f.tolist(),'heading_adaptation_deg':angle,'grade':slope,'bank':bank,'wheel_residual':residual,'reference_edge_index':k,'reference_fraction':float(t)})
    stations.append({'station':float(d),'reference_xy':p.tolist(),'candidates':candidates})
    if not candidates:missing.append({'station':float(d),'edge_id':f'way-421206045-seg-{k}','reference_xy':p.tolist()})
# DP: proíbe salto de camada; prefere pequena adaptação e mudança lateral contínua.
paths=[];blocks=[];start=0
while start<len(stations):
    if not stations[start]['candidates']:start+=1;continue
    costs=[q['offset']**2*.02 for q in stations[start]['candidates']];links=[];end=start+1
    while end<len(stations) and stations[end]['candidates']:
        previous=stations[end-1]['candidates'];current=stations[end]['candidates'];ds=stations[end]['station']-stations[end-1]['station'];nc=[];parents=[]
        for q in current:
            choices=[]
            for j,p in enumerate(previous):
                delta=math.dist(q['point'][:2],p['point'][:2]);dz=abs(q['point'][2]-p['point'][2]);do=abs(q['offset']-p['offset'])
                if delta>ds*1.65+.05 or dz>ds*.45 or do>.36:continue
                pf,qf=np.array(p['forward']),np.array(q['forward']);heading=math.acos(float(np.clip(pf@qf,-1,1)))
                motion=np.array(q['point'][:2])-np.array(p['point'][:2]);meanforward=pf+qf
                if heading>delta*math.tan(math.radians(35))/(2*halfbase)+.015:continue
                if delta<1e-6 or motion@meanforward/(delta*np.linalg.norm(meanforward))<math.cos(math.radians(15)):continue
                choices.append((costs[j]+q['offset']**2*.02+do*do*5+dz*dz+q['heading_adaptation_deg']**2*.0005,j))
            score,parent=min(choices,default=(float('inf'),-1));nc.append(score);parents.append(parent)
        if not any(math.isfinite(k) for k in nc):break
        links.append(parents);costs=nc;end+=1
    j=min(range(len(costs)),key=lambda k:costs[k]);chosen=[]
    for idx in range(end-1,start-1,-1):
        chosen.append(stations[idx]['candidates'][j])
        if idx>start:j=links[idx-start-1][j]
    chosen.reverse();paths.append({'start_index':start,'end_index':end-1,'points':chosen})
    if end<len(stations):blocks.append({'station':stations[end]['station'],'reason':'missing_support_or_no_continuous_layer_transition'})
    start=end
report={'source':source,'osm_way_id':421206045,'node_refs':way['node_refs'],'direction':way['direction'],'classification':'ADAPT_LOCAL','method':'Ligação do eixo OSM a apoio e envelope do carro existentes no pavimento; referência original preservada. Continuidade vertical/lateral obrigatória; nenhuma largura de rua criada.','reference_georeference_quality':'candidate','source_width_verified_m':None,'search_radius_units':3,'station_spacing_units':spacing,'vehicle_asset_dimensions':vehicle['vehicle_dimensions_measured_m'],'wheelbase_measured_m':2*halfbase,'track_probe_m':2*track,'track_status':'nominal_probe_not_verified','missing':missing,'blocks':blocks,'paths':paths,'scene_changed':False}
out=root/'artifacts/roads/r38';out.mkdir(parents=True,exist_ok=True)
(out/'driveable_plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'stations':len(stations),'missing':len(missing),'runs':[(p['start_index'],p['end_index']) for p in paths],'blocks':len(blocks)},ensure_ascii=False))
