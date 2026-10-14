"""Persistência e captura da B84 reaberta na janela existente."""
import bpy,bmesh,json,hashlib,runpy,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-glazing-b84'
r=json.loads((OUT/'application.json').read_text(encoding='utf8'));v=json.loads((OUT/'validation.json').read_text(encoding='utf8'))
assert v['passed'] and Path(bpy.data.filepath).resolve()==(ROOT/r['file']).resolve()
proof=json.loads((ROOT/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'));assert proof['file']==r['file'] and proof['load_post_completed']
assert bpy.context.scene.name=='SALVADOR | ESBOCO OFICIAL'
with (ROOT/r['parent_file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['parent_sha256']
for name in r['changed_objects']:
    ob=bpy.context.scene.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);assert not any(not e.is_manifold for e in bm.edges) and not any(f.calc_area()<1e-8 for f in bm.faces);bm.free()
    if 'Lambril' not in name:
        glassfaces=sum(p.material_index==1 for p in ob.data.polygons);assert glassfaces==27*6
v['reopened']=True;v['reopened_pid']=os.getpid();v['parent_snapshot_preserved']=True
(OUT/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(ROOT/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b84-glazed-upper-return.png'})
print(json.dumps({'passed':True,'reopened':True,'file':r['file'],'scene':bpy.context.scene.name,'pid':os.getpid()},ensure_ascii=False))
