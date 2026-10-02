"""Mantém a revisão de teste visível e registra a conferência das capturas."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
car=scene.objects['TESTE | carro | apoio de quatro rodas'];scene.frame_set(2200)
window=next(w for w in bpy.context.window_manager.windows if any(a.type=='VIEW_3D' for a in w.screen.areas));area=next(a for a in window.screen.areas if a.type=='VIEW_3D');r=area.spaces.active.region_3d
target=car.matrix_world.translation.copy()+Vector((0,0,.8));eye=target+Vector((-12,-14,11));r.view_rotation=(target-eye).to_track_quat('-Z','Y');r.view_distance=(target-eye).length;r.view_location=target;r.update()
out=root/'artifacts/terrain-vehicle/r30b23_vehicle_test.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
path=root/'docs/reports/blender/terrain_vehicle_replay.json';report=json.loads(path.read_text());report['test_blend_sha256']=hashlib.file_digest(out.open('rb'),'sha256').hexdigest();report['visual_review']='Três capturas inspecionadas: carro sobre o pavimento nos trechos percorridos; bordas de pista/passeio serrilhadas e encontros pendentes. Não aprovado como teste dinâmico integral.';path.write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print(json.dumps({'source_preserved':True,'test_blend':out.relative_to(root).as_posix(),'visible_frame':2200,'approved':False}))
