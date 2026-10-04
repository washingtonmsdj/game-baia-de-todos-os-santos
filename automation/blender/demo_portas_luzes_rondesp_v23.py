"""Demonstração visível, reversível, de portas e iluminação na janela MCP existente."""
import bpy, json, hashlib, struct, math, os
from pathlib import Path
from mathutils import Vector

r = Path(__file__).resolve().parents[2]
s = bpy.context.scene
root = s.objects['RDP01_ROOT | viatura']
parent = r/'blender/assets/vehicles/rondesp-pickup/marrom_v22_luzes.blend'
out = r/'blender/assets/vehicles/rondesp-pickup/marrom_v23_demonstracao.blend'
rp = r/'docs/reports/blender/rondesp_demonstracao_v23.json'
assert not bpy.app.background and Path(bpy.data.filepath).resolve() == parent.resolve()
assert not out.exists() and not bpy.app.is_job_running('RENDER')
v22 = json.loads((r/'docs/reports/blender/rondesp_marrom_v22.json').read_text(encoding='utf8'))

def fingerprint(ob):
    h = hashlib.sha256()
    for v in ob.data.vertices: h.update(struct.pack('<3d', *v.co))
    for p in ob.data.polygons:
        h.update(struct.pack('<I', len(p.vertices)))
        h.update(struct.pack('<'+'I'*len(p.vertices), *p.vertices))
    return h.hexdigest()

assert all(fingerprint(s.objects[n]) == h for n,h in v22['protected_mesh_hashes'].items())
window = next(w for w in bpy.context.window_manager.windows if any(a.type == 'VIEW_3D' for a in w.screen.areas))
area = next(a for a in window.screen.areas if a.type == 'VIEW_3D')
region = next(x for x in area.regions if x.type == 'WINDOW')
if window.screen.is_animation_playing:
    with bpy.context.temp_override(window=window, area=area, region=region): bpy.ops.screen.animation_cancel(restore_frame=False)

before_path = r/'artifacts/vehicles/rondesp/v23-demo-before.json'
before = json.loads(before_path.read_text(encoding='utf8'))
report = {'asset_id':'vehicle-rondesp-pickup','status':'candidate','parent':parent.relative_to(r).as_posix(),
          'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),
          'protected_mesh_hashes':v22['protected_mesh_hashes'],'geometry_unchanged':True,
          'source_reopened':False,'runtime_exported':False,'timeline':[1,240],'fps':24,
          'diagnosis':{'doors_had_no_timeline_animation':True,'material_preview_without_compositor':True,
                       'studio_lights_before':before['studio_lights'],'autoexec_fail':before['autoexec_fail']},
          'preview_changes':{},'checks':[]}
root['demonstracao_ativa'] = 1.0
root.id_properties_ui('demonstracao_ativa').update(min=0.,max=1.,description='1: demonstração automática de portas/freio; 0: controles manuais originais.')
keys = {'demo_portas_dianteiras':[(1,0),(20,0),(65,65),(115,65),(160,0),(240,0)],
        'demo_portas_traseiras':[(1,0),(28,0),(73,65),(123,65),(168,0),(240,0)],
        'demo_freio':[(1,0),(45,1),(80,0),(155,1),(190,0),(240,0)]}
for key,poses in keys.items():
    root[key] = 0.0
    root.id_properties_ui(key).update(min=0.,max=1. if key=='demo_freio' else 70.,description='Canal da demonstração na timeline.')
    for frame,value in poses:
        root[key] = float(value)
        root.keyframe_insert(data_path='["'+key+'"]',frame=frame,group='Demonstracao portas e freio')

def action_curves(ob):
    action = ob.animation_data.action
    curves = list(getattr(action,'fcurves',[]))
    if not curves and hasattr(action,'layers'):
        slot = ob.animation_data.action_slot
        for layer in action.layers:
            for strip in layer.strips:
                bag = strip.channelbag(slot)
                if bag: curves.extend(bag.fcurves)
    return curves

curves = action_curves(root)
assert len([f for f in curves if f.data_path.startswith('["demo_')]) == 3
for f in curves:
    if f.data_path.startswith('["demo_'):
        for point in f.keyframe_points:
            point.interpolation = 'CONSTANT' if f.data_path == '["demo_freio"]' else 'BEZIER'
            point.handle_left_type = point.handle_right_type = 'AUTO_CLAMPED'
root.animation_data.action.name = 'HILUX23 | Demonstracao portas e freio'

def variable(driver,symbol,obj,key):
    v = driver.variables.get(symbol) or driver.variables.new()
    v.name = symbol; v.type = 'SINGLE_PROP'
    v.targets[0].id = obj; v.targets[0].data_path = '["'+key+'"]'

doors = [o for o in s.objects if 'abertura_graus' in o]
assert len(doors) == 4
for pivot in doors:
    f = next(f for f in pivot.animation_data.drivers if f.data_path=='rotation_euler')
    original_sign = -1 if f.driver.expression.startswith('-1*') else 1
    variable(f.driver,'demo',root,'demonstracao_ativa')
    channel = 'demo_portas_dianteiras' if 'dianteira' in pivot.name else 'demo_portas_traseiras'
    variable(f.driver,'ang',root,channel)
    f.driver.expression = f'{original_sign}*min(70,max(0,graus*(1-demo)+ang*demo))*0.017453292519943295'

# Pisca mais lento para continuar legível quando a viewport não mantém 24 fps.
phase = {-1:'(((frame-1)*vel)%36<18)', 1:'(((frame-1)*vel)%36>=18)'}
for m in bpy.data.materials:
    if not (m.name.startswith('HILUX22') and m.use_nodes and m.node_tree.animation_data): continue
    for f in m.node_tree.animation_data.drivers:
        if 'AZUL ESQUERDO' in m.name or 'VERMELHO DIREITO' in m.name:
            side = -1 if 'AZUL ESQUERDO' in m.name else 1
            amount = 12 if 'LED ' in m.name else 3
            f.driver.expression = f'liga*(.015+{amount}*{phase[side]})'
        elif m.name in ['HILUX22 | Lanterna e freio vermelhos','HILUX22 | Terceira luz freio']:
            variable(f.driver,'demo',root,'demonstracao_ativa'); variable(f.driver,'auto_freio',root,'demo_freio')
            f.driver.expression = ('.50*pos+' if 'Lanterna e freio' in m.name else '')+'2.4*(freia*(1-demo)+auto_freio*demo)'
        elif m.name=='HILUX22 | Lente farol iluminada': f.driver.expression='.25*aceso'
        m.node_tree.update_tag(); m.update_tag()
for side in [-1,1]:
    ob = s.objects[f'HILUX22 | Reflexo giroflex {side}']
    ob.location.z = 2.055
    ob.data.animation_data.drivers[0].driver.expression = '110*liga*'+phase[side]
    ob.data.update_tag()

studio = bpy.data.collections['RDP01 | APRESENTACAO']
for ob in studio.objects:
    if ob.type == 'LIGHT':
        base = next(x['energy'] for x in before['studio_lights'] if x['name']==ob.name)
        ob.data.energy = base*.15
background = s.world.node_tree.nodes.get('Background')
report['preview_changes']['world_strength_before'] = background.inputs['Strength'].default_value
background.inputs['Strength'].default_value = .035
s.render.engine = 'BLENDER_EEVEE'
if hasattr(s,'eevee'):
    if hasattr(s.eevee,'taa_samples'): s.eevee.taa_samples = 16
    if hasattr(s.eevee,'taa_render_samples'): s.eevee.taa_render_samples = 32
    if hasattr(s.eevee,'use_raytracing'): s.eevee.use_raytracing = False
s.view_settings.exposure = 0.

# Halo óptico da prévia; não adiciona geometria para representar luz.
try:
    if hasattr(s,'use_nodes'): s.use_nodes=True
    tree = getattr(s,'node_tree',None)
    group_tree = False
    if tree is None:
        tree = getattr(s,'compositing_node_group',None)
        if tree is None:
            tree = bpy.data.node_groups.new('HILUX23 | Halo das luzes','CompositorNodeTree')
            tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
            s.compositing_node_group = tree
        group_tree = True
    output = next((n for n in tree.nodes if n.type==('GROUP_OUTPUT' if group_tree else 'COMPOSITE')),None)
    if output is None: output=tree.nodes.new('NodeGroupOutput' if group_tree else 'CompositorNodeComposite')
    oldlink = next((l for l in tree.links if l.to_node == output and l.to_socket == output.inputs['Image']),None)
    source_socket = oldlink.from_socket if oldlink else (tree.nodes.new('CompositorNodeRLayers').outputs['Image'])
    glow = tree.nodes.get('HILUX23 | Brilho visivel') or tree.nodes.new('CompositorNodeGlare')
    glow.name = 'HILUX23 | Brilho visivel'
    if hasattr(glow,'glare_type'): glow.glare_type='FOG_GLOW'
    if hasattr(glow,'quality'): glow.quality='MEDIUM'
    if hasattr(glow,'threshold'): glow.threshold=.8
    if hasattr(glow,'size'): glow.size=8
    if hasattr(glow,'mix'): glow.mix=-.75
    for name,value in [('Type','Fog Glow'),('Threshold',.8),('Strength',.25)]:
        sock=glow.inputs.get(name)
        if sock:
            try: sock.default_value=value
            except (TypeError,ValueError): pass
    if oldlink: tree.links.remove(oldlink)
    tree.links.new(source_socket,glow.inputs['Image']); tree.links.new(glow.outputs['Image'],output.inputs['Image'])
    report['preview_changes']['glow_compositor']=True
except (AttributeError,RuntimeError,KeyError,TypeError) as ex:
    report['preview_changes']['glow_compositor']=False; report['preview_changes']['glow_note']=str(ex)

cam = s.camera
cam.location = (-6.8,-8,4.2)
cam.rotation_euler = (Vector((0,.15,1.05))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=7.6
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type == 'VIEW_3D':
            sp=a.spaces.active; sp.shading.type='RENDERED'
            sp.shading.use_scene_lights=True; sp.shading.use_scene_world=True
            if hasattr(sp.shading,'use_compositor'): sp.shading.use_compositor='ALWAYS'
            sp.overlay.show_overlays=False
            sp.region_3d.view_perspective='CAMERA'; sp.region_3d.view_camera_zoom=0.
        elif a.type == 'PROPERTIES': a.spaces.active.context='OBJECT'

s.name='VIATURA | Rondesp Hilux demonstracao v23'
s.frame_start=1; s.frame_end=240; s.render.fps=24; s.sync_mode='NONE'
for name,frame in [('Portas fechadas',1),('Abrindo quatro portas',28),('Quatro portas abertas',90),('Fechando portas',130),('Portas fechadas novamente',190)]:
    m=s.timeline_markers.get(name) or s.timeline_markers.new(name,frame=frame); m.frame=frame
root['giroflex_ligado']=root['farois_ligados']=root['lanternas_ligadas']=1.
root['giroflex_velocidade']=1.; root['freio']=0.
root.update_tag()
for o in doors: o.update_tag()
for frame in [1,19,60,90,156,190,240]:
    s.frame_set(frame); bpy.context.view_layer.update()
    checks={'frame':frame,'doors':[{'pivot':o.name,'angle_deg':math.degrees(o.rotation_euler.z),'driver_valid':all(f.driver.is_valid for f in o.animation_data.drivers)} for o in doors],
            'blue':bpy.data.materials['HILUX22 | LED AZUL ESQUERDO'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value,
            'red':bpy.data.materials['HILUX22 | LED VERMELHO DIREITO'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value,
            'third_brake':bpy.data.materials['HILUX22 | Terceira luz freio'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value}
    assert all(x['driver_valid'] for x in checks['doors'])
    report['checks'].append(checks)
assert all(abs(x['angle_deg'])<.01 for x in report['checks'][0]['doors'])
assert all(abs(abs(x['angle_deg'])-65)<.01 for x in report['checks'][3]['doors'])
assert all(abs(x['angle_deg'])<.01 for x in report['checks'][-1]['doors'])
assert report['checks'][0]['blue']>10 and report['checks'][0]['red']<.1
assert report['checks'][1]['red']>10 and report['checks'][1]['blue']<.1
assert all(fingerprint(s.objects[n]) == h for n,h in report['protected_mesh_hashes'].items())
s.frame_set(90); bpy.context.view_layer.update()
for o in s.objects: o.select_set(False)
root.select_set(True); bpy.context.view_layer.objects.active=root
s['boas_revision_parent']=parent.relative_to(r).as_posix()
s['boas_authoring_mode']='assembled_demo_review'
notes=bpy.data.texts.get('HILUX23 | COMO VER A DEMONSTRACAO') or bpy.data.texts.new('HILUX23 | COMO VER A DEMONSTRACAO')
notes.clear(); notes.write('Espaço: iniciar/pausar ciclo 1–240. Quatro portas abrem, aguardam e fecham; giroflex azul/vermelho alterna.\nFrame 1: fechadas. Frame 90: todas abertas. Frame 190: fechadas. Freio também alterna.\nPrévia salva em Renderizado, com luz de estúdio reduzida e halo. Numpad 0: câmera.\nRDP01_ROOT | viatura → demonstracao_ativa=0 devolve os controles manuais abertura_graus nos quatro pivôs e freio no root.\nNenhuma chapa foi modificada. Iluminação/animação da autoria Blender; sem integração runtime.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report.update({'file':out.relative_to(r).as_posix(),'scene':s.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'objects':len(s.objects),'live_session':{'pid':os.getpid(),'port':9876},'visual_review':'pending'})
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':str(out),'sha256':report['sha256'],'glow':report['preview_changes'].get('glow_compositor'),'checks':report['checks']},ensure_ascii=False))
