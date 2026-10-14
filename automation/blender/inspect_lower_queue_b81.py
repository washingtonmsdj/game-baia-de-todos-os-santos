"""Audita somente guia de fila/acesso inferior; sem modificar ou salvar cena."""
import bpy,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/research/lower-lobby-connector';OUT.mkdir(parents=True,exist_ok=True)
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b81_cairu_colisao_e_rota_parcial.blend'
objects=[]
for ob in bpy.context.scene.objects:
 if ob.name not in ['INFERIOR | guia de fila','INFERIOR | guia de fila.001','INFERIOR | piso do saguão','B81 | NAV | Cairu OSM parcial bloqueada']:continue
 mats=[]
 for m in getattr(ob.data,'materials',[]):
  if m is not None:mats.append({'name':m.name,'diffuse':list(m.diffuse_color),'metallic':m.metallic,'roughness':m.roughness})
 objects.append({'object':ob.name,'type':ob.type,'location':list(ob.location),'rotation':list(ob.rotation_euler),'scale':list(ob.scale),'dimensions':list(ob.dimensions),'matrix_world':[list(r) for r in ob.matrix_world],'collections':[c.name for c in ob.users_collection],'properties':{k:ob[k] for k in ob.keys() if isinstance(ob[k],(str,float,int,bool))},'materials':mats,'mesh':{'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons)} if ob.type=='MESH' else None,'parent':ob.parent.name if ob.parent else None,'modifiers':[(m.name,m.type) for m in ob.modifiers]})
report={'file':Path(bpy.data.filepath).relative_to(ROOT).as_posix(),'pid':os.getpid(),'dirty':bpy.data.is_dirty,'objects':objects,'scene_changed':False}
(OUT/'live_object_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects':len(objects),'scene_changed':False,'pid':os.getpid()}))
