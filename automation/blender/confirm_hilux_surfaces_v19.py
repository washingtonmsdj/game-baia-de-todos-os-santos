import bpy,runpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[2]
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_superficies_v19.blend'
bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
runpy.run_path(str(r/'automation/blender/inspect_hilux_surfaces_v19.py'),run_name='__main__')
runpy.run_path(str(r/'automation/blender/review_hilux_surfaces_v19.py'),run_name='__main__')
rp=r/'docs/reports/blender/hilux_superficies_v19.json'
d=json.loads(rp.read_text(encoding='utf8'));d['source_reopened']=True
rp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
