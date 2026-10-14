"""B72: enquadramento da área corrigida e leitura da sobreposição de terreno."""
import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
names=['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'];trees=[]
for n in names:
 o=s.objects[n];o.data.calc_loop_triangles()
 trees.append(BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[t.vertices for t in o.data.loop_triangles],all_triangles=True))
rows=[]
for y in np.arange(-280,-12,3.):
 for dx in [.25,.5,1]:
  x=-285.70343017578125+dx;hits=[t.ray_cast(Vector((-285.70343017578125+(dx if k==0 else -dx),y,150)),Vector((0,0,-1)),300)[0] for k,t in enumerate(trees)]
  if all(h is not None for h in hits):rows.append({'xy':[x,float(y)],'core_z':hits[0].z,'extension_z':hits[1].z,'difference_m':abs(hits[0].z-hits[1].z)})
out={'source':Path(bpy.data.filepath).name,'sample_count':len(rows),'max_opposite_seam_difference_m':max((x['difference_m'] for x in rows),default=None),'p95_opposite_seam_difference_m':float(np.percentile([x['difference_m'] for x in rows],95)) if rows else None,'largest':sorted(rows,key=lambda x:x['difference_m'],reverse=True)[:16],'read_only':True}
(r/'docs/reports/blender/city_seam_b72_overlap.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active
   sp.region_3d.view_location=(-315,-125,15);sp.region_3d.view_distance=300
   sp.region_3d.view_rotation=Vector((1,-.6,1.6)).to_track_quat('Z','Y')
   sp.region_3d.view_perspective='ORTHO';sp.overlay.show_overlays=False
print(json.dumps(out))
