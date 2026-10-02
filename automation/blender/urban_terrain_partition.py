"""Particiona o chão existente, sem camadas de pista sobrepostas.

As regiões da slice apenas classificam polígonos: a altura vem da própria
triangulação autoral. Cada fragmento pertence a terreno, pista OU passeio.
"""
import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text())
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Fonte ativa incorreta')
if c['world_source']['revision']!='R30C.2':raise RuntimeError('Aplicar uma única vez sobre R30C.2')
scene=bpy.context.scene;source=bpy.data.objects[c['export']['road_object']]
source.data.calc_loop_triangles()
original=[source.matrix_world@v.co for v in source.data.vertices]
tree=BVHTree.FromPolygons(original,[list(t.vertices) for t in source.data.loop_triangles],all_triangles=True)
game=bpy.data.collections['41 GAMEPLAY | URBAN SLICE'];visual=bpy.data.collections['40 VISUAL | URBAN SLICE']
old=[o for o in game.objects if o.get('boas_role') in ('road','walkable','crossing')]
regions=[];grid={};cell=8
for o in old:
    o.data.calc_loop_triangles()
    for t in o.data.loop_triangles:
        ps=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
        area=sum(ps[i].x*ps[(i+1)%3].y-ps[(i+1)%3].x*ps[i].y for i in range(3))
        if abs(area)<1e-8:continue
        if area<0:ps.reverse()
        role='road' if o['boas_role']=='road' else 'walkable'
        bounds=(min(p.x for p in ps),min(p.y for p in ps),max(p.x for p in ps),max(p.y for p in ps))
        item=(ps,role,bounds,o.name);index=len(regions);regions.append(item)
        for x in range(math.floor(bounds[0]/cell),math.floor(bounds[2]/cell)+1):
            for y in range(math.floor(bounds[1]/cell),math.floor(bounds[3]/cell)+1):grid.setdefault((x,y),[]).append(index)
def area(poly):return abs(sum(p.x*poly[(i+1)%len(poly)].y-poly[(i+1)%len(poly)].x*p.y for i,p in enumerate(poly)))/2
def clip(poly,a,b,inside):
    result=[]
    def side(p):return (b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x)
    for i,p in enumerate(poly):
        q=poly[(i+1)%len(poly)];dp=side(p);dq=side(q)
        pp=dp>=-1e-9 if inside else dp<=1e-9
        qq=dq>=-1e-9 if inside else dq<=1e-9
        if pp:result.append(p)
        if pp!=qq and abs(dp-dq)>1e-12:result.append(p.lerp(q,dp/(dp-dq)))
    return result if len(result)>=3 and area(result)>1e-9 else []
def split(poly,region):
    inside=poly;outside=[]
    for a,b in zip(region,region[1:]+region[:1]):
        if not inside:break
        part=clip(inside,a,b,False)
        if part:outside.append(part)
        inside=clip(inside,a,b,True)
    return inside,outside
buffers={role:{'vertices':[],'faces':[],'materials':[],'map':{}} for role in ('terrain','road','walkable')}
def emit(role,poly,material):
    if not poly or area(poly)<1e-8:return
    b=buffers[role];indices=[]
    for p in poly:
        p=p+Vector((0,0,.12 if role=='walkable' else 0));key=tuple(round(v,6) for v in p)
        if key not in b['map']:b['map'][key]=len(b['vertices']);b['vertices'].append(tuple(p))
        indices.append(b['map'][key])
    for i in range(1,len(indices)-1):
        ids=(indices[0],indices[i],indices[i+1])
        if len(set(ids))<3:continue
        p,q,r=[Vector(b['vertices'][j]) for j in ids]
        if (q-p).cross(r-p).length<1e-8:continue
        if (q-p).cross(r-p).z<0:ids=tuple(reversed(ids))
        b['faces'].append(ids);b['materials'].append(material)
affected=0;totalarea={'terrain':0,'road':0,'walkable':0};sourcearea=0
for t in source.data.loop_triangles:
    poly=[original[i] for i in t.vertices];sourcearea+=area(poly)
    bounds=(min(p.x for p in poly),min(p.y for p in poly),max(p.x for p in poly),max(p.y for p in poly))
    # Vertical retaining faces are preserved, never interpreted as road footprints.
    if area(poly)<1e-8:
        b=buffers['terrain'];ids=[]
        for p in poly:
            key=tuple(round(v,6) for v in p)
            if key not in b['map']:b['map'][key]=len(b['vertices']);b['vertices'].append(tuple(p))
            ids.append(b['map'][key])
        b['faces'].append(tuple(ids));b['materials'].append(t.material_index);continue
    candidates=set()
    for x in range(math.floor(bounds[0]/cell),math.floor(bounds[2]/cell)+1):
        for y in range(math.floor(bounds[1]/cell),math.floor(bounds[3]/cell)+1):candidates.update(grid.get((x,y),[]))
    candidates=[i for i in candidates if not (regions[i][2][2]<bounds[0] or regions[i][2][0]>bounds[2] or regions[i][2][3]<bounds[1] or regions[i][2][1]>bounds[3])]
    candidates.sort(key=lambda i:regions[i][1]!='road')
    remaining=[poly]
    for index in candidates:
        region,role,bb,name=regions[index];nextparts=[]
        for part in remaining:
            if min(p.z for p in part)<55:nextparts.append(part);continue
            inside,outside=split(part,region)
            if inside:emit(role,inside,t.material_index);totalarea[role]+=area(inside);affected+=1
            nextparts.extend(outside)
        remaining=nextparts
        if not remaining:break
    for part in remaining:emit('terrain',part,t.material_index);totalarea['terrain']+=area(part)
if abs(sum(totalarea.values())-sourcearea)>.02:raise RuntimeError('Particionamento perdeu ou duplicou área')
def write_mesh(o,b):
    me=bpy.data.meshes.new(o.name+' | malha contínua');me.from_pydata(b['vertices'],[],b['faces']);me.update();oldmesh=o.data;o.data=me
    if oldmesh.users==0:bpy.data.meshes.remove(oldmesh)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    return me
materials=list(source.data.materials);source.matrix_world.identity();me=write_mesh(source,buffers['terrain'])
for m in materials:me.materials.append(m)
# Material indices must be assigned before cleaning when topology is unchanged.
for p,m in zip(me.polygons,buffers['terrain']['materials']):p.material_index=m
created=[]
for role,material in [('road',bpy.data.materials['SLICE | pavimento']),('walkable',bpy.data.materials['SLICE | passeio de pedra'])]:
    o=bpy.data.objects.new('SLICE | '+role+' | superfície particionada',bpy.data.meshes.new('placeholder'));visual.objects.link(o);game.objects.link(o);write_mesh(o,buffers[role]);o.data.materials.append(material);o['boas_role']=role;o['boas_area_id']=c['area_id'];o['boas_source']=source.name;o['boas_adaptation']='ADAPT_LOCAL: classificação da malha-fonte, passeio elevado 0,12m; largura não levantada';created.append(o)
    if role=='walkable':
        # Actual vertical curb/fascia closes raised sidewalks, not a cover panel.
        bm=bmesh.new();bm.from_mesh(o.data);boundary=[e for e in bm.edges if e.is_boundary];vs=[];fs=[]
        for e in boundary:
            a,b=[v.co.copy() for v in e.verts];base=len(vs);vs.extend([tuple(a),tuple(b),tuple(b-Vector((0,0,.12))),tuple(a-Vector((0,0,.12)))]);fs.append((base,base+1,base+2,base+3))
        bm.free();m=bpy.data.meshes.new('Guias da superfície');m.from_pydata(vs,[],fs);m.update();curb=bpy.data.objects.new('SLICE | guias da malha particionada',m);visual.objects.link(curb);m.materials.append(material)
for o in old:bpy.data.objects.remove(o,do_unlink=True)
# Collider mirrors the actual repaired terrain rather than the obsolete proxy.
proxy=bpy.data.objects[c['export']['terrain_proxy']];proxy.data=source.data.copy();proxy.matrix_world=source.matrix_world.copy();proxy['boas_support_source']=source.name
config_path=root/'prototypes/threejs-water-lab/public/data/urban_slice.json';config=json.loads(config_path.read_text());config['surfaces']=[]
def runtime(p):return [round(p.x,6),round(p.z,6),round(-p.y,6)]
for o in created:
    o.data.calc_loop_triangles();config['surfaces'].append({'name':o.name,'role':o['boas_role'],'positions':[v for p in o.data.vertices for v in runtime(o.matrix_world@p.co)],'indices':[v for t in o.data.loop_triangles for v in t.vertices]})
config['status']='terrain_review';config['adaptations'].append({'classification':'ERROR','description':'Removidas sobreposições. Terreno/pista/passeio particionados a partir dos mesmos triângulos e alturas, sem offset da pista.'})
config_path.write_text(json.dumps(config,ensure_ascii=False,separators=(',',':')),encoding='utf8')
output=root/'blender/salvador_lacerda_mvp_r30c3_terrain_partition.blend';bpy.ops.wm.save_as_mainfile(filepath=str(output));c['world_source'].update(file=output.relative_to(root).as_posix(),revision='R30C.3',sha256=hashlib.sha256(output.read_bytes()).hexdigest(),selection_reason='Correção de sobreposição: chão particionado sobre a malha-fonte; gameplay ainda em revisão');c['runtime']['world']['spawn']=c['runtime']['spawn'];cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report={'source':c['world_source'],'classification':'ERROR','affected_fragments':affected,'projected_area_before_m2':sourcearea,'partition_area_m2':totalarea,'area_error_m2':abs(sum(totalarea.values())-sourcearea),'road_vertical_offset_m':0,'sidewalk_raise_m':.12,'geography_xy_changed':False,'dem_changed':False,'scope':'somente terreno e malha da slice; tráfego suspenso para revisão'}
(root/'docs/reports/blender/urban_terrain_partition.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
