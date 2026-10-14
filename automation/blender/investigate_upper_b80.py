"""Comparação explícita B78/B79 e medições locais; nenhuma mutação geométrica."""
import bpy,json,runpy,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-controller-b80';OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene;assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b79_contrato_colisao_slice.blend'
saved=scene.frame_current;scene.frame_set(31978)
helper=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))
b78=json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))
names=[x['object'] for x in b78['changed_meshes']];other=helper['inspect_file'](ROOT/b78['source_after']['file'],names)
comparison=[]
for name in names:
    current=helper['signature'](scene.objects[name]);old=other[name]
    comparison.append({'object':name,'same_geometry':current['geometry_sha256']==old['geometry_sha256'],
        'same_transform':current['transform']==old['transform'],'same_materials':current['materials']==old['materials'],
        'b79_mesh':current['geometry_sha256'],'b78_mesh':old['geometry_sha256'],
        'migration':'NEEDS_REVIEW; no automatic merge; historical bridge width corroborates only overall bridge'})
scene.frame_set(65024);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
measurements=[]
for name in ['SUPERIOR | piso saguão','NAV | passarela superior','LAC R30B | Passarela | piso paginado visual',
 'B77 | COLLISION | NAV | passarela superior','FUNCIONAL | 3 soleira superior','FUNCIONAL | 3 piso',
 'FUNCIONAL | 3 teto','ESTAÇÃO SUPERIOR | plataforma','ESTAÇÃO INFERIOR | cobertura']:
    ob=scene.objects[name];ev=ob.evaluated_get(dg);m=ev.to_mesh()
    try:
        points=[ev.matrix_world@v.co for v in m.vertices]
        measurements.append({'object':name,'bounds':{'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]},
            'mesh_coordinate_extents_not_world_lengths':[max(v.co[i] for v in m.vertices)-min(v.co[i] for v in m.vertices) for i in range(3)],
            'classification':'candidate_scene_measurement_not_real_dimension','properties':{k:ob[k] for k in ob.keys() if isinstance(ob[k],(str,int,float,bool))}})
    finally:ev.to_mesh_clear()
scene.frame_set(saved)
report={'baseline':'R30B.79','compared':'R30B.78','merge_applied':False,'comparison':comparison,'measurements':measurements,
        'B78_scope':'two posterior returns, two lambris, two skirtings and lintel; not cabin/shaft/landing slabs',
        'B79_sweep_relevance':'B78 leaves all 54 contacts and 27 solid witnesses sources unchanged; posterior gap fix cannot certify cabin travel'}
(OUT/'upper_investigation_b80.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'compared_meshes':len(comparison),'measured_sources':len(measurements),'merge_applied':False}))
