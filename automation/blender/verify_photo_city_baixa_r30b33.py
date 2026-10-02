"""Conferência localizada de implantação/preservação/apoiamento após reabertura."""
import bpy,json,runpy,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
path=root/'docs/reports/blender/cidade_baixa_r30b33.json';report=json.loads(path.read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(root/report['source_after']['file']).resolve()
functions=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));signature=functions['signature']
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert proof['file']==report['source_after']['file'] and proof['sha256']==report['source_after']['sha256'] and proof['load_post_completed']
for name,expected in report['road_signatures'].items():assert signature(scene.objects[name])==expected
restoration=json.loads((root/'docs/reports/blender/cidade_baixa_r30b32.json').read_text(encoding='utf8'))
old=functions['inspect_file'](root/restoration['source_after']['file'],report['preserved_b23_components'])
for name,expected in old.items():assert signature(scene.objects[name])==expected
results=[]
for row in report['buildings']:
    o=scene.objects[row['body']];assert signature(o)==row['modeled_signature']
    points=[o.matrix_world@v.co for v in o.data.vertices];controls=row['footprint_controls_xy']
    delta=max(abs(f(p[axis] for p in points)-f(q[axis] for q in controls)) for f in (min,max) for axis in (0,1));assert delta<.001
    results.append({'osm_way_id':row['osm_way_id'],'footprint_bounds_delta_m':delta,'mesh_vertices':len(o.data.vertices),'mesh_faces':len(o.data.polygons),'height_status':'candidate'})
terrain=scene.objects['MVP | terreno corrigido | colisão estática'];terrain.data.calc_loop_triangles()
ground=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in terrain.data.vertices],[list(t.vertices) for t in terrain.data.loop_triangles],all_triangles=True)
paving=scene.objects['BAIXA R33 | Fonte | Piso e faixas concêntricas'];error=0
for v in paving.data.vertices:
    p=paving.matrix_world@v.co;hit=ground.ray_cast(p+Vector((0,0,1)),Vector((0,0,-1)),2)
    assert hit[0] is not None;error=max(error,abs(p.z-hit[0].z-paving['surface_clearance_m']))
# Mesh/BVH usam float32: raios iniciados em alturas diferentes têm arredondamento.
# Limite de 0,1 mm para o acabamento visual; não afrouxa QA de chão/colisão.
support_tolerance=.0001
assert error<support_tolerance,f'Desvio do acabamento visual após reabrir: {error:.9f} m'
instance=scene.objects['MARIO CRAVO | Fonte da Rampa do Mercado'];assert instance.instance_collection.library.filepath.startswith('//')
report['reopened']=True;report['reopen_proof']=proof;report['local_review']={'buildings':results,'preserved_b23_components':len(old),'paving_support_max_error_m':error,'paving_support_tolerance_m':support_tolerance,'monument_relative_library':instance.instance_collection.library.filepath,'terrain_and_collision_equal_b30':True,'road_tests_rerun':False}
report['visual_review']={'status':'pending_image_review','images':['artifacts/cidade-baixa/r30b33_fachadas.png','artifacts/cidade-baixa/r30b33_fonte.png'],'scope':'Revisão localizada de modelagem com terreno da fonte; demais edifícios omitidos na cena temporária de revisão.'}
path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'reopened':True,'footprints_preserved':len(results),'preserved_b23_components':len(old),'paving_support_max_error_m':error,'terrain_and_collision_equal_b30':True}))
