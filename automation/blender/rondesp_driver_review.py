"""Revisão da rede com a biblioteca real, câmera interna e replays separados."""
import bpy,json,math,hashlib,runpy,numpy as np
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
rp=r/'docs/reports/blender/rondesp_network_audit_b38.json';audit=json.loads(rp.read_text(encoding='utf8'))
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
source=audit['source_before'];assert Path(bpy.data.filepath).resolve()==(r/source['file']).resolve()
out=r/'blender/salvador_lacerda_r30b39_rondesp_percursos.blend';assert not out.exists()
helpers=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'));wm=helpers['world_matrix'];signature=helpers['signature']
protected={o.name:signature(o) for o in s.objects if o.type in {'MESH','CURVE','FONT'} and o.name!=c['export']['terrain_proxy']}
original_frame=s.frame_current
# Static obstacle candidates from visible authored meshes, spatially indexed.
grid=defaultdict(set);boxes={};trees={};cell=24.
excluded=('TESTE','VALIDACAO','GAMEPLAY | carro','SOURCE_GEOREF','REFERENCE','R30A7','R30A6','R30A5')
for ob in s.objects:
    if ob.type!='MESH' or not ob.visible_get() or ob==s.objects[c['export']['road_object']]:continue
    labels=' '.join([ob.name,*[co.name for co in ob.users_collection]])
    if any(x.casefold() in labels.casefold() for x in excluded) or any(x in labels.casefold() for x in ['oceano','ocean','water','baía','terreno dem','céu']):continue
    corners=[wm(ob)@Vector(p) for p in ob.bound_box]
    lo=Vector(tuple(min(p[i] for p in corners) for i in range(3)));hi=Vector(tuple(max(p[i] for p in corners) for i in range(3)))
    boxes[ob.name]=(lo,hi)
    for x in range(math.floor(lo.x/cell),math.floor(hi.x/cell)+1):
        for y in range(math.floor(lo.y/cell),math.floor(hi.y/cell)+1):grid[x,y].add(ob.name)
def obstacle_tree(name):
    if name not in trees:
        ob=s.objects[name];me=ob.data;me.calc_loop_triangles()
        trees[name]=BVHTree.FromPolygons([wm(ob)@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)
    return trees[name]
issues=[];count=0;safe=[];candidate_count=0
for run in audit['poses']:
    accepted=[]
    for pose in run['samples']:
        count+=1;location=Vector(pose['location']);rotation=Quaternion(pose['rotation']);names=set()
        for x in range(math.floor((location.x-4)/cell),math.floor((location.x+4)/cell)+1):
            for y in range(math.floor((location.y-4)/cell),math.floor((location.y+4)/cell)+1):names.update(grid.get((x,y),[]))
        hits=[]
        for name in names:
            lo,hi=boxes[name]
            if lo.z>location.z+2.1 or hi.z<location.z+.35:continue
            if hi.x<location.x-4 or lo.x>location.x+4 or hi.y<location.y-4 or lo.y>location.y+4:continue
            candidate_count+=1;bvh=obstacle_tree(name)
            for z in [.48,1.05,1.65]:
                for x in [-.92,0,.92]:
                    start=location+rotation@Vector((x,-2.85,z));end=location+rotation@Vector((x,2.75,z));d=end-start
                    if bvh.ray_cast(start,d.normalized(),d.length)[0] is not None:hits.append(name);break
                if hits and hits[-1]==name:break
        if hits:issues.append({'edge_id':run['edge_id'],'fraction':pose['fraction'],'objects':sorted(set(hits)),'classification':'NEEDS_REVIEW'})
        else:accepted.append(pose)
    if accepted:safe.append({**run,'samples':accepted,'obstacle_free_full_run':len(accepted)==len(run['samples'])})
(r/'artifacts/roads/rondesp/obstacle_progress.json').write_text(json.dumps({'poses':count,'issues':issues,'safe':len(safe),'mesh_candidates':len(boxes)},ensure_ascii=False),encoding='utf8')
# Library binding stays relative and independent of city geometry.
local=bpy.data.collections.new('QA | RONDESP | percursos e camera B39');s.collection.children.link(local)
local['boas_role']='review_only_exclude_from_runtime_export'
with bpy.data.libraries.load(str(r/audit['vehicle']['file']),link=True) as (available,requested):
    requested.collections=[n for n in available.collections if n not in {'RDP01 | APRESENTACAO','RDP01 | PECAS RESERVADAS','HILUX | PORTAS EM EDICAO'}]
assembly=bpy.data.collections.new('QA | RONDESP | biblioteca montada')
parts={o for co in requested.collections for o in co.all_objects if not o.hide_render and not o.hide_viewport}
for ob in parts:assembly.objects.link(ob)
glass_override=[]
for ob in list(assembly.objects):
    if ob.type!='MESH' or 'vidro' not in ob.name.casefold():continue
    local_glass=ob.copy();local_glass.data=ob.data.copy();assembly.objects.unlink(ob);assembly.objects.link(local_glass)
    for i,mat in enumerate(local_glass.data.materials):
        if mat is None:continue
        clear=mat.copy();clear.name='QA B39 | vidro transparente | '+mat.name
        clear.use_nodes=True;bs=clear.node_tree.nodes.get('Principled BSDF')
        if bs:
            bs.inputs['Base Color'].default_value=(.65,.78,.82,1);bs.inputs['Alpha'].default_value=.08
            bs.inputs['Transmission Weight'].default_value=1.;bs.inputs['Roughness'].default_value=.025;bs.inputs['IOR'].default_value=1.45
        clear.diffuse_color=(.65,.78,.82,.08)
        if hasattr(clear,'surface_render_method'):clear.surface_render_method='DITHERED'
        if hasattr(clear,'use_transparency_overlap'):clear.use_transparency_overlap=False
        local_glass.data.materials[i]=clear
    local_glass['boas_review_override']='thin glazing transparency; linked asset remains unchanged'
    glass_override.append(ob.name)
instance=bpy.data.objects.new('QA | RONDESP | veiculo na pista',None);local.objects.link(instance)
instance.instance_type='COLLECTION';instance.instance_collection=assembly;instance.rotation_mode='QUATERNION'
instance['boas_asset_id']='vehicle-rondesp-pickup';instance['boas_role']='review_vehicle_kinematic';instance['boas_source_file']=audit['vehicle']['file']
for library in bpy.data.libraries:
    if Path(bpy.path.abspath(library.filepath)).resolve()==(r/audit['vehicle']['file']).resolve():library.filepath=bpy.path.relpath(str(r/audit['vehicle']['file']),start=str(out.parent))
camera=bpy.data.objects.new('QA | RONDESP | camera motorista',bpy.data.cameras.new('QA | RONDESP | camera motorista'))
local.objects.link(camera);camera.parent=instance;camera.location=(-.43,-.02,1.46)
camera.rotation_euler=Vector((0,-1,-.035)).to_track_quat('-Z','Y').to_euler();camera.data.lens=24;camera.data.clip_start=.06;camera.data.clip_end=3000
camera['boas_eye_position_status']='candidate; posição aproximada sobre assento esquerdo, não medida antropométrica';s.camera=camera
# Independent route ranges: no unsupported gap is silently crossed.
runs=[];frame=241;s.render.fps=24
for run in safe:
    if not run['full_segment_clear'] or not run['obstacle_free_full_run']:continue
    pp=run['samples']
    if run['direction']=='reverse':
        pp=[{**p,'rotation':list(Quaternion(p['rotation'])@Quaternion((0,0,1),math.pi))} for p in reversed(pp)]
    start=frame;prior=None
    for p in pp:
        if prior is not None:frame+=max(1,round(math.dist(p['location'],prior)*24/4))
        instance.location=p['location'];instance.rotation_quaternion=p['rotation']
        instance.keyframe_insert(data_path='location',frame=frame);instance.keyframe_insert(data_path='rotation_quaternion',frame=frame);prior=p['location']
    runs.append({'edge_id':run['edge_id'],'name':pp[0].get('name'),'start':start,'end':frame,'direction':run['direction'],'status':'geometry_only_not_dynamic_physics'})
    s.timeline_markers.new(run['edge_id'],frame=start);frame+=24
if not runs:raise RuntimeError('Nenhum segmento apto para replay geométrico')
action=instance.animation_data.action
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for f in bag.fcurves:
                for key in f.keyframe_points:key.interpolation='LINEAR'
                # Holding the endpoint over the gap avoids interpolation to another street.
                for run in runs:
                    key=next((k for k in f.keyframe_points if round(k.co.x)==run['end']),None)
                    if key:key.interpolation='CONSTANT'
s.frame_start=241;s.frame_end=frame-24
# Select named street examples for actual viewport evidence.
selected=[];seen=set()
for keyword in ['Montanha','Concei','Chile','Cairu','Carlos Gomes','Castro','Barroquinha']:
    options=[p for p in runs if keyword.casefold() in (p['name'] or '').casefold() and p['name'] not in seen]
    if options:
        p=max(options,key=lambda p:p['end']-p['start']);selected.append(p);seen.add(p['name'])
for p in sorted(runs,key=lambda p:p['end']-p['start'],reverse=True):
    if len(selected)>=8:break
    if p['name'] not in seen:selected.append(p);seen.add(p['name'])
window=bpy.context.window;area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(reg for reg in area.regions if reg.type=='WINDOW')
for a in window.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.shading.type='MATERIAL'
        a.spaces.active.shading.use_scene_lights=False;a.spaces.active.shading.use_scene_world=False
        a.spaces.active.shading.studiolight_rotate_z=.5
shots=[]
for index,p in enumerate(selected):
    s.frame_set(round((p['start']+p['end'])/2));bpy.context.view_layer.update()
    path=r/f'artifacts/roads/rondesp/driver-{index:02}.png'
    with bpy.context.temp_override(window=window,area=area,region=region):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2);bpy.ops.screen.screenshot(filepath=str(path))
    shots.append({'file':path.relative_to(r).as_posix(),'name':p['name'],'edge_id':p['edge_id'],'frame':s.frame_current})
preferred=next((p for p in selected if 'Montanha' in (p['name'] or '')),selected[0]);s.frame_set(preferred['start'])
s.frame_set(original_frame);bpy.context.view_layer.update()
differences=[n for n,h in protected.items() if signature(s.objects[n])!=h]
(r/'artifacts/roads/rondesp/preservation_differences.json').write_text(json.dumps(differences,ensure_ascii=False),encoding='utf8')
assert not differences,'Componente externo ao colisor foi alterado: '+str(differences[:8])
s.frame_set(preferred['start']);bpy.context.view_layer.update()
refinement=json.loads((r/'artifacts/roads/rondesp/collision_refinement.json').read_text(encoding='utf8'))
report={'source_before':source,'vehicle':audit['vehicle'],'classification':'ERROR','collision_refinement':refinement,
        'world_visual_components_preserved':len(protected),'source_network_audit':rp.relative_to(r).as_posix(),
        'obstacle_checks':{'poses':count,'mesh_candidates':len(boxes),'nearby_checks':candidate_count,'issue_poses':len(issues),'issues':issues,
                           'scope':'Nove raios longitudinais no envelope candidato; malhas base visíveis. Não cobre interiores sólidos, modificadores, toda colisão ou física.'},
        'driver_camera':{'object':camera.name,'asset_local_eye':list(camera.location),'lens_mm':24,'status':'candidate'},
        'glazing_material_review_override':glass_override,'route_ranges':runs,'driver_view_evidence':shots,'approved':False,'dynamic_physics_tested':False,'runtime_exported':False,
        'inter_segment_turns_validated':False,'reverse_direction_on_bidirectional_roads_validated':False,
        'unsupported_policy':'Trechos independentes; saltos entre ruas são cortes de revisão, não conexões dirigíveis.',
        'pending':['Curvas entre segmentos e sentidos inversos de vias duplas','Trechos sem binding/pavimento/apoio','Diferenças grandes piso/colisor','Varredura volumétrica contínua e física','Inspeção visual das capturas internas']}
s['boas_review_status']='candidate; auditoria parcial, não AAA ou circuito completo aprovado';s['boas_revision_parent']=source['file']
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['source_after']={'file':out.relative_to(r).as_posix(),'revision':'R30B.39','sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
report['source_reopened']=False
(r/'docs/reports/blender/rondesp_driver_review_b39.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source_after':report['source_after'],'runs':len(runs),'obstacle_issue_poses':len(issues),'camera':camera.name,'shots':shots},ensure_ascii=False))
