"""Conferência da malha particionada e sincronização de apoio, sem decoração."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text());scene=bpy.context.scene
if c['world_source']['revision']!='R30C.3':raise RuntimeError('Revisão de entrada incorreta')
source=scene.objects[c['export']['road_object']]
# Recupera a atribuição de materiais da fonte preservada, sem substituir a cena.
with bpy.data.libraries.load(str(root/'blender/salvador_lacerda_mvp_r30c2_urban_slice.blend'),link=False) as (src,dst):dst.objects=[source.name]
original=dst.objects[0];me=original.data;me.calc_loop_triangles();tris=list(me.loop_triangles)
tree=BVHTree.FromPolygons([original.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in tris],all_triangles=True)
for f in source.data.polygons:
    p=source.matrix_world@f.center;hit=tree.find_nearest(p)
    if hit and hit[2] is not None:f.material_index=tris[hit[2]].material_index
bpy.data.objects.remove(original,do_unlink=True)
game=bpy.data.collections['41 GAMEPLAY | URBAN SLICE'];roads=next(o for o in game.objects if o['boas_role']=='road');walk=next(o for o in game.objects if o['boas_role']=='walkable')
def bvh(o):
    o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True,epsilon=.0001)
roadtree=bvh(roads);walktree=bvh(walk);terraintree=bvh(source)
config_path=root/'prototypes/threejs-water-lab/public/data/urban_slice.json';config=json.loads(config_path.read_text())
def height(tree,x,y):
    # Local-height ray avoids cancellation on small clipped triangles; 0.1mm
    # BVH tolerance is numerical precision, not an expanded gameplay floor.
    hit=tree.ray_cast(Vector((x,y,75)),Vector((0,0,-1)),160)[0];return hit.z if hit else None
# Drain/crossing landing grades use the same terrain, with a documented local
# reduction of the 12cm curb to zero at the crossing rather than an overlay ramp.
a,b=config['crossing']['points'];center=Vector(((a[0]+b[0])/2,-(a[2]+b[2])/2,0));normal=Vector((a[0]-b[0],-(a[2]-b[2]),0)).normalized();forward=Vector((-normal.y,normal.x,0))
for v in walk.data.vertices:
    p=walk.matrix_world@v.co;d=p-center;along=abs(d.dot(forward));across=abs(d.dot(normal))
    if along<=2.0 and 3.05<=across<=5.0:
        curb=.12*max(0,min(1,(across-3.05)/1.95));v.co.z-=.12-curb
walk.data.update();walktree=bvh(walk)
# Source-derived support for spawn, navigation and painted markings.
spawn=config['spawn'];z=height(walktree,spawn[0],-spawn[2]);
if z is None:raise RuntimeError('Spawn sem passeio')
spawn[1]=round(z+.04,6)
for route in config['routes']:
    for p in route['points']:
        h=height(roadtree,p[0],-p[2]);
        if h is None:raise RuntimeError('Nó da rota sem pista')
        p[1]=round(h,6)
for p in config['crossing']['points']:
    h=height(walktree,p[0],-p[2])
    if h is None:
        nearest=walktree.find_nearest(Vector((p[0],p[2]*-1,p[1])))
        if not nearest or nearest[3]>.5:raise RuntimeError('Extremo da travessia sem passeio')
        point=nearest[0];p[:]=[point.x,point.z,-point.y];h=point.z
    p[1]=round(h,6)
for o in scene.objects:
    if o.type!='MESH' or not (o.name.startswith('SLICE | faixa pedestre') or o.name.startswith('SLICE | linha parada')):continue
    inverse=o.matrix_world.inverted()
    for v in o.data.vertices:
        p=o.matrix_world@v.co;h=height(roadtree,p.x,p.y)
        if h is not None:v.co=inverse@Vector((p.x,p.y,h+.006))
    o.data.update()
# Close only actual sidewalk boundaries. Triangulation T-junction edges inside
# the same continuous surface must never become curb walls.
curb=scene.objects['SLICE | guias da malha particionada'];bm=bmesh.new();bm.from_mesh(walk.data);vs=[];faces=[]
for e in bm.edges:
    if not e.is_boundary:continue
    a,b=[v.co.copy() for v in e.verts];d=b-a;d.z=0
    if d.length<1e-5:continue
    normal=Vector((-d.y,d.x,0)).normalized();mid=(a+b)/2
    if all(height(walktree,*(mid+normal*s)[:2]) is not None for s in [-.003,.003]):continue
    bottom=[]
    for p in [a,b]:
        h=height(roadtree,p.x,p.y)
        if h is None:h=height(terraintree,p.x,p.y)
        if h is None:h=height(tree,p.x,p.y)
        if h is None:raise RuntimeError('Guia sem base')
        bottom.append(Vector((p.x,p.y,h)))
    start=len(vs);vs.extend([tuple(a),tuple(b),tuple(bottom[1]),tuple(bottom[0])]);faces.append((start,start+1,start+2,start+3))
bm.free();curb.data.clear_geometry();curb.data.from_pydata(vs,[],faces);curb.data.update()
def runtime(p):return [round(p.x,6),round(p.z,6),round(-p.y,6)]
config['surfaces']=[]
for o in game.objects:
    o.data.calc_loop_triangles();config['surfaces'].append({'name':o.name,'role':o['boas_role'],'positions':[v for p in o.data.vertices for v in runtime(o.matrix_world@p.co)],'indices':[v for t in o.data.loop_triangles for v in t.vertices]})
# Test support geometrically along every road segment, not only OSM nodes.
missing=[];overlap=[];samples=0;maxgrade=0
for route in config['routes']:
    for a,b in zip(route['points'],route['points'][1:]):
        p=Vector((a[0],-a[2],a[1]));q=Vector((b[0],-b[2],b[1]));d=q-p;d.z=0;n=Vector((-d.y,d.x,0)).normalized();length=d.length;previous=None
        for i in range(math.ceil(length)+1):
            t=i/math.ceil(length);point=p.lerp(q,t)
            for offset in [-1.0,0,1.0]:
                r=point+n*offset;h=height(roadtree,r.x,r.y);samples+=1
                if h is None:missing.append([route['id'],runtime(r)])
                terrainh=height(terraintree,r.x,r.y)
                if h is not None and terrainh is not None and abs(h-terrainh)<.015:overlap.append(runtime(r))
                if offset==0 and h is not None:
                    if previous is not None:maxgrade=max(maxgrade,abs(h-previous)/(length/math.ceil(length)))
                    previous=h
if missing or overlap:
    (root/'artifacts/urban-slice/terrain_missing.json').write_text(json.dumps({'missing':missing,'overlap':overlap,'maximum_grade':maxgrade}),encoding='utf8')
    raise RuntimeError('Falha de continuidade/sobreposição: '+str((len(missing),len(overlap))))
config_path.write_text(json.dumps(config,ensure_ascii=False,separators=(',',':')),encoding='utf8')
text=bpy.data.texts.get('BOAS_URBAN_SLICE.json');text.clear();text.write(json.dumps({k:v for k,v in config.items() if k not in ('surfaces','obstacles')},ensure_ascii=False,indent=2))
(root/'world/areas/mvp-centro-lacerda/urban_slice.json').write_text(text.as_string(),encoding='utf8')
output=root/'blender/salvador_lacerda_mvp_r30c4_terrain_continuity.blend';bpy.ops.wm.save_as_mainfile(filepath=str(output));c['world_source'].update(file=output.relative_to(root).as_posix(),revision='R30C.4',sha256=hashlib.sha256(output.read_bytes()).hexdigest());c['runtime']['world']['spawn']=dict(x=spawn[0],z=spawn[2],headingDeg=0);cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report_path=root/'docs/reports/blender/urban_terrain_partition.json';report=json.loads(report_path.read_text(encoding='utf8'));report.update(source=c['world_source'],support_samples=samples,missing_road_samples=len(missing),overlap_samples=len(overlap),maximum_centerline_grade=maxgrade,spawn=spawn,visual_review='pending');report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
# Visible viewport of the terrain focus, without opening another window.
from mathutils import Quaternion
target=Vector((-6,-91,68));eye=target+Vector((-38,-45,35))
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        region=area.spaces.active.region_3d;region.view_rotation=(target-eye).to_track_quat('-Z','Y');region.view_distance=(eye-target).length;region.view_location=target;region.view_perspective='PERSP';area.spaces.active.shading.type='MATERIAL'
