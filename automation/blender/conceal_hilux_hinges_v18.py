"""Reposiciona os eixos candidatos sob a chapa e ajusta as folhas das dobradiças."""
import bpy, json
from pathlib import Path
from mathutils import Vector, Matrix
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_portas_v18.blend'
assert s.get('boas_v18_doors_applied') and not s.get('boas_v18_hinges_concealed')
rp=r/'docs/reports/blender/hilux_portas_v18.json';report=json.loads(rp.read_text(encoding='utf8'))
for d in report['door_assemblies']:
 p=s.objects[d['pivot']];side=d['side'];label='dianteira' if 'dianteira' in d['door'] else 'traseira'
 hand='esquerda' if side==-1 else 'direita'
 assert abs(p['abertura_graus'])<1e-9
 old=p.location.copy();new=Vector((side*(.870 if label=='dianteira' else .870),-1.000 if label=='dianteira' else .120,.985))
 delta=old-new
 for child in p.children:
  if child.type in {'MESH','CURVE'}:child.data.transform(Matrix.Translation(delta))
 p.location=new
 hx=abs(new.x);hy=new.y
 for number,z in enumerate([.695,1.135],1):
  for suffix,cx,cy,dy in [('fixa',hx-.017,hy-.018,.047),('movel',hx-.020,hy+.058,.124)]:
   ob=s.objects[f'HILUX18 | Dobradica {suffix} {label} {hand} {number}']
   center=Vector((side*cx,cy,z))-(new if suffix=='movel' else Vector())
   dim=(.025 if suffix=='movel' else .010,dy,.048)
   pattern=[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
   for v,pat in zip(ob.data.vertices,pattern):
    v.co=center+Vector((side*pat[0]*dim[0]/2,pat[1]*dim[1]/2,pat[2]*dim[2]/2))
   ob.data.update()
  pin=s.objects[f'HILUX18 | Pino dobradica {label} {hand} {number}']
  for point,zz in zip(pin.data.splines[0].points,[z-.026,z+.026]):point.co=(side*hx,hy,zz,1)
 d['hinge_position_candidate_m']=list(new)
 p.update_tag(refresh={'OBJECT'})
s.frame_set(s.frame_current);bpy.context.view_layer.update()
s['boas_v18_hinges_concealed']=True
report['hinge_finish']='Eixos recuados sob a chapa fixa, com folhas moveis prolongadas ate a estrutura interna.'
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
