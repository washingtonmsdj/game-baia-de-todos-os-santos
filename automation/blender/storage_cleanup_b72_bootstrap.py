import bpy,json,shutil,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2]
rows=[]
for n in ['salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a7_road_graph','salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a8_ocean']:
 p=r/'blender'/(n+'.blend1');q=r/'blender'/(n+'.blend')
 if p.exists() and q.is_file() and q.stat().st_size>1000000 and p.resolve().parent==(r/'blender').resolve():
  rows.append({'path':p.relative_to(r).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'preserved':q.relative_to(r).as_posix()});p.unlink()
(r/'docs/reports/blender/storage_cleanup_b72_bootstrap.json').write_text(json.dumps({'deleted':rows,'free':shutil.disk_usage(r).free}),encoding='utf8')
