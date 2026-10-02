"""Confere paredes da malha de terreno contra envelope superior do carro."""
import bpy,json,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
o=scene.objects[c['export']['road_object']];me=o.data;me.calc_loop_triangles()
a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);M=np.array(wm(o));world=a.reshape(-1,3)@M[:3,:3].T+M[:3,3]
a=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',a);tree=BVHTree.FromPolygons(world.tolist(),a.reshape(-1,3).tolist(),all_triangles=True)
p=root/'docs/reports/blender/conceicao_binding_r30b38.json';r=json.loads(p.read_text());car=scene.objects['GAMEPLAY | carro real V14 | teste Conceicao B38'];old=scene.frame_current;collisions=[];samples=0
for frame in range(1,scene.frame_end+1,6):
    scene.frame_set(frame);m=wm(car)
    for y in (-2.56,0,2.56):
        for z in (.4,1,1.51):
            start=m@Vector((0,y,z))
            for sign in (-1,1):
                direction=(m.to_3x3()@Vector((sign,0,0))).normalized();q,n,i,d=tree.ray_cast(start,direction,1.025);samples+=1
                if q is not None:collisions.append({'frame':frame,'local_y':y,'local_z':z,'side':sign,'distance':d,'normal':list(n)})
scene.frame_set(old)
r['validation']['terrain_body_clearance']={'method':'raios laterais do envelope em três estações longitudinais e três alturas, a cada seis frames; não cobre todos os obstáculos externos','rays':samples,'hits':collisions,'approved':not collisions}
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'samples':samples,'hits':len(collisions),'first_hits':collisions[:4]}))
