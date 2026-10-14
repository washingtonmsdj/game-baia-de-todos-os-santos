"""Inventário delimitado do exterior e instalação B101, sem mutação."""
import bpy,json,os,runpy
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b101_pavimentos_estruturais.blend'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']); inv=M.inverted()
prior=json.loads((root/'docs/reports/blender/lacerda-floors-b101/application.json').read_text())
expected=dict(prior['preserved_signatures'])
expected.update({r['object']:r['after']['signature'] for r in prior['added']})
rows=[]
for scene in bpy.data.scenes:
 for o in scene.objects:
  if o.type!='MESH' or not o.data.vertices:continue
  p=[inv@wm(o)@v.co for v in o.data.vertices]; b=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
  relevant=any('Lacerda' in c.name for c in o.users_collection) or o.name in expected
  if not relevant:continue
  rows.append({'object':o.name,'scene':scene.name,'visible':o.visible_get(),'hidden':o.hide_get(),'render_hidden':o.hide_render,
    'bounds':b,'collections':[c.name for c in o.users_collection],'materials':[m.name if m else None for m in o.data.materials],
    'properties':dict(o.items()),'animated':bool(o.animation_data),'parent':o.parent.name if o.parent else None,
    'signature':sig(o),'vertices_local':[list(v) for v in p] if len(p)<140 else None,'faces':[list(f.vertices) for f in o.data.polygons] if len(p)<140 else None})
delta=[n for n,s in expected.items() if n not in bpy.context.scene.objects or sig(bpy.context.scene.objects[n])!=s]
out=root/'docs/reports/blender/lacerda-exterior-b102';out.mkdir(parents=True,exist_ok=True)
r={'file':Path(bpy.data.filepath).relative_to(root).as_posix(),'pid':os.getpid(),'scene':bpy.context.scene.name,'dirty':bpy.data.is_dirty,'frame':bpy.context.scene.frame_current,
 'playing':any(w.screen.is_animation_playing for w in bpy.context.window_manager.windows),'session_geometry_delta':delta,
 'preserved_signatures':expected,'scenes':[{'name':s.name,'properties':dict(s.items())} for s in bpy.data.scenes],'rows':rows}
(out/'before.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf8')
print(json.dumps({'pid':r['pid'],'dirty':r['dirty'],'frame':r['frame'],'playing':r['playing'],'delta':delta,'objects':len(rows)},ensure_ascii=False))
