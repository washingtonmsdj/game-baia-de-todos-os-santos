"""Corrige abertura por geometria e rota pelo desembarque inferior existente."""
import bpy,json,math,hashlib,runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'docs/reports/blender/lacerda-corridor';scene=bpy.context.scene
report=json.loads((out/'scene_b77.json').read_text(encoding='utf8'));qa=json.loads((out/'walkability_candidate_b77.json').read_text(encoding='utf8'));assert all(qa['routes'][k]['status']=='sampled_clear' for k in ('upper','lower'))
scene.frame_set(report['baseline_frame']);report['intermediate_revision']=report['source_after'];report['revision']='R30B.77B'
t=report['timeline'];fps=scene.render.fps/scene.render.fps_base;t['end']=t['walk_out']+math.ceil(qa['routes']['lower']['length_design_units']/1.4*fps)
def curves(action):
    return [c for layer in action.layers for strip in layer.strips for bag in strip.channelbags for c in bag.fcurves]
def center(ob):return sum((ob.matrix_world@Vector(p) for p in ob.bound_box),Vector())/8
for group in report['door_states']:
    a,b=[scene.objects[name] for name in group['objects']];axis=center(b)-center(a);axis.z=0;assert axis.length>.01;axis.normalize()
    upper=group['group'][1] in ('upper',1)
    keys=[(65000,0),(65024,1),(66473,1),(t['departure'],0),(t['end']+24,0)] if upper else [(65000,0),(t['landing'],0),(t['landing']+24,1),(t['end']+24,1)]
    group['keys']=keys
    for ob,sign in ((a,-1),(b,1)):
        # Remover somente canais XY gerados nesta rodada; preservar translação Z.
        for layer in ob.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in list(bag.fcurves):
                        if curve.data_path=='location' and curve.array_index in (0,1):bag.fcurves.remove(curve)
        original=ob.location.copy();projection=[(ob.matrix_world@v.co).dot(axis) for v in ob.data.vertices];distance=max(projection)-min(projection)
        local=ob.parent.matrix_world.inverted().to_3x3()@axis if ob.parent else axis
        for f,amount in keys:
            ob.location=original+local*(sign*distance*amount)
            for i in (0,1):ob.keyframe_insert(data_path='location',index=i,frame=f)
        ob.location=original
nav=scene.objects['B77 | NAV QA | inferior'];spline=nav.data.splines[0]
nav.data.splines.remove(spline);spline=nav.data.splines.new('POLY');spline.points.add(len(qa['routes']['lower']['points'])-1)
for p,xyz in zip(spline.points,qa['routes']['lower']['points']):p.co=(*xyz[:2],xyz[2]+.025,1)
# Derivar o topo da plataforma existente, sem acrescentar piso ao vão.
source=scene.objects['ESTAÇÃO INFERIOR | plataforma'];world=[source.matrix_world@v.co for v in source.data.vertices];top=max(p.z for p in world);faces=[tuple(poly.vertices) for poly in source.data.polygons if all(abs(world[i].z-top)<.00001 for i in poly.vertices)]
assert faces;mesh=bpy.data.meshes.new('B77 | topo plataforma inferior');mesh.from_pydata(world,[],faces);mesh.update()
if any(p.normal.z<0 for p in mesh.polygons):
    import bmesh
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.reverse_faces(bm,faces=[f for f in bm.faces if f.normal.z<0]);bm.to_mesh(mesh);bm.free();mesh.update()
ob=bpy.data.objects.new('B77 | COLLISION | ESTAÇÃO INFERIOR | plataforma',mesh);bpy.data.collections['33.3 RUNTIME | WALKABLE'].objects.link(ob)
ob.hide_render=True;ob.hide_set(True);ob['boas_role']='COLLISION_WALKABLE_CANDIDATE';ob['boas_provenance_ids']=json.dumps(['derived:lacerda-corridor-b77']);ob['boas_geographic_ssot_id']=scene['boas_geographic_ssot_id'];ob['boas_production_ready']=False;ob['boas_derived_from_object']=source.name
report['added_objects'].append(ob.name);report['collision_bindings'].append({'object':ob.name,'source':source.name,'triangles':len(faces)*2,'vertices':len(world),'moving':False})
camera=scene.objects['B77 | QA | personagem'];camera.animation_data_clear()
def camera_route(points,first):
    elapsed=0;previous=None
    for i,p in enumerate(points):
        if i:elapsed+=math.dist(points[i-1],p)/1.4*fps
        f=first+round(elapsed);camera.location=(p[0],p[1],p[2]+1.65);following=points[min(i+4,len(points)-1)];direction=Vector((following[0]-p[0],following[1]-p[1],0))
        if direction.length>.01:
            camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
            if previous is not None:camera.rotation_euler.make_compatible(previous)
            previous=camera.rotation_euler.copy()
        camera.keyframe_insert(data_path='location',frame=f);camera.keyframe_insert(data_path='rotation_euler',frame=f)
camera_route(qa['routes']['upper']['points'],t['start'])
for f,z in ((t['departure'],qa['elevator']['upper_z']),(t['landing'],qa['elevator']['lower_z']),(t['walk_out'],qa['elevator']['lower_z'])):
    p=qa['routes']['upper']['points'][-1];camera.location=(*p[:2],z+1.65);camera.keyframe_insert(data_path='location',frame=f)
camera_route(qa['routes']['lower']['points'],t['walk_out'])
for ob in [camera]+[scene.objects[name] for name in report['animated_existing_objects']]:
    for curve in curves(ob.animation_data.action):
        for key in curve.keyframe_points:key.interpolation='LINEAR'
for marker in scene.timeline_markers:
    if marker.name=='B77 | fim':marker.frame=t['end']
scene.frame_start=t['start'];scene.frame_end=t['end']+24;scene.frame_set(t['start'])
# Usar o relatório atualizado para a checagem real das folhas antes de salvar.
(out/'scene_b77.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(ROOT/'automation/blender/check_corridor_doors_b77.py'))
destination=ROOT/'blender/salvador_lacerda_r30b77b_portas_e_percurso.blend';assert not destination.exists();bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
with destination.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report['source_after']={'file':destination.relative_to(ROOT).as_posix(),'revision':'R30B.77B','sha256':sha};report['door_correction']='Abertura por centros geométricos e projeção dos vértices; lado oposto fechado na busca inferior; topo da plataforma existente tratado como chão.'
(out/'scene_b77.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'saved':report['source_after'],'door_validation':True,'lower_length':qa['routes']['lower']['length_design_units']}))
