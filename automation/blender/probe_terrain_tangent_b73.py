"""B73: candidato de tangente da encosta, mesmas posições e vias bloqueadas."""
import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
src=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source'];assert src['revision']=='R30B.72'
objects=[s.objects[n] for n in ['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa']];trees=[]
for o in objects:
 o.data.calc_loop_triangles();trees.append(BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[t.vertices for t in o.data.loop_triangles],all_triangles=True))
me=objects[1].data;xyz=np.array([v.co for v in me.vertices],float);new=xyz[:,2].copy();seam=-285.70343017578125;width=8.
def hit(tree,x,y):
 p=tree.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),300)[0];return p.z if p is not None else None
locked=set()
for p in me.polygons:
 if me.attributes['boas_surface_role'].data[p.index].value in (1,2):locked.update(p.vertices)
eligible=np.where((xyz[:,0]>=seam-width)&(xyz[:,0]<=seam+.001)&(xyz[:,1]>=-281)&(xyz[:,1]<=-94.85))[0];skipped=0
for i in eligible:
 if int(i) in locked:continue
 x,y,z=xyz[i];z0=hit(trees[1],seam-width,y);zl=hit(trees[1],seam-width-.2,y);zr=hit(trees[1],seam-width+.2,y)
 z1=hit(trees[0],seam+.001,y);za=hit(trees[0],seam+.05,y);zb=hit(trees[0],seam+1.05,y)
 if any(v is None for v in [z0,zl,zr,z1,za,zb]):skipped+=1;continue
 m0=(zr-zl)/.4;m1=zb-za;t=np.clip((x-seam+width)/width,0,1)
 target=(2*t**3-3*t**2+1)*z0+(t**3-2*t**2+t)*width*m0+(-2*t**3+3*t**2)*z1+(t**3-t**2)*width*m1
 target=float(np.clip(target,min(z0,z1),max(z0,z1)));fade=min(1,max(0,(y+281)/3),max(0,(-94.85-y)/3))
 new[i]=z+(target-z)*fade
candidate=xyz.copy();candidate[:,2]=new;newtree=BVHTree.FromPolygons([Vector(v) for v in candidate],[t.vertices for t in me.loop_triangles],all_triangles=True)
rows=[]
for y in np.arange(-277,-98,1.):
 vals=[hit(trees[0],seam+.01,y),hit(trees[0],seam+1.01,y),hit(trees[1],seam-.01,y),hit(trees[1],seam-1.01,y),hit(newtree,seam-.01,y),hit(newtree,seam-1.01,y)]
 if any(v is None for v in vals):continue
 a,b,c,d,e,f=vals;rows.append({'y':float(y),'slope_discontinuity_before':abs((b-a)-(c-d)),'slope_discontinuity_after':abs((b-a)-(e-f)),'opposite_point_difference_before':abs(a-c),'opposite_point_difference_after':abs(a-e)})
stats=lambda key:{'max':max(x[key] for x in rows),'p95':float(np.percentile([x[key] for x in rows],95))}
out={'source':src,'classification':'ADAPT_LOCAL','design_transition_width_m':width,'width_surveyed':False,'changed_vertices':int((abs(new-xyz[:,2])>1e-5).sum()),'max_delta_z_m':float(abs(new-xyz[:,2]).max()),'skipped_no_support':skipped,'locked_vertices':len(locked),'finite':bool(np.isfinite(new).all()),'xy_changed':False,'topology_changed':False,'source_dem_changed':False,'metrics':{k:stats(k) for k in ['slope_discontinuity_before','slope_discontinuity_after','opposite_point_difference_before','opposite_point_difference_after']},'rows':rows}
np.savez_compressed(r/'artifacts/waterfront/terrain_tangent_b73.npz',xyz=xyz,z=new,locked=np.array(sorted(locked),int))
(r/'docs/reports/blender/terrain_tangent_b73_candidate.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
