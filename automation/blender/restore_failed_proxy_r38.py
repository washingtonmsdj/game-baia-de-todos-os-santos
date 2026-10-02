"""Desfaz exclusivamente o refino não salvo da tentativa B38."""
import bpy,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2]
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
o=bpy.context.scene.objects[c['export']['terrain_proxy']]
path=root/'artifacts/roads/r38/proxy_restore.blend';shutil.copyfile(bpy.data.filepath,path)
before=set(bpy.data.objects)
try:
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=[o.name]
    old=o.data;o.data=dst.objects[0].data.copy()
    if old.users==0:bpy.data.meshes.remove(old)
    for k in list(o.keys()):
        if k=='boas_conceicao_refinement':del o[k]
finally:
    for obj in set(bpy.data.objects)-before:bpy.data.objects.remove(obj,do_unlink=True)
    path.unlink()
print(json.dumps({'proxy_restored':o.name,'vertices':len(o.data.vertices)}))
