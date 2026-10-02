"""Compara eixos por OSM ID e apoio na malha atual; somente leitura da fonte."""
import bpy,json,math,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
catalog=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))
source=catalog['authoring_source']; assert Path(bpy.data.filepath).resolve()==(root/source['file']).resolve()
contract=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
terrain=scene.objects[contract['export']['road_object']]; terrain.data.calc_loop_triangles()
triangles=list(terrain.data.loop_triangles); points=[wm(terrain)@v.co for v in terrain.data.vertices]
tree=BVHTree.FromPolygons(points,[list(t.vertices) for t in triangles],all_triangles=True)
def hits(xy):
    p=Vector((xy[0],xy[1],150)); rows=[]
    for _ in range(8):
        q,normal,index,d=tree.ray_cast(p,Vector((0,0,-1)),350)
        if q is None:break
        slot=triangles[index].material_index
        rows.append({'z':q.z,'material':terrain.data.materials[slot].name,'face':triangles[index].polygon_index,'normal':list(normal)})
        p=q-Vector((0,0,.002))
    return rows
g=json.loads((root/contract['staging']['roads']).read_text(encoding='utf8'))
nodes={n['id']:n for n in g['nodes']}; edges={e['id']:e for e in g['edges']}
curves=[]
for o in scene.objects:
    if o.type!='CURVE' or str(o.get('osm_id','')) not in ('421206045','48846625'):continue
    curves.append({'object':o.name,'osm_way_id':str(o['osm_id']),'matrix':[list(r) for r in wm(o)],'points':[[list(wm(o)@Vector(p.co[:3])) for p in sp.points] for sp in o.data.splines],'properties':{k:str(v) for k,v in o.items()}})
legacy=next(r for r in curves if r['osm_way_id']=='421206045')['points'][0]
way=next(w for w in g['ways'] if w['osm_way_id']==421206045)
assert len(legacy)==len(way['node_refs']), 'Não associar pontos por proximidade'
legacy_by_node=dict(zip(way['node_refs'],legacy)); samples=[]
for edgeid in ('way-421206045-seg-5','way-421206045-seg-6','way-421206045-seg-7','way-421206045-seg-8'):
    e=edges[edgeid]; a=Vector((*nodes[e['from']]['blender_xy'],0));b=Vector((*nodes[e['to']]['blender_xy'],0))
    olda=Vector(legacy_by_node[e['from']]);oldb=Vector(legacy_by_node[e['to']])
    for i in range(21):
        p=a.lerp(b,i/20); old=olda.lerp(oldb,i/20);d=(b-a).normalized();side=Vector((-d.y,d.x,0))
        samples.append({'edge_id':edgeid,'fraction':i/20,'reference_xy':list(p.xy),'authoring_xy':list(old.xy),'axis_offset_units':(p-old).xy.length,'graph_hits':hits(p),'authoring_hits':hits(old),'cross_section': [{'distance':s,'hits':hits(old+side*s)} for s in (-4,-3,-2,-1,0,1,2,3,4)]})
out=root/'artifacts/roads/r38';out.mkdir(parents=True,exist_ok=True)
report={'source':source,'classification':'NEEDS_REVIEW','curves':curves,'samples':samples,'scene_changed':False,'real_width_m':None,'legacy_z_is_altimetry':False}
(out/'conceicao_inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'source':source['revision'],'samples':len(samples),'eixos':[(r['object'],len(r['points'][0])) for r in curves],'max_xy_axis_difference':max(r['axis_offset_units'] for r in samples)},ensure_ascii=False))
# Vue locale éphémère: terrain seul et eixos existants, jamais une nouvelle piste.
review=bpy.data.scenes.new('REVIEW TEMP | Conceição R38'); review.render.engine='BLENDER_WORKBENCH'
review.display.shading.light='STUDIO';review.display.shading.color_type='MATERIAL';review.display.shading.show_cavity=True
review.render.resolution_x=1100;review.render.resolution_y=800;review.render.resolution_percentage=100
vv=[];ff=[];slots=[];lookup={}
for f in terrain.data.polygons:
    coords=[points[k] for k in f.vertices]
    if not any(-256<p.x<-125 and -283<p.y<-104 for p in coords):continue
    ids=[]
    for k in f.vertices:
        if k not in lookup:lookup[k]=len(vv);vv.append(points[k])
        ids.append(lookup[k])
    ff.append(ids);slots.append(f.material_index)
me=bpy.data.meshes.new('REVIEW TEMP | Terrain');me.from_pydata(vv,[],ff);me.update()
for m in terrain.data.materials: me.materials.append(m)
for f,slot in zip(me.polygons,slots):f.material_index=slot
obj=bpy.data.objects.new(me.name,me);review.collection.objects.link(obj)
camera=bpy.data.cameras.new('REVIEW TEMP | Camera');cam=bpy.data.objects.new(camera.name,camera);review.collection.objects.link(cam);review.camera=cam
camera.type='ORTHO';camera.ortho_scale=190;camera.clip_end=600
try:
    bpy.context.window.scene=review
    for label,eye,target in [('top',Vector((-192,-195,210)),Vector((-192,-195,30))),('oblique',Vector((-334,-307,165)),Vector((-192,-195,30)))]:
        cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(out/f'before_{label}.png');bpy.ops.render.render(write_still=True)
finally:
    bpy.context.window.scene=scene
    bpy.data.objects.remove(obj,do_unlink=True);bpy.data.objects.remove(cam,do_unlink=True);bpy.data.scenes.remove(review);bpy.data.meshes.remove(me);bpy.data.cameras.remove(camera)
