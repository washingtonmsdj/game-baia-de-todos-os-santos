import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];r=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'));o=bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'];o.data.calc_loop_triangles()
bvh=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
rows=[]
for s in r['galleries']['segments']:
    p=Vector(s['origin_world']);u=Vector(s['along_world']);n=Vector(s['outward_world']);L=s['length_from_existing_controls_m'];cross=[]
    for f in (.05,.5,.95):
        cross.append({'fraction':f,'samples':[(d,list(h[0]) if h[0] else None) for d in (-4,-1,0,1,3,5,8,12,16,24,32,48) for h in [bvh.ray_cast(p+u*L*f+n*d+Vector((0,0,120)),Vector((0,0,-1)),200)]]})
    rows.append({'segment':s['name'],'sections':cross})
collection=bpy.data.collections['16 ENCOSTA | contencao da praca'];objects=[{'name':x.name,'type':x.type,'vertices':[list(x.matrix_world@v.co) for v in x.data.vertices] if x.type=='MESH' and len(x.data.vertices)<40 else None,'properties':{k:x[k] for k in x.keys() if isinstance(x[k],(str,int,float,bool))}} for x in collection.all_objects]
out={'ground':rows,'walls':objects,'terrain_materials':[m.name for m in o.data.materials],'terrain_vertices':len(o.data.vertices),'terrain_polygons':len(o.data.polygons),'plaza_vertices':[list(bpy.data.objects['PRAÇA | OSM 1263035782'].matrix_world@v.co) for v in bpy.data.objects['PRAÇA | OSM 1263035782'].data.vertices]}
(root/'artifacts/palacio-rio-branco/gallery_ground.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'ground':rows,'walls':[(x['name'],x['type'],x['properties']) for x in objects],'terrain_materials':out['terrain_materials'],'plaza':out['plaza_vertices']},ensure_ascii=True))
