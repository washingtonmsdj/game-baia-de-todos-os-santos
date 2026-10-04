"""Apresentação da câmera interna com vidro sem ruído de transparência."""
import bpy,json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
rp=r/'docs/reports/blender/rondesp_driver_review_b39.json';report=json.loads(rp.read_text(encoding='utf8'))
material=next(m for m in bpy.data.materials if m.name.startswith('QA B39 | Vidro fino transparente para revisão') and m.users)
options={x.identifier for x in material.bl_rna.properties['surface_render_method'].enum_items}
if 'BLENDED' in options:material.surface_render_method='BLENDED'
bs=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Transmission Weight'].default_value=0.
s.camera.location=(-.43,-.12,1.56)
report['driver_camera']['asset_local_eye']=list(s.camera.location)
report['glazing_override_scope']='Sete chapas de vidro com material local de prévia, alpha 0,045 e transparência BLENDED; geometria e borrachas da biblioteca preservadas. Não é calibração fotométrica industrial nem alteração da V25.'
window=bpy.context.window;area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(reg for reg in area.regions if reg.type=='WINDOW')
for item in report['driver_view_evidence']:
    s.frame_set(item['frame']);bpy.context.view_layer.update()
    with bpy.context.temp_override(window=window,area=area,region=region):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2);bpy.ops.screen.screenshot(filepath=str(r/item['file']))
s.frame_set(report['preview_range']['start'])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
report['source_after']['sha256']=hashlib.sha256((r/report['source_after']['file']).read_bytes()).hexdigest();report['source_reopened']=False
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'hash':report['source_after']['sha256'],'render_method':material.surface_render_method,'eye':list(s.camera.location)}))