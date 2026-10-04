"""Ajuste localizado do eixo dianteiro para liberar a dobra na saída do batente A."""
import bpy,json
from pathlib import Path
from mathutils import Vector,Matrix
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_portas_v18.blend'
assert s.get('boas_v18_door_returns_finished') and not s.get('boas_v18_front_hinge_finished')
rp=r/'docs/reports/blender/hilux_portas_v18.json';report=json.loads(rp.read_text(encoding='utf8'))
for d in report['door_assemblies']:
 if 'dianteira' not in d['door']:continue
 pivot=s.objects[d['pivot']];side=d['side'];hand='esquerda' if side==-1 else 'direita'
 assert abs(pivot['abertura_graus'])<1e-9
 new=Vector((side*.900,-1.000,.985));delta=pivot.location-new
 for child in pivot.children:
  if child.type in {'MESH','CURVE'}:child.data.transform(Matrix.Translation(delta))
 pivot.location=new;pivot.update_tag(refresh={'OBJECT'})
 for number in [1,2]:
  ob=s.objects[f'HILUX18 | Dobradica fixa dianteira {hand} {number}']
  ob.data.transform(Matrix.Translation(Vector((side*.030,0,0))))
  pin=s.objects[f'HILUX18 | Pino dobradica dianteira {hand} {number}']
  for point in pin.data.splines[0].points:point.co.x=side*.900
 d['hinge_position_candidate_m']=list(new)
s['boas_v18_front_hinge_finished']=True
s.frame_set(s.frame_current);bpy.context.view_layer.update()
report['front_hinge_finish']='Eixo dianteiro ajustado em X para liberar a dobra no batente A, sem deslocar as portas fechadas.'
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
