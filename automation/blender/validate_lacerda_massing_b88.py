"""Valida estrutura persistida e apresenta a mesma cena visível em duas vistas."""
import bpy,bmesh,json,os,runpy,math
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-massing-b88'
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b88_estrutura_arquitetonica_plantas.blend'
report=json.loads((out/'application.json').read_text());cfg=json.loads((out/'architectural-controls.json').read_text())
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
checked=[]
for r in report['changes']+report['added']:
    o=bpy.context.scene.objects[r['object']];expected=r.get('after',r)['signature'];assert sig(o)==expected,o.name
    bm=bmesh.new();bm.from_mesh(o.data)
    degenerate=sum(f.calc_area()<1e-9 for f in bm.faces);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
    assert degenerate==0,o.name
    checked.append({'object':o.name,'vertices':len(o.data.vertices),'degenerate_faces':degenerate,'nonmanifold_edges':nonmanifold})
dim=[]
bindings=[('SUPERIOR | piso saguão','upper_floor'),('TORRE | cornija galeria','new_gallery'),('LAC R30B | Passarela | piso paginado visual','bridge'),('INFERIOR | piso do saguão','lower_floor')]
for name,poly in bindings:
    o=bpy.context.scene.objects[name];p=[inv@wm(o)@v.co for v in o.data.vertices];actual=[[min(v[i] for v in p),max(v[i] for v in p)] for i in (0,1)]
    source=cfg['polygons'][poly]['points_local'];expected=[[min(v[i] for v in source),max(v[i] for v in source)] for i in (0,1)]
    residual=max(abs(actual[i][j]-expected[i][j]) for i in (0,1) for j in (0,1));assert residual<.001,(name,residual)
    dim.append({'object':name,'source_polygon':poly,'bounds_xy':actual,'maximum_bound_residual_m':residual})
validation={'revision':'B88','pid':os.getpid(),'file':report['file'],'scene':bpy.context.scene.name,'mesh_checks':checked,'dimension_checks':dim,'dimensions_relative_to_document':True,'independent_geographic_registration':False,'installed_elevator_certified':False,'full_controller_validated':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'production_ready':False}
(out/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
window=next(w for w in bpy.context.window_manager.windows if w.screen)
area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW');space=area.spaces.active
with bpy.context.temp_override(window=window,area=area,region=region):
    if space.local_view:bpy.ops.view3d.localview(frame_selected=False)
    bpy.ops.object.select_all(action='DESELECT')
    names={r['object'] for r in report['changes']+report['added'] if r.get('visible',True)}
    for name in names:
        o=bpy.context.scene.objects[name]
        if o.visible_get():o.select_set(True)
    bpy.context.view_layer.objects.active=bpy.context.scene.objects['TORRE | cornija galeria']
    bpy.ops.view3d.localview(frame_selected=False)
    space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.overlay.show_overlays=False
    target=M@Vector((-27.,2.,45.));eye=M.to_3x3()@Vector((-1.1,-1.7,.7))
    space.region_3d.view_location=target;space.region_3d.view_rotation=eye.to_track_quat('Z','Y');space.region_3d.view_distance=106.;space.region_3d.view_perspective='ORTHO'
    runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b88-structure-isolated.png'})
    # Vista ortogonal de comparação com a planta: mesma cena e mesmas malhas.
    space.region_3d.view_location=M@Vector((-28.,2.,70.));space.region_3d.view_rotation=M.to_quaternion();space.region_3d.view_distance=94.
    runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b88-plan-isolated.png'})
    bpy.ops.view3d.localview(frame_selected=False)
    space.overlay.show_overlays=True;space.region_3d.view_location=target;space.region_3d.view_rotation=eye.to_track_quat('Z','Y');space.region_3d.view_distance=120.
    bpy.ops.object.select_all(action='DESELECT')
    runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b88-structure-in-map.png'})
print(json.dumps({'mesh_objects_checked':len(checked),'dimension_checks':dim,'same_visible_scene':True,'local_view_left_enabled':bool(space.local_view),'production_ready':False},ensure_ascii=False))
