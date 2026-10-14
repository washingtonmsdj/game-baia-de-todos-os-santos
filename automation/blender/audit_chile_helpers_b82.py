"""Exportação read-only do recorte pedonal; não avalia interiores do Lacerda."""
import bpy,json,runpy,sys
import numpy as np
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/world/chile-pedestrian-b82';OUT.mkdir(parents=True,exist_ok=True)
ART=ROOT/'artifacts/chile-pedestrian-b82';ART.mkdir(parents=True,exist_ok=True)
wm=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['world_matrix']
scene=bpy.data.scenes['SALVADOR | ESBOCO OFICIAL']
triage=json.loads((ROOT/'docs/reports/world/centro-structural-triage/triage.json').read_text(encoding='utf8'))['alerts']
alerts=[r for r in triage if r['subarea']=='TOME_RUA_CHILE' and r['category']=='LEGACY_PROXY']
features=json.loads((ROOT/'artifacts/structural-pipeline/centro-lapa-tororo-fontenova/structural_reference.json').read_text(encoding='utf8'))['features']
ways={f['osm_id']:f for f in features if f['osm_type']=='way'}
ids={r['osm_way_id'] for r in alerts}|{30968017,231091547,258560240,803899198,390875490,1321755864}
points=[p for oid in ids for p in ways[oid]['blender_xy']];roi=[min(p[i] for p in points)-3 for i in range(2)]+[max(p[i] for p in points)+3 for i in range(2)]
contract=json.loads((ROOT/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
def triangles(ob):
    me=ob.data;me.calc_loop_triangles();buf=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',buf)
    m=np.array(wm(ob));xyz=buf.reshape(-1,3)@m[:3,:3].T+m[:3,3]
    ids=np.empty(len(me.loop_triangles)*3,np.int32);me.loop_triangles.foreach_get('vertices',ids)
    tri=xyz[ids.reshape(-1,3)];low=tri.min(axis=1);high=tri.max(axis=1)
    mask=(low[:,0]<roi[2])&(high[:,0]>roi[0])&(low[:,1]<roi[3])&(high[:,1]>roi[1])
    return tri[mask]
def tree(tri):return BVHTree.FromPolygons(tri.reshape(-1,3).tolist(),np.arange(len(tri)*3).reshape(-1,3).tolist(),all_triangles=True)
visual=scene.objects[contract['export']['road_object']];collider=scene.objects[contract['export']['terrain_proxy']]
vt=triangles(visual);ct=triangles(collider);vbh,cbh=tree(vt),tree(ct)
def hit(bvh,p):
    v,n,k,d=bvh.ray_cast(Vector((p[0],p[1],120)),Vector((0,0,-1)),200)
    return {'z':float(v.z),'normal_z':float(n.z)} if v is not None else None
helpers={int(o['boas_osm_way_id']):o for o in scene.objects if o.name.startswith('R30A7 | ROAD |') and 'boas_osm_way_id' in o}
rows=[]
prior_binding=json.loads((ROOT/'docs/reports/blender/conceicao_binding_r30b38.json').read_text(encoding='utf8'))['binding']
for alert in alerts:
    f=ways[alert['osm_way_id']];mapping={str(n):p for n,p in zip(f['node_refs'],f['blender_xy'])};ob=helpers.get(f['osm_id'])
    checks=[]
    for n in alert['node_ids']:
        p=mapping.get(n);v=hit(vbh,p) if p else None;c=hit(cbh,p) if p else None
        checks.append({'node_id':n,'source_node_present':p is not None,'xy':p,'visual':v,'collider':c,
                       'difference':abs(v['z']-c['z']) if v and c else None})
    node_valid=all(x['visual'] and x['collider'] and x['difference']<=.05 and x['visual']['normal_z']>.65 for x in checks)
    classification='SOURCE_NODE_PRESENT_SURFACE_VALID' if node_valid else 'MISSING_BINDING' if ob is None else 'VALID_PARTIAL_HELPER' if ob.get('boas_partial_source') else 'NEEDS_REVIEW'
    if f['osm_id']==prior_binding['osm_way_id']:classification='NEEDS_REVIEW'
    equivalents=[]
    for other in scene.objects:
        if other.type!='MESH':continue
        binding=other.get('boas_osm_way_id',other.get('osm_way_id',other.get('osm_id')))
        if str(binding)!=str(f['osm_id']):continue
        other_tri=triangles(other)
        if not len(other_tri):continue
        tb=tree(other_tri)
        equivalents.append({'object':other.name,'role':other.get('boas_role'),'reference_only':bool(other.get('boas_reference_only') or other.get('boas_source_reference')),'hide_render':other.hide_render,'collections':[c.name for c in other.users_collection],'node_hits':[hit(tb,mapping[n]) if n in mapping else None for n in alert['node_ids']]})
    rows.append({'issue_id':alert['issue_id'],'osm_way_id':f['osm_id'],'name':f.get('tags',{}).get('name'),
                 'classification':classification,'binding_present':ob is not None,'partial_helper':bool(ob and ob.get('boas_partial_source')),
                 'unresolved_nodes':ob.get('boas_unresolved_nodes') if ob else None,'node_checks':checks,
                 'equivalent_bound_meshes':equivalents,'classification_scope':'node supports only; not clearance, complete segment or permission',
                 'historical_generator':'automation/blender/r30a7_road_graph.py#create_way',
                 'recorded_local_adaptation':prior_binding if f['osm_id']==prior_binding['osm_way_id'] else None,'missing_surface_is_proven_error':False,'scene_change_authorized':False})
# Fonte física externa existente. Não usar internos/congelados, proxies B82 ou referência como obstáculos.
obstacles=[];arrays=[ct];index=[{'name':collider.name,'role':'GROUND','first':0,'count':len(ct)}]
for ob in scene.objects:
    role=ob.get('boas_role','')
    if ob.type!='MESH' or role not in {'COLLISION_STATIC_OBSTACLE_CANDIDATE','static_collider'}:continue
    source=ob.get('boas_derived_from_object') or ob.get('boas_source_object') or ob.get('boas_source_name')
    if not source:continue
    # Exclusão explícita dos gates internos, não retirada de colisão para aprovar rota.
    if any(token in str(source).upper() for token in ('INFERIOR','SUPERIOR','CABINE','TORRE','POÇO','SOLEIRA','GUIA DE FILA','PASSARELA','ELEVADOR')):continue
    tri=triangles(ob)
    if not len(tri):continue
    obstacles.append({'name':ob.name,'source':source,'role':role,'triangles':len(tri)})
    index.append({'name':ob.name,'role':'OBSTACLE_CANDIDATE','first':sum(len(x) for x in arrays),'count':len(tri)});arrays.append(tri)
np.savez_compressed(ART/'physics.npz',visual=vt,physical=np.concatenate(arrays))
metadata={'source':'B82 historical scene read-only','roi':roi,'scene_changed':False,'alerts':rows,'counts':{},
          'physics_objects':index,'obstacles':obstacles,'physical_scope':'Existing contract ground + bound external candidate obstacles; unclassified visual meshes not certified',
          'physics_file':'artifacts/chile-pedestrian-b82/physics.npz','unknown_width_and_direction_block_geometry':False}
from collections import Counter
metadata['counts']=dict(Counter(r['classification'] for r in rows))
(OUT/'helpers.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'alerts':len(rows),'unique_ways':len({r['osm_way_id'] for r in rows}),'counts':metadata['counts'],'bound_external_obstacles':len(obstacles),'scene_changed':False}))
