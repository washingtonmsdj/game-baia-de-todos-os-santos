"""Corrige os saltos locais de perfil na malha, mantendo os anchors e XY.

Não modifica DEM nem escala Z global. Regulariza somente o corredor recortado
e uma transição exterior de dois metros para o terreno preservado.
"""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text())
if c['world_source']['revision'] not in ('R30C.3','R30C.4'):raise RuntimeError('Entrada esperada: revisão da malha particionada')
scene=bpy.context.scene;source=scene.objects[c['export']['road_object']];game=bpy.data.collections['41 GAMEPLAY | URBAN SLICE'];road=next(o for o in game.objects if o['boas_role']=='road');walk=next(o for o in game.objects if o['boas_role']=='walkable')
config_path=root/'prototypes/threejs-water-lab/public/data/urban_slice.json';config=json.loads(config_path.read_text());graph=json.loads((root/c['staging']['roads']).read_text());ways={w['osm_way_id']:w for w in graph['ways']};edges={e['id']:e for e in graph['edges']}
if c['world_source']['revision']=='R30C.4':
    # The prior candidate read an unlinked library object's stale world matrix.
    # Restore only these three meshes from the preserved partition before fitting.
    with bpy.data.libraries.load(str(root/'blender/salvador_lacerda_mvp_r30c3_terrain_partition.blend'),link=False) as (src,dst):dst.objects=[o.name for o in (source,road,walk)]
    for saved,active in zip(dst.objects,(source,road,walk)):
        active.data=saved.data.copy();bpy.data.objects.remove(saved,do_unlink=True)
# Read the preserved uncut mesh to retain its nodal height anchors/materials.
with bpy.data.libraries.load(str(root/'blender/salvador_lacerda_mvp_r30c2_urban_slice.blend'),link=False) as (src,dst):dst.objects=[source.name]
original=dst.objects[0]
if original.parent:raise RuntimeError('Fonte com ancestral exige carregar dependências explicitamente')
scene.collection.objects.link(original);bpy.context.view_layer.update()
original.data.calc_loop_triangles();tris=list(original.data.loop_triangles);tree=BVHTree.FromPolygons([original.matrix_world@v.co for v in original.data.vertices],[list(t.vertices) for t in tris],all_triangles=True)
def original_height(x,y):
    p=tree.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)[0]
    if p is None:raise RuntimeError('Fonte de altura ausente')
    return p.z
for f in source.data.polygons:
    nearest=tree.find_nearest(source.matrix_world@f.center)
    if nearest:f.material_index=tris[nearest[2]].material_index
segments=[];seen=set();anchors={}
for route in config['routes']:
    for id,p in zip(route['node_ids'],route['points']):anchors[id]=original_height(p[0],-p[2])
    for i,(a,b) in enumerate(zip(route['points'],route['points'][1:])):
        edge=edges[route['edge_ids'][i]]
        if edge['id'] in seen:continue
        seen.add(edge['id']);width=ways[edge['osm_way_id']].get('width_m_tagged') or (6.4 if ways[edge['osm_way_id']]['highway']=='secondary' else 4.2)
        p=Vector((a[0],-a[2],anchors[route['node_ids'][i]]));q=Vector((b[0],-b[2],anchors[route['node_ids'][i+1]]));segments.append((p,q,width))
def profile(x,y):
    values=[]
    for a,b,width in segments:
        dx=b.x-a.x;dy=b.y-a.y;length2=dx*dx+dy*dy;t=max(0,min(1,((x-a.x)*dx+(y-a.y)*dy)/length2));dist=math.hypot(x-a.x-dx*t,y-a.y-dy*t);values.append((dist,a.z+(b.z-a.z)*t,width))
    values.sort();nearest=values[0];local=[v for v in values if v[0]<=nearest[0]+2.0]
    weights=[1/max(v[0],.001)**2 for v in local];z=sum(v[1]*w for v,w in zip(local,weights))/sum(weights)
    envelope=min(v[0]-(v[2]/2+1.7) for v in values)
    return z,envelope
a,b=config['crossing']['points'];center=Vector(((a[0]+b[0])/2,-(a[2]+b[2])/2,0));normal=Vector((a[0]-b[0],-(a[2]-b[2]),0)).normalized();forward=Vector((-normal.y,normal.x,0))
def curb_raise(p):
    d=p-center;along=abs(d.dot(forward));across=abs(d.dot(normal))
    longitudinal=max(0,min(1,(along-1.6)/.4));across_raise=max(0,min(1,(across-3.05)/1.95))
    return .12*max(longitudinal,across_raise)
maxdelta=0;modified=0
for o in [road,walk]:
    for v in o.data.vertices:
        p=o.matrix_world@v.co;z,_=profile(p.x,p.y);target=z+(curb_raise(p) if o==walk else 0);maxdelta=max(maxdelta,abs(p.z-target));v.co.z=target;modified+=1
    o.data.update();o['boas_grade_method']='ADAPT_LOCAL: perfil dos nós OSM sobre fonte autoral, transições locais contínuas; sem escala global'
# Keep terrain boundary heights identical to adjacent road/walkway, then blend
# smoothly into the untouched surface outside the corridor.
low_x=min(min(a.x,b.x)-w/2-3.7 for a,b,w in segments);high_x=max(max(a.x,b.x)+w/2+3.7 for a,b,w in segments);low_y=min(min(a.y,b.y)-w/2-3.7 for a,b,w in segments);high_y=max(max(a.y,b.y)+w/2+3.7 for a,b,w in segments)
for v in source.data.vertices:
    p=source.matrix_world@v.co
    if p.z<55 or not (low_x<=p.x<=high_x and low_y<=p.y<=high_y):continue
    z,distance=profile(p.x,p.y)
    if distance>2:continue
    original_z=original_height(p.x,p.y);weight=1-max(0,min(1,distance/2));weight=weight*weight*(3-2*weight)
    target=original_z+(z-original_z)*weight;v.co.z=target;maxdelta=max(maxdelta,abs(p.z-target));modified+=1
source.data.update();bpy.data.objects.remove(original,do_unlink=True)
curb=scene.objects['SLICE | guias da malha particionada'];bm=bmesh.new();bm.from_mesh(walk.data);vs=[];fs=[]
# Horizontal coverage index: barycentric tests in double precision avoid BVH
# edge-ray cancellation on clipped slivers. Used for boundaries and QA.
def index_surface(o):
    o.data.calc_loop_triangles();grid={};size=4
    for t in o.data.loop_triangles:
        a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];den=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
        if abs(den)<1e-10:continue
        lengths=[(b-c).to_2d().length,(a-c).to_2d().length,(a-b).to_2d().length]
        tri=(a,b,c,den,lengths)
        for x in range(math.floor(min(a.x,b.x,c.x)/size),math.floor(max(a.x,b.x,c.x)/size)+1):
            for y in range(math.floor(min(a.y,b.y,c.y)/size),math.floor(max(a.y,b.y,c.y)/size)+1):grid.setdefault((x,y),[]).append(tri)
    def sample(x,y,tolerance=.0001):
        found=[]
        for a,b,c,den,lengths in grid.get((math.floor(x/size),math.floor(y/size)),[]):
            u=((b.y-c.y)*(x-c.x)+(c.x-b.x)*(y-c.y))/den;v=((c.y-a.y)*(x-c.x)+(a.x-c.x)*(y-c.y))/den;w=1-u-v;margin=min(k*abs(den)/length for k,length in zip((u,v,w),lengths))
            if margin>=-tolerance:
                # Edge tolerance cannot extrapolate height from a sliver.
                weights=[max(0,k) for k in (u,v,w)];scale=sum(weights)
                found.append((sum(k*p.z for k,p in zip(weights,(a,b,c)))/scale,margin))
        return max(found,key=lambda a:a[1]) if found else None
    return sample
walk_sample=index_surface(walk);road_sample=index_surface(road)
for e in bm.edges:
    if not e.is_boundary:continue
    a,b=[v.co.copy() for v in e.verts];d=b-a;d.z=0
    if d.length<1e-5:continue
    n=Vector((-d.y,d.x,0)).normalized();mid=(a+b)/2
    if all(walk_sample((mid+n*s).x,(mid+n*s).y,0) for s in [-.005,.005]):continue
    # Both sides use the exact same grade function: no upward spikes from
    # intersecting a different terrain triangle with a height ray.
    base=[]
    for p in [a,b]:z,_=profile(p.x,p.y);base.append(Vector((p.x,p.y,z)))
    start=len(vs);vs.extend([tuple(a),tuple(b),tuple(base[1]),tuple(base[0])]);fs.append((start,start+1,start+2,start+3))
bm.free();curb.data.clear_geometry();curb.data.from_pydata(vs,[],fs);curb.data.update()
proxy=scene.objects[c['export']['terrain_proxy']];proxy.data=source.data.copy();proxy.matrix_world=source.matrix_world.copy();proxy['boas_support_source']=source.name
def runtime(p):return [round(p.x,6),round(p.z,6),round(-p.y,6)]
spawn=config['spawn'];hit=walk_sample(spawn[0],-spawn[2])
if not hit:raise RuntimeError('Spawn sem suporte')
spawn[1]=round(hit[0]+.04,6)
for route in config['routes']:
    for p in route['points']:
        hit=road_sample(p[0],-p[2]);
        if not hit:raise RuntimeError('Nó sem suporte')
        p[1]=round(hit[0],6)
for p in config['crossing']['points']:
    hit=walk_sample(p[0],-p[2])
    if hit:p[1]=round(hit[0],6)
for o in scene.objects:
    if o.type=='MESH' and o.name.startswith(('SLICE | faixa pedestre','SLICE | linha parada')):
        for v in o.data.vertices:
            p=o.matrix_world@v.co;hit=road_sample(p.x,p.y)
            if hit:v.co.z=hit[0]+.006
        o.data.update()
samples=0;missing=[];maxgrade=0
for route in config['routes']:
    for a,b in zip(route['points'],route['points'][1:]):
        p=Vector((a[0],-a[2],a[1]));q=Vector((b[0],-b[2],b[1]));d=q-p;d.z=0;length=d.length;n=Vector((-d.y,d.x,0)).normalized();previous=None;steps=math.ceil(length)
        for i in range(steps+1):
            point=p.lerp(q,i/steps)
            for offset in [-1,0,1]:
                r=point+n*offset;hit=road_sample(r.x,r.y);samples+=1
                if not hit:missing.append(runtime(r))
                if offset==0 and hit:
                    if previous is not None:maxgrade=max(maxgrade,abs(hit[0]-previous)/(length/steps))
                    previous=hit[0]
if missing:raise RuntimeError('Sem suporte: '+str(missing))
config['surfaces']=[]
for o in game.objects:
    o.data.calc_loop_triangles();config['surfaces'].append({'name':o.name,'role':o['boas_role'],'positions':[v for p in o.data.vertices for v in runtime(o.matrix_world@p.co)],'indices':[v for t in o.data.loop_triangles for v in t.vertices]})
config['adaptations'].append({'classification':'ADAPT_LOCAL','description':'Perfil de pista derivado das alturas dos nós na malha-fonte; calçada 0,12m com rebaixo e faixa de transição de terreno 2m. Corrige saltos do pavimento; DEM e implantação XY preservados.','width_verified_m':None})
config_path.write_text(json.dumps(config,ensure_ascii=False,separators=(',',':')),encoding='utf8');text=bpy.data.texts.get('BOAS_URBAN_SLICE.json');text.clear();text.write(json.dumps({k:v for k,v in config.items() if k not in ('surfaces','obstacles')},ensure_ascii=False,indent=2));(root/'world/areas/mvp-centro-lacerda/urban_slice.json').write_text(text.as_string(),encoding='utf8')
output=root/'blender/salvador_lacerda_mvp_r30c5_terrain_world_coordinates.blend';bpy.ops.wm.save_as_mainfile(filepath=str(output));c['world_source'].update(file=output.relative_to(root).as_posix(),revision='R30C.5',sha256=hashlib.sha256(output.read_bytes()).hexdigest(),selection_reason='Correção de terreno: partição e perfil derivados em coordenadas mundiais; tráfego em revisão');c['runtime']['world']['spawn']=dict(x=spawn[0],z=spawn[2],headingDeg=0);cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
rp=root/'docs/reports/blender/urban_terrain_partition.json';report=json.loads(rp.read_text(encoding='utf8'));report.update(source=c['world_source'],support_samples=samples,missing_road_samples=0,maximum_centerline_grade=maxgrade,max_local_height_adjustment_m=maxdelta,modified_vertices=modified,terrain_transition_band_m=2,numerical_coverage_tolerance_m=.0001,spawn=spawn,visual_review='pending');rp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
