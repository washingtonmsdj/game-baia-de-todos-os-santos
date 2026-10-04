"""Uniformiza o plano da coluna A, sem deslocar os encontros já soldados."""
import ast,bpy,bmesh,json,math
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_carroceria_v15.blend'
assert s.get('boas_v15_contours_finished') and not s.get('boas_v15_a_regularized')
o=s.objects['HILUX | CARROCERIA PRINCIPAL'];labels=json.loads(o['boas_panel_id_map'])
for file,names in [('rebuild_hilux_reference_v06.py',{'interp','sidewidth'}),
    ('rebuild_hilux_cab_v15.py',{'smooth','roof_width','roof_edge_z','cab_side','radius','rear_y','cab_x'}),
    ('finish_hilux_cab_v15.py',{'regular_x'})]:
    for fn in ast.parse((r/'automation/blender'/file).read_text(encoding='utf-8')).body:
        if isinstance(fn,ast.FunctionDef) and fn.name in names:
            exec(compile(ast.Module(body=[fn],type_ignores=[]),file,'exec'),globals())
cage=next(int(k) for k,v in labels.items() if 'Armacão lateral' in v)
jamb=next(int(k) for k,v in labels.items() if 'Batente dianteiro ligado' in v)
bm=bmesh.new();bm.from_mesh(o.data);fl=bm.faces.layers.int.get('boas_panel_id')
changed=0
for v in bm.verts:
    y,z=v.co.y,v.co.z
    if not 1.331<z<roof_edge_z(y)-.017 or y>-.16:continue
    ids={f[fl] for f in v.link_faces}
    if not ids.intersection({cage,jamb}) or ids-{cage,jamb}:continue
    fy=-.970+.632*(z-1.326)/.442
    fx=.803-.092*(z-1.326)/.442
    w=1-smooth((y-fy-.14)/.15)
    old=regular_x(y,z);new=old*(1-w)+fx*w
    if cage in ids:v.co.x=new
    else:v.co.x+=new-old
    changed+=1
bm.normal_update();bm.to_mesh(o.data);bm.free();o.data.update()
s['boas_v15_a_regularized']=True
rp=r/'docs/reports/blender/hilux_carroceria_v15.json';report=json.loads(rp.read_text(encoding='utf-8'))
report['contour_finish']['a_plane_regularized_vertices']=changed
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
