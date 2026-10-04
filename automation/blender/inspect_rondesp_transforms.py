import bpy,json
from pathlib import Path
scene=bpy.context.scene
assert scene.name=='VIATURA | Rondesp picape marrom v01'
prefixes=['Pneu ','Eixo giro roda','Aro borda','Cubo roda','Bloco banda pneu','Porta dianteira','Caixilho porta dianteira','Vidro porta dianteira','Pivô porta']
objects=[]
for prefix in prefixes:
    ob=next(o for o in scene.objects if o.name.startswith('RDP01 | '+prefix))
    objects.append({'name':ob.name,'parent':ob.parent.name if ob.parent else None,'location':list(ob.location),'basis':[list(r) for r in ob.matrix_basis],'inverse':[list(r) for r in ob.matrix_parent_inverse],'world':[list(r) for r in ob.matrix_world]})
repo=Path(__file__).resolve().parents[2]
(repo/'artifacts/vehicles').mkdir(parents=True,exist_ok=True)
(repo/'artifacts/vehicles/rondesp-transforms.json').write_text(json.dumps({'file':bpy.data.filepath,'objects':objects},ensure_ascii=False,indent=2),encoding='utf-8')
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D': a.spaces.active.shading.type='SOLID'
