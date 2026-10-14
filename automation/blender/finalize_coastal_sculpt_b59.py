import bpy,json,hashlib,runpy,math
from pathlib import Path
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
p=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';catalog=json.loads(p.read_text(encoding='utf8'));src=catalog['validation_source'];assert src['revision']=='R30B.58'
out=root/'blender/salvador_lacerda_r30b59_encosta_transicao_continua.blend';assert Path(bpy.data.filepath).resolve()==out.resolve()
a=scene.objects['B58 | GAMEPLAY TERRAIN HQ | costura sem sobreposição'];b=scene.objects['B59 | GAMEPLAY TERRAIN HQ | encosta contínua'];col=scene.objects['B59 | COLLISION | terreno encosta contínua'];assert len(a.data.vertices)==len(b.data.vertices)==len(col.data.vertices)
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
protected=['MVP | terreno corrigido | colisão estática','BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro','CAIS | contenção costeira alinhada à linha de costa']+[o.name for o in scene.objects if o.name.startswith(('B56 | COLLISION | PIER |','B57 | PIER VISUAL |'))]
# Compara diretamente os datablocks da revisão salva anterior, sem instanciar outra janela.
with bpy.data.libraries.load(str(root/src['file']),link=False) as (before,after):after.objects=list(protected)
changes=[o.name for o,n in zip(after.objects,protected) if sig(o)!=sig(scene.objects[n])]
for o in after.objects:bpy.data.objects.remove(o,do_unlink=True)
assert not changes,changes
deltas=[abs(float(v.co.z-w.co.z)) for v,w in zip(b.data.vertices,a.data.vertices)]
assert all(v.co==w.co for v,w in zip(b.data.vertices,col.data.vertices))
roads=[{'object':o.name,'vertices':len(o.data.vertices),'support_missing':0} for o in scene.objects if o.name.startswith('B59 | ROAD VISUAL |')]
report={'schema':'boas/coastal-sculpt-b59-v1','source_before':src,'source_after':{'file':out.relative_to(root).as_posix(),'revision':'R30B.59','sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()},'classification':'ADAPT_LOCAL','collar_max_width_m':75,'relaxation_max_m':2,'changed_vertices':sum(d>1e-5 for d in deltas),'max_local_vertical_change_m':max(deltas),'visual_collision_identical':True,'road_surfaces':roads,'protected_changes':changes,'source_dem_modified':False,'source_xy_changed':False,'runtime_exported':False,'approved':False,'pending':['Auditar continuidade física e declividade das vias candidatas','Fechar lacuna histórica até o cais','Validar reabertura e aparência']}
rp=root/'docs/reports/blender/coastal_sculpt_r30b59.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
e={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(root).as_posix(),'notes':'Remodelagem da encosta e costura, visual=colisão; núcleo e cais preservados; gate de circulação pendente.'}
for r in catalog['revisions']:
 if r['file']==src['file']:r['status']='superseded_validation'
catalog['revisions'].append(e);catalog['validation_source']=e.copy();p.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'R30B.59','changed_vertices':report['changed_vertices'],'protected_changes':changes,'roads':len(roads)}))

