"""Regulariza a faixa frontal abaixo do encontro com o capô na sessão visível."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_carroceria_v16.blend'
assert s.get('boas_v16_front_aligned') and not s.get('boas_v16_front_band_finished')
o=s.objects['HILUX | CARROCERIA PRINCIPAL'];labels=json.loads(o['boas_panel_id_map'])
old=json.loads((r/'artifacts/vehicles/rondesp/v16-contours-live.json').read_text(encoding='utf-8'))
panel=next(p for p in old if p['name']=='HILUX06 | Para-choque e testa esculpidos')
def front_y(x):return -2.435+.49*(abs(x)/.9275)**3.5
def front_z(x):return 1.137+.10*(abs(x)/.9275)**2.8
old_top={}
for a,b in panel['boundary_edges']:
    if abs(a[0]-b[0])<.00001 or any(p[2]<=front_z(p[0])-.012 for p in (a,b)):continue
    for p in (a,b):old_top[round(p[0],7)]=Vector(p)
old_top=sorted(old_top.values(),key=lambda p:p.x)
def at(points,x):
    for a,b in zip(points,points[1:]):
        if a.x-.00001<=x<=b.x+.00001:return a.lerp(b,max(0,min(1,(x-a.x)/(b.x-a.x))))
    return points[0].copy() if x<0 else points[-1].copy()
bm=bmesh.new();bm.from_mesh(o.data);fl=bm.faces.layers.int.get('boas_panel_id')
hood=next(int(k) for k,v in labels.items() if v=='HILUX06 | Capô e ombros estampados')
front=next(int(k) for k,v in labels.items() if v=='HILUX16 | Chapa frontal alinhada ao capo')
hp=sorted({tuple(v.co):v.co.copy() for f in bm.faces if f[fl]==hood for v in f.verts
    if abs(v.co.y-front_y(v.co.x))<.0015}.values(),key=lambda p:p.x)
assert len(hp)>=37 and len(old_top)>20
vi={v for f in bm.faces if f[fl]==front for v in f.verts};changed=0
for v in vi:
    if any(f[fl]==hood for f in v.link_faces):continue
    a=at(old_top,v.co.x);distance=a.z-v.co.z
    if not -.001<distance<.025:continue
    t=max(0,min(1,distance/.025));weight=1-t*t*(3-2*t)
    delta=at(hp,v.co.x)-a;delta.x=0
    v.co+=delta*weight;changed+=1
bm.normal_update();bm.to_mesh(o.data);bm.free();o.data.update()
s['boas_v16_front_band_finished']=True
rp=r/'docs/reports/blender/hilux_carroceria_v16.json';report=json.loads(rp.read_text(encoding='utf-8'))
report['front_finish']['upper_band_regularized_vertices']=changed
report['notes'].append('Faixa frontal abaixo do capô regularizada para acompanhar a nova borda sem triângulos invertidos.')
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
