"""Duas vistas locais do replay, sem editar a cidade nem salvar outra revisão."""
import bpy,json,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert (root/'artifacts/roads/r38/replay_complete.json').is_file()
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text());terrain=scene.objects[c['export']['road_object']]
car=scene.objects['GAMEPLAY | carro real V14 | teste Conceicao B38'];parts=list(car.children)
me=terrain.data;me.calc_loop_triangles();a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);M=np.array(wm(terrain));world=a.reshape(-1,3)@M[:3,:3].T+M[:3,3]
a=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',a);tri=a.reshape(-1,3)
a=np.empty(len(me.loop_triangles),dtype=np.int32);me.loop_triangles.foreach_get('polygon_index',a);polyidx=a
a=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',a);mats=a[polyidx]
previous=scene.frame_current;out=root/'artifacts/roads/r38';images=[]
for label,frame in [('middle',scene.frame_end//2),('end',scene.frame_end)]:
    scene.frame_set(frame);pos=wm(car).translation;p=world[tri];lo=np.array(pos[:2])-22;hi=np.array(pos[:2])+22
    ids=np.flatnonzero(np.all(p[:,:,:2].max(axis=1)>=lo,axis=1)&np.all(p[:,:,:2].min(axis=1)<=hi,axis=1));local=tri[ids];verts=np.unique(local);mapping=np.full(len(world),-1,dtype=np.int32);mapping[verts]=np.arange(len(verts))
    review=bpy.data.scenes.new('TEMP | Revisao estrada');review.render.engine='BLENDER_WORKBENCH';review.display.shading.color_type='MATERIAL';review.display.shading.light='STUDIO';review.display.shading.show_cavity=True
    review.render.resolution_x=1000;review.render.resolution_y=720;review.render.resolution_percentage=100;objects=[]
    mesh=bpy.data.meshes.new('TEMP | Piso');mesh.from_pydata(world[verts].tolist(),[],mapping[local].tolist());mesh.update()
    for m in terrain.data.materials:mesh.materials.append(m)
    mesh.polygons.foreach_set('material_index',mats[ids]);obj=bpy.data.objects.new(mesh.name,mesh);review.collection.objects.link(obj);objects.append(obj)
    for part in parts:
        o=bpy.data.objects.new('TEMP | '+part.name,part.data);review.collection.objects.link(o);o.matrix_world=wm(part);objects.append(o)
    camdata=bpy.data.cameras.new('TEMP | Camera');cam=bpy.data.objects.new(camdata.name,camdata);review.collection.objects.link(cam);objects.append(cam);review.camera=cam
    cam.location=pos+Vector((0,0,70));cam.rotation_euler=(pos+Vector((0,0,.6))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=14;camdata.clip_end=200
    try:
        bpy.context.window.scene=review;image=out/f'replay_{label}.png';review.render.filepath=str(image);bpy.ops.render.render(write_still=True);images.append(image.relative_to(root).as_posix())
    finally:
        bpy.context.window.scene=scene
        for o in objects:bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.scenes.remove(review);bpy.data.meshes.remove(mesh);bpy.data.cameras.remove(camdata)
scene.frame_set(previous)
path=root/'docs/reports/blender/conceicao_binding_r30b38.json';r=json.loads(path.read_text());r['validation']['local_images']=images;path.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'images':images}))
