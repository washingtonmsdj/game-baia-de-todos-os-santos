"""Confere somente as superfícies remodeladas, após reabertura."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b59_encosta_transicao_continua.blend'
visual=scene.objects['B59 | GAMEPLAY TERRAIN HQ | encosta contínua'];collision=scene.objects['B59 | COLLISION | terreno encosta contínua']
ground=scene.objects['MVP | terreno corrigido | colisão estática']
def tree(ob):
    ob.data.calc_loop_triangles()
    return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(t.vertices) for t in ob.data.loop_triangles],all_triangles=True)
vt,ct,gt=tree(visual),tree(collision),tree(ground)
def hit(t,x,y):return t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400)[0]
def union(t,x,y):
    a=hit(t,x,y);b=hit(gt,x,y)
    if a is None:return b
    if b is None:return a
    return a if a.z>=b.z else b
same=len(visual.data.vertices)==len(collision.data.vertices) and all(a.co==b.co for a,b in zip(visual.data.vertices,collision.data.vertices))
seam=json.loads((root/'docs/reports/blender/coastal_seam_r30b58.json').read_text(encoding='utf8'))['physical_boundary_xy']
errors=[];seam_missing=0
for v in visual.data.vertices:
    x,y,z=map(float,v.co)
    if (abs(x-seam['x'])<.0001 and y>=seam['y']-.0001) or (abs(y-seam['y'])<.0001 and x>=seam['x']-.0001):
        p=hit(gt,max(x,seam['x']+.002),max(y,seam['y']+.002))
        if p is None:seam_missing+=1
        else:errors.append(abs(z-p.z))
road_rows=[]
for ob in scene.objects:
    if not ob.name.startswith('B59 | ROAD VISUAL |'):continue
    max_error=0;missing=0
    for v in ob.data.vertices:
        p=union(vt,v.co.x,v.co.y)
        if p is None:missing+=1
        else:max_error=max(max_error,abs(v.co.z-p.z-.015))
    road_rows.append({'object':ob.name,'vertices':len(ob.data.vertices),'support_missing':missing,'max_drape_error_m':max_error})
contract=json.loads((root/'world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json').read_text(encoding='utf8'))
paths=[]
for r in contract['roads']:
    if r['role']!='road_driveable':continue
    grades=[];cross=[];missing=0;collision_error=0;count=0
    for a,b in zip(r['blender_xy'],r['blender_xy'][1:]):
        a=Vector(a);b=Vector(b);d=b-a;L=d.length
        if L<.001:continue
        direction=d/L;normal=Vector((-direction.y,direction.x));previous=None
        for k in range(math.ceil(L)+1):
            p=a+d*(k/math.ceil(L))
            # Amostra apenas o domínio da expansão, com prova de apoio real.
            if hit(vt,p.x,p.y) is None:previous=None;continue
            supports=[]
            for side in (-.825,.825):
                q=p+normal*side;h=union(vt,q.x,q.y);c=union(ct,q.x,q.y)
                if h is None or c is None:missing+=1;continue
                supports.append(h.z);collision_error=max(collision_error,abs(h.z-c.z))
            if len(supports)!=2:previous=None;continue
            z=sum(supports)/2;cross.append(abs(supports[1]-supports[0])/1.65);count+=1
            if previous:
                xy,pz=previous;step=(p-xy).length
                if step>.001:grades.append(abs(z-pz)/step)
            previous=(p,z)
    paths.append({'osm_way_id':r['osm_way_id'],'name':r['name'],'sample_count':count,'missing_wheel_supports':missing,'max_grade':max(grades,default=None),'max_crossfall':max(cross,default=None),'max_collision_difference_m':collision_error,'traffic_approved':False})
visual.data.calc_loop_triangles();degenerate=sum(t.area<1e-10 for t in visual.data.loop_triangles)
result={'schema':'boas/coastal-transition-b59-check-v1','source_reopened':True,'visual_collision_identical':same,'finite':all(math.isfinite(c) for v in visual.data.vertices for c in v.co),'degenerate_triangles':degenerate,'seam_samples':len(errors),'seam_missing':seam_missing,'max_seam_error_m':max(errors,default=None),'road_surfaces':road_rows,'candidate_wheel_paths':paths,'source_dem_unchanged':True,'approved':False,'pending':['Lacuna histórica entre núcleo e cais permanece aberta','Grade/crossfall e navegação precisam de gate próprio; probes não equivalem à física na engine']}
(root/'docs/reports/blender/coastal_transition_r30b59_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert same and result['finite'] and not degenerate and not seam_missing
assert max(errors,default=0)<.005
print(json.dumps(result,ensure_ascii=False))
