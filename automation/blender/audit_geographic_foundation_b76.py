"""Auditar a sessão visível B75 sem mudar geometria nem instanciar outra janela."""
import bpy,json,sys,runpy,math,hashlib
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
folder=root/'docs/reports/blender/geographic-foundation';folder.mkdir(parents=True,exist_ok=True)
source=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
assert source['revision']=='R30B.75' and Path(bpy.data.filepath).resolve()==(root/source['file']).resolve()
old=sys.argv[:]
try:
    sys.argv=['blender','--','--output',str(folder/'structural_scene_before.json')]
    runpy.run_path(str(root/'tools/blender/audit_structural_scene.py'),run_name='__main__')
finally:sys.argv=old
helpers=runpy.run_path(str(root/'tools/blender/audit_structural_scene.py'))
signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
cols=[{'name':c.name,'objects':len(c.objects),'children':[v.name for v in c.children],'role':c.get('boas_role'),'hidden':c.hide_viewport} for c in scene.collection.children]
all_cols=[{'name':c.name,'objects':len(c.objects),'role':c.get('boas_role')} for c in bpy.data.collections if not c.library]
grounds=[];ground_names=['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B74 | TERRENO | Lapa Tororo Fonte Nova | candidato']
for ob in scene.objects:
    if ob.type=='MESH' and (ob.name in ground_names or ob.name.startswith('B75 | passeio OSM ')):
        points=[ob.matrix_world@v.co for v in ob.data.vertices];polys=[list(p.vertices) for p in ob.data.polygons]
        grounds.append((ob,BVHTree.FromPolygons(points,polys,all_triangles=False)))
def ground(x,y):
    candidates=[]
    for ob,tree in grounds:
        hit=tree.ray_cast(Vector((x,y,500)),Vector((0,0,-1)),1000)
        if hit[0]:candidates.append((hit[0].z,ob.name))
    return max(candidates) if candidates else None
duplicates=defaultdict(list);transforms=[];far=[];building_ground=[];road_ground=[]
for ob in scene.objects:
    matrix=ob.matrix_world;scale=matrix.to_scale();finite=all(math.isfinite(v) for row in matrix for v in row)
    if not finite or min(abs(v) for v in scale)<1e-8 or matrix.determinant()<0 or max(abs(v) for v in scale)-min(abs(v) for v in scale)>.0001:
        transforms.append({'object':ob.name,'type':ob.type,'scale_world':list(scale),'finite':finite,'determinant':matrix.determinant(),'classification':'NEEDS_REVIEW','reason':'Transform não uniforme/refletido/nulo não é erro automaticamente'})
    bb=helpers['world_bounds'](ob)
    if bb and math.hypot((bb['min'][0]+bb['max'][0])/2,(bb['min'][1]+bb['max'][1])/2)>10000:
        far.append({'object':ob.name,'bounds':bb,'classification':'NEEDS_REVIEW','review_radius_design_units':10000})
    if ob.type=='MESH':
        duplicates[(ob.data.as_pointer(),tuple(round(v,7) for row in matrix for v in row))].append(ob)
    ids=helpers['osm_ids'](ob)
    if helpers['is_reference_object'](ob) or not ids:continue
    category=helpers['classify'](ob)
    if ob.type=='MESH' and 'buildings' in category and bb:
        samples=[]
        for x,y in [((bb['min'][0]+bb['max'][0])/2,(bb['min'][1]+bb['max'][1])/2),*[(bb[k][0],bb[j][1]) for k in ('min','max') for j in ('min','max')]]:
            hit=ground(x,y)
            if hit:samples.append({'xy':[x,y],'ground_z':hit[0],'ground_object':hit[1],'above_building_bottom':hit[0]-bb['min'][2],'above_roof':hit[0]-bb['max'][2]})
        if samples and (max(s['above_roof'] for s in samples)>.05 or min(s['above_building_bottom'] for s in samples)<-.5):
            building_ground.append({'object':ob.name,'osm_ids':ids,'samples':samples,'classification':'NEEDS_REVIEW','method':'AABB/cantos/centro; triagem, não interseção volumétrica'})
    if ob.type=='CURVE' and (ob.name.startswith('R30A7 | ROAD |') or ob.name.startswith('R30A7 | SIDEWALK |')):
        for sp in ob.data.splines:
            points=list(sp.points)
            for point in points[::max(1,len(points)//12)]:
                p=matrix@Vector(point.co[:3]);hit=ground(p.x,p.y)
                if not hit or abs(p.z-hit[0])>.75:
                    road_ground.append({'object':ob.name,'osm_ids':ids,'xyz':list(p),'ground_z':hit[0] if hit else None,'delta_z':p.z-hit[0] if hit else None,'classification':'NEEDS_REVIEW','helper_not_pavement':True})
groups=[{'objects':[o.name for o in objects],'collections':[[c.name for c in o.users_collection] for o in objects], 'classification':'NEEDS_REVIEW','shared_mesh_same_matrix':True} for objects in duplicates.values() if len(objects)>1]
report={'source':source,'scene_units':{'system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length},'scene_object_count':len(scene.objects),'root_collections':cols,'all_collections':all_cols,'ground_objects':[ob.name for ob,_ in grounds],'transforms_review':transforms,'far_origin_review':far,'shared_mesh_duplicates_review':groups,'building_ground_review':building_ground,'road_helper_ground_review':road_ground,'scope':'Cena atual; triagem de malha base e BVH. Sem física/navmesh/interseção volumétrica exaustiva. Sem matching por nomes.', 'geometry_changed':False,'production_ready':False}
(folder/'foundation_before.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
artifact=root/'artifacts/geographic-foundation';artifact.mkdir(parents=True,exist_ok=True)
# Snapshot de conservação de TODOS os componentes: dados, transforms, hierarquia
# e configuração de constraints; propriedades de classificação serão editadas à parte.
protected={}
for ob in scene.objects:
    try:sig=signature(ob)
    except RuntimeError:
        sig={'type':ob.type,'transform':[list(row) for row in ob.matrix_world],'data_name':ob.data.name if ob.data else None,'constraints':[(c.name,c.type) for c in ob.constraints]}
    protected[ob.name]={'signature':sig,'parent':ob.parent.name if ob.parent else None,'collections':[c.name for c in ob.users_collection]}
(artifact/'b76_protected.json').write_text(json.dumps(protected,ensure_ascii=False),encoding='utf8')
print(json.dumps({'source':source['file'],'objects':len(scene.objects),'collections':cols,'transforms_review':len(transforms),'far_origin_review':len(far),'shared_mesh_duplicate_groups':len(groups),'building_ground_review':len(building_ground),'road_helper_ground_review':len(road_ground)},ensure_ascii=False))
