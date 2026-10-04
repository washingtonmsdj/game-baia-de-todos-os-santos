"""Corrige vidro fino na montagem de revisão, sem editar biblioteca/ferragens."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
rp=r/'docs/reports/blender/rondesp_driver_review_b39.json';report=json.loads(rp.read_text(encoding='utf8'))
assembly=bpy.data.collections['QA | RONDESP | biblioteca montada']
for name in report['glazing_material_review_override']:
    original=next(o for o in bpy.data.objects if o.library is not None and o.name==name)
    for ob in list(assembly.objects):
        if ob.library is None and ob.get('boas_review_override') and ob.name.startswith(name):
            assembly.objects.unlink(ob);bpy.data.objects.remove(ob,do_unlink=True)
    if original.name not in assembly.objects:assembly.objects.link(original)
material=bpy.data.materials.new('QA B39 | Vidro fino transparente para revisão');material.use_nodes=True
material.node_tree.nodes.clear();bs=material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
output=material.node_tree.nodes.new('ShaderNodeOutputMaterial');material.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface'])
bs.inputs['Base Color'].default_value=(.55,.65,.68,1);bs.inputs['Alpha'].default_value=.045
bs.inputs['Transmission Weight'].default_value=.9;bs.inputs['Roughness'].default_value=.015;bs.inputs['IOR'].default_value=1.45
material.diffuse_color=(.55,.65,.68,.045);material.surface_render_method='DITHERED';material.use_transparency_overlap=False
changed=[]
for original in list(assembly.objects):
    name=original.name.casefold()
    actual_glass=('para-brisa envolvente' in name or '| vidro dianteira ' in name or '| vidro traseira ' in name or '| vidro capota traseira' in name or name=='hilux21 | vidro posterior cabine')
    if original.type!='MESH' or not actual_glass:continue
    ob=original.copy();ob.data=original.data.copy();ob.data.materials.clear();ob.data.materials.append(material)
    ob['boas_review_override']='thin_glazing_material_only; original linked geometry preserved'
    assembly.objects.unlink(original);assembly.objects.link(ob);changed.append(original.name)
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_camera_offset=(0,0);area.spaces.active.region_3d.view_camera_zoom=0
            area.spaces.active.region_3d.view_perspective='CAMERA'
report['glazing_material_review_override']=changed
report['glazing_override_scope']='Somente sete chapas de vidro, shader de vidro fino com alpha 0,045; ferragens/borrachas originais restauradas. Material local da montagem QA, fonte V25 não alterada.'
window=bpy.context.window;area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(reg for reg in area.regions if reg.type=='WINDOW')
for item in report['driver_view_evidence']:
    s.frame_set(item['frame']);bpy.context.view_layer.update()
    with bpy.context.temp_override(window=window,area=area,region=region):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=3);bpy.ops.screen.screenshot(filepath=str(r/item['file']))
first=next(p for p in report['route_ranges'] if 'Montanha' in (p['name'] or ''))
s.frame_start=first['start'];s.frame_end=first['end'];s.frame_set(first['start'])
report['preview_range']=first;report['source_reopened']=False
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
report['source_after']['sha256']=hashlib.sha256((r/report['source_after']['file']).read_bytes()).hexdigest()
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source_after':report['source_after'],'glazing':changed,'preview_range':first},ensure_ascii=False))