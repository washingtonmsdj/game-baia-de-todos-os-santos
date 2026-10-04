"""Separa as normais da chapa e das dobras internas da carroceria V15."""
import bpy,bmesh,json,math
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_carroceria_v15.blend'
assert s.get('boas_v15_a_regularized') and not s.get('boas_v15_sheet_normals_finished')
o=s.objects['HILUX | CARROCERIA PRINCIPAL'];labels=json.loads(o['boas_panel_id_map'])
bm=bmesh.new();bm.from_mesh(o.data);fl=bm.faces.layers.int.get('boas_panel_id')
bm.normal_update();marked=0
fold_ids={int(k) for k,v in labels.items() if v.startswith('HILUX15 |') and
    any(word in v for word in ['Batente','Retorno'])}
for e in bm.edges:
    if len(e.link_faces)!=2:continue
    a,b=e.link_faces;ids={a[fl],b[fl]}
    at_fold=bool(ids.intersection(fold_ids)) and len(ids)==2
    if at_fold or e.calc_face_angle(0)>math.radians(55):
        e.smooth=False;marked+=1
bm.to_mesh(o.data);bm.free();o.data.update()
s['boas_v15_sheet_normals_finished']=True
rp=r/'docs/reports/blender/hilux_carroceria_v15.json';report=json.loads(rp.read_text(encoding='utf-8'))
report['contour_finish']['sheet_fold_sharp_edges']=marked
report['notes'].append('Normais separadas nas dobras internas, preservando o arredondamento geométrico da chapa externa.')
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
