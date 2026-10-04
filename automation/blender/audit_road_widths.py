"""Mede pavimento autoral transversalmente; não infere largura real ou faixas."""
import bpy, json, math, hashlib, statistics
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
source = json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['authoring_source']
assert Path(bpy.data.filepath).resolve() == (root/source['file']).resolve()
contract = json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
graph = json.loads((root/contract['staging']['roads']).read_text(encoding='utf8'))
ground = scene.objects[contract['export']['road_object']]
mesh = ground.data
mesh.calc_loop_triangles()
triangles = list(mesh.loop_triangles)
tree = BVHTree.FromPolygons([ground.matrix_world@v.co for v in mesh.vertices], [list(t.vertices) for t in triangles], all_triangles=True)
road_slots = {i for i,m in enumerate(mesh.materials) if m and m.name in contract['export']['road_materials']}
roads = {int(o['boas_osm_way_id']):o for o in scene.objects if o.name.startswith('R30A7 | ROAD |') and 'boas_osm_way_id' in o}
ways = {w['osm_way_id']:w for w in graph['ways']}
results=[]
counts=Counter()
for edge in graph['edges']:
    way=ways[edge['osm_way_id']]
    curve=roads.get(edge['osm_way_id'])
    record={'edge_id':edge['id'],'osm_way_id':edge['osm_way_id'],'name':way.get('name'),'stations':[],'real_width_verified_m':None,'approved':False}
    if curve is None:
        record['binding_status']='missing_curve';results.append(record);counts['missing_curve']+=1;continue
    points=[curve.matrix_world@Vector(p.co[:3]) for sp in curve.data.splines for p in sp.points]
    binding={i:p for i,p in enumerate(points)} if len(points)==len(way['node_refs']) else {}
    if not binding:
        for point in points:
            matches=[i for i,xy in enumerate(way['blender_xy']) if math.dist(list(point)[:2],xy)<.01]
            if len(matches)==1:binding[matches[0]]=point
    index=int(edge['id'].rsplit('-',1)[-1])
    if index not in binding or index+1 not in binding:
        record['binding_status']='unresolved_endpoint';results.append(record);counts['unresolved_endpoint']+=1;continue
    a,b=binding[index],binding[index+1]
    direction=(b-a).to_2d()
    if direction.length<.01:continue
    direction.normalize();right=Vector((direction.y,-direction.x,0))
    record['binding_status']='same_osm_way_node_order'
    record['osm_direction_candidate']=edge['direction']
    for fraction in (.25,.5,.75):
        center=a.lerp(b,fraction)
        hit,normal,face,_=tree.ray_cast(center+Vector((0,0,2)),Vector((0,0,-1)),4.)
        station={'fraction':fraction,'position':list(center),'classification':'NEEDS_REVIEW','width_m':None,'issues':[]}
        if hit is None or triangles[face].material_index not in road_slots or normal.z<.7:
            station['issues'].append('center_not_drivable_pavement');record['stations'].append(station);counts['center_not_drivable_pavement']+=1;continue
        center=hit
        # Local lateral slope follows the actual face; do not jump road layers.
        slope=-(normal.x*right.x+normal.y*right.y)/normal.z
        def pavement(offset):
            p=center+right*offset;p.z+=slope*offset
            q,n,idx,_=tree.ray_cast(p+Vector((0,0,.4)),Vector((0,0,-1)),.8)
            return q is not None and n.z>.7 and triangles[idx].material_index in road_slots
        distances=[]
        for sign in (-1,1):
            lower=0.;upper=None
            for step in range(1,65):
                distance=step*.25
                if not pavement(sign*distance):upper=distance;break
                lower=distance
            if upper is None:
                distances.append(None);station['issues'].append('boundary_not_found_within_16m');continue
            for _ in range(4):
                mid=(lower+upper)*.5
                if pavement(sign*mid):lower=mid
                else:upper=mid
            distances.append((lower+upper)*.5)
        station.update({'position':list(center),'left_from_osm_axis_m':distances[0],'right_from_osm_axis_m':distances[1],'lateral_slope':slope})
        if all(d is not None for d in distances):station['width_m']=sum(distances)
        if abs(slope)>.15:station['issues'].append('crossfall_review')
        counts['stations_measured' if station['width_m'] is not None else 'stations_unresolved']+=1
        record['stations'].append(station)
    values=[p['width_m'] for p in record['stations'] if p['width_m'] is not None]
    record['scene_pavement_width_median_m']=statistics.median(values) if values else None
    results.append(record)
report={'schema':'boas/road-width-scene-audit-v1','source':source,'source_sha256_at_read':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'segments':results,'summary':dict(counts),'real_width_verified':False,'geometry_changed':False,'approved':False,'method':'Três estações internas por segmento, transversal ao eixo OSM. Limite pelo material do pavimento autoral e camada local ±0,4 m, passos 0,25 m e bisseção. Raio de busca 16 m por lado. Exclui calçadas com outro material; não identifica meio-fio por levantamento.','limitations':['Interseções e pavimentos contíguos podem ampliar medida; variações e estreitamentos exigem inspeção.','Largura da cena não comprova largura real. Tags OSM são referência, não levantamento.','Não determina quantas faixas cabem nem sentido; não aprova ônibus.']}
out=root/'docs/reports/blender/road_width_scene_b39.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report['summary']))
