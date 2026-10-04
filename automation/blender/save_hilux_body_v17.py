"""Salva e reabre a revisão real V17, com relatório da malha e cena visível."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v17.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert s.get('boas_v17_joints_finished') and not s.get('boas_v17_final_saved')
o=s.objects['HILUX | CARROCERIA PRINCIPAL']
visible=[ob.name for ob in s.objects if ob.type=='MESH' and ob.visible_get()]
assert visible==[o.name]
assert o.modifiers[0].type=='MIRROR' and o.modifiers[0].use_clip
before=json.loads((r/'artifacts/vehicles/rondesp/v17-mesh-before.json').read_text(encoding='utf-8'))
after=json.loads((r/'artifacts/vehicles/rondesp/v17-mesh-after.json').read_text(encoding='utf-8'))
intersections=json.loads((r/'artifacts/vehicles/rondesp/v17-intersections.json').read_text(encoding='utf-8'))
fields=['multi_edges','inconsistent_winding','tiny_faces','duplicate_faces','wire_edges','coincident_vertices','t_junctions']
assert all(not after[key] for key in fields),'Falha de malha remanescente'
assert intersections['non_adjacent_intersecting_face_pairs']==0,'Penetração entre chapas remanescente'
assert len(o.data.vertices)==after['vertices'] and len(o.data.polygons)==after['faces']
s['boas_v17_final_saved']=True
o['boas_v17_mesh_review']='Malha base revisada: conexões, degenerações, normais e penetração não local; encaixe com conjuntos reservados pendente.'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.color_type='OBJECT';sp.shading.show_cavity=False;sp.shading.show_shadows=False
            sp.region_3d.view_rotation=(Vector((0,.15,1.07))-Vector((7,8,4.8))).to_track_quat('-Z','Y')
            sp.region_3d.view_location=(0,.15,1.07);sp.region_3d.view_distance=5.5
bpy.context.view_layer.update()
s.render.filepath='//../../../../artifacts/vehicles/rondesp/v17-carroceria.png'
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
rp=r/'docs/reports/blender/hilux_carroceria_v17.json';report=json.loads(rp.read_text(encoding='utf-8'))
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
report['visual_review']='reviewed_with_reserved_components_fit_pending'
report['visual_views']=[f'artifacts/vehicles/rondesp/v17-carroceria-{n}.png' for n in
    ['cacamba','encontro-cabine','frente','batente-dianteiro','tampa','arco-traseiro','interior-cacamba','lateral']]
report['remaining']=['Fidelidade interpretada das referências; não representa certificação ou medidas industriais.',
    'Conferir encaixes de portas, vidros e componentes reservados ao restaurar a montagem.',
    'Dobradiças, direção e rodagem ainda adiadas, conforme o escopo atual.']
report['base_vertices']=len(o.data.vertices);report['base_faces']=len(o.data.polygons)
report['visible_meshes']=visible;report['source_reopened']=False
report['mesh_review']={'scope':'Malha base de autoria, sem os conjuntos reservados.',
    'before':{key:len(before[key]) for key in fields},'after':{key:len(after[key]) for key in fields},
    'edge_face_counts_after':after['edge_face_counts'],'intersections':intersections,
    'mesh_before':'artifacts/vehicles/rondesp/v17-mesh-before.json',
    'mesh_after':'artifacts/vehicles/rondesp/v17-mesh-after.json',
    'intersection_report':'artifacts/vehicles/rondesp/v17-intersections.json'}
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out))
    body=bpy.context.scene.objects['HILUX | CARROCERIA PRINCIPAL']
    data=json.loads(rp.read_text(encoding='utf-8'))
    data['source_reopened']=Path(bpy.data.filepath).resolve()==out.resolve()
    data['reopened_observation']={'scene':bpy.context.scene.name,'base_vertices':len(body.data.vertices),
        'base_faces':len(body.data.polygons),'visible_meshes':[ob.name for ob in bpy.context.scene.objects if ob.type=='MESH' and ob.visible_get()],
        'mirror_clipping':body.modifiers[0].use_clip,'objects':len(bpy.context.scene.objects),
        'file_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
    assert data['reopened_observation']['base_faces']==data['base_faces']
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return None
bpy.app.timers.register(reopen,first_interval=.5)
