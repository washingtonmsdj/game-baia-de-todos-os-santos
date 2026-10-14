"""Encontros dos corredores na sessão B93; sem alteração de geometria."""
import bpy,json,runpy,os
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b93_estrutura_inferior_documental.blend'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted();cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
names=['SUPERIOR | piso saguão','SUPERIOR | cobertura saguão','INFERIOR | piso do saguão','INFERIOR | cobertura do saguão','INFERIOR | parede lateral','INFERIOR | parede lateral.001','LAC R30B08 | apoio oposto | corpo estrutural afunilado','SUPERIOR | parede lateral saguão','SUPERIOR | parede lateral saguão.001','B88 | cidade alta | alas estruturais sob edifício','B88 | galeria nova | limite envidraçado','B88 | galeria nova | peitoril estrutural','B88 | galeria nova | verga estrutural','TORRE | cornija galeria','TORRE | teto galeria']
rows=[]
for n in names:
    o=bpy.context.scene.objects.get(n)
    if not o:continue
    t=inv@wm(o);p=[list(t@v.co) for v in o.data.vertices]
    rows.append({'object':n,'visible':o.visible_get(),'signature':sig(o),'vertices_local':p,'faces':[list(f.vertices) for f in o.data.polygons],'bounds':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]})
out=root/'docs/reports/blender/lacerda-closure-b94';out.mkdir(parents=True,exist_ok=True)
(out/'before.json').write_text(json.dumps({'file':bpy.data.filepath,'scene':bpy.context.scene.name,'pid':os.getpid(),'polygons':cfg['polygons'],'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps([{'object':r['object'],'bounds':r['bounds'],'vertices':len(r['vertices_local'])} for r in rows],ensure_ascii=False))
window=next(w for w in bpy.context.window_manager.windows if w.screen);a=next(a for a in window.screen.areas if a.type=='VIEW_3D');rg=next(r for r in a.regions if r.type=='WINDOW')
with bpy.context.temp_override(window=window,area=a,region=rg):
    runpy.run_path(str(root/'automation/blender/present_lacerda_structure_b91.py'))
    runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b93-closure-before.png'})
