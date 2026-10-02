"""Conferência localizada da revisão salva; não modifica a cena."""
import bpy,json,runpy,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
path=root/'docs/reports/blender/palacio_rio_branco_r30b34.json'
r=json.loads(path.read_text(encoding='utf8'))
helpers=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))
signature=helpers['signature']
file=root/r['source_after']['file']
with file.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
assert Path(bpy.data.filepath).resolve()==file.resolve()
assert digest==r['source_after']['sha256'],'Relatório e arquivo salvo divergem'
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert proof['sha256']==digest and proof['load_post_completed'],'Reabertura não confirmada'
terrain_names=[g['object'] for g in r['retaining_profile_refinement']['geometry']]
changed=[n for n,sig in r['protected_signatures'].items() if n not in terrain_names and signature(scene.objects[n])!=sig]
assert not changed,'Alteração fora do escopo: '+str(changed)
assert all(signature(scene.objects[g['object']])==g['after'] for g in r['retaining_profile_refinement']['geometry'])
slabs=[]
for s in r['galleries']['support_slabs']:
    tops={k:max((scene.objects[s[k]].matrix_world@v.co).z for v in scene.objects[s[k]].data.vertices) for k in ('visual','collider')}
    assert all(abs(z-s['top_from_previous_ground_m'])<.00002 for z in tops.values())
    slabs.append({'visual':s['visual'],'top_levels_m':tops,'previous_ground_m':s['top_from_previous_ground_m']})
body=scene.objects[r['palace']['object']]
base=min((body.matrix_world@v.co).z for v in body.data.vertices)
assert abs(base-r['palace']['base_z_preserved_m'])<.00002

before={table:set(getattr(bpy.data,table)) for table in ('objects','meshes','curves','materials')}
try:
    with bpy.data.libraries.load(str(root/r['retaining_profile_refinement']['backup']),link=False) as (available,requested):
        requested.objects=list(terrain_names)
    old_source,old_proxy=requested.objects
    source=scene.objects[terrain_names[0]];proxy=scene.objects[terrain_names[1]]
    road_indices={i for i,m in enumerate(old_source.data.materials) if any(k in m.name.lower() for k in ('asfalto','pedonal','percurso','passeio','calçada','calcada','chile'))}
    def coordinates(o,indices):
        ids={i for p in o.data.polygons if p.material_index in indices for i in p.vertices}
        return {tuple(round(c,5) for c in o.data.vertices[i].co) for i in ids}
    old_road=coordinates(old_source,road_indices);new_road=coordinates(source,road_indices)
    absent=old_road-new_road
    assert not absent,'Vértices de circulação anterior ausentes: '+str(len(absent))
    # Consulta só a vizinhança das galerias para conferir o proxy contra a
    # classificação dos materiais anterior à retopologia.
    segments=r['galleries']['segments']
    def local(w):
        for s in segments:
            d=w-Vector(s['origin_world']);x=d.dot(Vector(s['along_world']));y=d.dot(Vector(s['outward_world']))
            if -.2<x<s['length_from_existing_controls_m']+.2 and -1.4<y<20.2 and w.z>s['origin_world'][2]-1:return True
        return False
    old_source.data.calc_loop_triangles()
    vertices=[old_source.matrix_world@v.co for v in old_source.data.vertices]
    selected=[];materials=[]
    for t in old_source.data.loop_triangles:
        center=sum((vertices[i] for i in t.vertices),Vector())/3
        if local(center):selected.append(list(t.vertices));materials.append(old_source.data.polygons[t.polygon_index].material_index)
    bvh=BVHTree.FromPolygons(vertices,selected,all_triangles=True)
    current={}
    for v in proxy.data.vertices:
        w=proxy.matrix_world@v.co
        if local(w):current.setdefault((round(w.x,4),round(w.y,4)),[]).append(w.z)
    checked=0;issues=[]
    for v in old_proxy.data.vertices:
        w=old_proxy.matrix_world@v.co
        if not local(w):continue
        hit=bvh.ray_cast(Vector((w.x,w.y,150)),Vector((0,0,-1)),250)
        if hit[0] is None or materials[hit[2]] not in road_indices:continue
        checked+=1;zs=current.get((round(w.x,4),round(w.y,4)),[])
        error=min((abs(z-w.z) for z in zs),default=999)
        if error>.001:issues.append({'world_before':list(w),'error_m':error})
    assert not issues,'Proxy de circulação local mudou: '+str(issues[:3])
    road_review={'source_material_indices':sorted(road_indices),'source_road_vertices_preserved':len(old_road),'missing_vertices':len(absent),'proxy_local_road_vertices_checked':checked,'proxy_local_issues':issues,'scope':'Conferência de malha local; não teste de direção/tráfego nem aprovação de runtime.'}
finally:
    for o in set(bpy.data.objects)-before['objects']:
        if not o.users_scene:bpy.data.objects.remove(o,do_unlink=True)
    for table in ('meshes','curves','materials'):
        data=getattr(bpy.data,table)
        for item in set(data)-before[table]:
            if item.users==0:data.remove(item)

images=['artifacts/palacio-rio-branco/r30b34_'+s+'.png' for s in ('frente','lateral','galeria_palacio','galeria_prefeitura')]
assert all((root/p).is_file() for p in images)
r['visual_review']={'status':'reviewed_modeling_candidate','source_sha256':digest,'views':images,'method':'Renders CPU na janela MCP e comparação com as nove capturas locais; sem revisão de gameplay.','limits':'Estatuária/águias e interior não produzidos; implantação da colunata branca da encosta pendente. Alturas/profundidades proporcionais às fotos. Lateral anterior à última correção de material das galerias.'}
r['retaining_profile_refinement']['visual_review']='reviewed_local_modeling_candidate'
r['localized_scene_review']={'file_reopened':proof,'protected_components_unchanged':len(r['protected_signatures'])-len(terrain_names),'terrain_profile_matches_saved_report':True,'palace_base_m':base,'support_slabs':slabs,'road_mesh_review':road_review,'project_tests_or_runtime_export':False}
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'reopened':True,'protected_components':len(r['protected_signatures'])-len(terrain_names),'road_mesh_review':road_review,'support_slabs':len(slabs),'source_sha256':digest},ensure_ascii=False))
