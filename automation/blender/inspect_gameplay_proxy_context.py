"""Pré-flight read-only da B81; não altera os gates históricos."""
import bpy, json, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b81_cairu_colisao_e_rota_parcial.blend'
names=['FUNCIONAL | 3 piso','FUNCIONAL | 3 teto','SUPERIOR | piso saguão','INFERIOR | piso do saguão','CALIBRADO | passarela piso 28.71 x 6.00m','INFERIOR | guia de fila.001','INFERIOR | guia de fila','INFERIOR R21 | passeio da entrada']
rows=[]
for ob in scene.objects:
 if ob.name not in names and ob.get('elevator_id')!=3:continue
 pts=[ob.matrix_world@Vector(v) for v in ob.bound_box]
 rows.append({'name':ob.name,'matrix':[list(r) for r in ob.matrix_world], 'dimensions':list(ob.dimensions),'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)],'properties':{k:ob[k] for k in ob.keys() if isinstance(ob[k],(str,float,int,bool))},'collections':[c.name for c in ob.users_collection]})
out=ROOT/'docs/reports/blender/lacerda-gameplay-proxy';out.mkdir(parents=True,exist_ok=True)
report={'file':bpy.data.filepath,'pid':os.getpid(),'dirty':bpy.data.is_dirty,'frame':scene.frame_current,'objects':len(scene.objects),'root_collections':[{'name':c.name,'objects':len(c.all_objects),'hidden':c.hide_viewport} for c in scene.collection.children],'context':rows}
(out/'b81_context.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':bpy.data.filepath,'pid':os.getpid(),'objects':len(scene.objects),'dirty':bpy.data.is_dirty,'context':len(rows)}))
