"""Corrige retornos antigos e pontas da espessura na oficina visível V13."""
import bpy, bmesh, math, json, hashlib, collections
from pathlib import Path
from mathutils import Vector

r=Path(__file__).resolve().parents[2];s=bpy.context.scene
out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v13.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert not s.get('boas_v13_finish_applied')
o=s.objects['HILUX | CARROCERIA PRINCIPAL']
checkpoint=r/'artifacts/vehicles/rondesp/pre-v13-finish.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
members=collections.defaultdict(set)
for v in o.data.vertices:
    for g in v.groups:members[g.group].add(v.index)
def ids(fragment):
    return set().union(*(members[g.index] for g in o.vertex_groups if fragment in g.name))
def boundary(fragment):
    vi=ids(fragment);counts=collections.Counter()
    for p in o.data.polygons:
        if all(i in vi for i in p.vertices):
            v=list(p.vertices)
            for a,b in zip(v,v[1:]+v[:1]):counts[tuple(sorted((a,b)))]+=1
    return [o.data.vertices[i].co.copy() for i in sorted({i for e,n in counts.items() if n==1 for i in e})]
roof={}
for p in boundary('Teto curvatura dupla'):
    if p.x>.5:
        key=round(p.y,6)
        if key not in roof or p.x>roof[key].x:roof[key]=p
roof_side=sorted(roof.values(),key=lambda p:p.y)
rear_wall_edges=boundary('Painel posterior com vão do vidro')
rear_top=[p for p in rear_wall_edges if p.z>1.755 and p.z>1.785-.024*(p.x/.708)**4-.001]
rear_top.sort(key=lambda p:p.x)
arch=[]
for fragment,cy in [('Para-lama dianteiro 1',-1.43),('Lateral caçamba 1',1.655)]:
    pts=boundary(fragment)
    # Menor Z por estação identifica o recorte de roda da própria chapa.
    rows={}
    for p in pts:
        if cy-.53<=p.y<=cy+.53 and p.z<1.0:
            key=round(p.y,5)
            if key not in rows or p.z<rows[key].z:rows[key]=p
    arch.append((fragment,sorted(rows.values(),key=lambda p:p.y)))

remove=['Calha fixa 1','Coluna B 1','Caixa interna roda (1, -1.43)',
        'Retorno caixa roda (-1.43, 1)','Retorno caixa roda (1.655, 1)']
sets=[ids(f) for f in remove]
bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
faces=[f for f in bm.faces if any(all(v.index in vi for v in f.verts) for vi in sets)]
removed=len(faces)
bmesh.ops.delete(bm,geom=faces,context='FACES')
deform=bm.verts.layers.deform.verify()
mat=list(o.data.materials).index(bpy.data.materials['RDP01 | Pintura marrom Rondesp'])
new=[]
def patch(name,vs,fs,normal):
    group=o.vertex_groups.new(name='HILUX13 | '+name);new.append(group.name)
    vv=[bm.verts.new(Vector(p)) for p in vs]
    for v in vv:v[deform][group.index]=1.
    for indices in fs:
        try:f=bm.faces.new([vv[i] for i in indices])
        except ValueError:continue
        f.normal_update()
        if f.normal.dot(Vector(normal))<0:f.normal_flip()
        f.material_index=mat;f.smooth=True
    return vv
def strip(name,rows,normal):
    nv=len(rows[0]);return patch(name,[p for row in rows for p in row],
        [(i*nv+j,(i+1)*nv+j,(i+1)*nv+j+1,i*nv+j+1) for i in range(len(rows)-1) for j in range(nv-1)],normal)
def linear(nodes,x):
    if x<=nodes[0][0]:return nodes[0][1]
    if x>=nodes[-1][0]:return nodes[-1][1]
    for a,b in zip(nodes,nodes[1:]):
        if a[0]<=x<=b[0]:return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])

# Remover o perímetro reaproveitado das portas: ele atravessava a nova coluna C.
# O retorno novo acompanha exatamente as estações da borda real do teto.
strip('Retorno continuo da borda do teto',[
    [p+Vector((.009*math.sin(math.pi*j/12),0,-.018*(1-math.cos(math.pi*j/12)))) for j in range(7)]
    for p in roof_side],(1,0,1))
if len(rear_top)>2:
    strip('Encontro teto painel posterior',[[p,Vector((p.x,1.105,p.z))] for p in rear_top],(0,0,1))

# Coluna B simples, com encontros suaves e batentes curtos voltados para a cabine.
rows=[]
for i in range(65):
    z=.488+(1.780-.488)*i/64
    x=linear([(.488,.827),(.8,.883),(1.10,.87),(1.29,.813),(1.5,.777),(1.68,.737),(1.78,.710)],z)
    rows.append([(x-.007*(1-math.cos(math.pi*j/12)),.175-.057*math.cos(math.pi*j/12),z) for j in range(13)])
strip('Coluna B com cantos arredondados',rows,(1,0,0))
for side in [-1,1]:
    strip('Retorno batente B '+str(side),[[Vector(row[0 if side<0 else -1]),Vector(row[0 if side<0 else -1])+Vector((-.026,0,0))] for row in rows],(0,side,0))

# Lábios dos recortes usam o próprio arco, sem descer chapas independentes abaixo dele.
for label,pts in arch:
    strip('Retorno recorte '+label,[[p+Vector((-.026*j/8,0,-.002*math.sin(math.pi*j/8))) for j in range(9)] for p in pts],(0,0,-1))

# Normal contínua e espessura constante evitam a amplificação em vértices de quina.
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00008)
bad=[f for f in bm.faces if f.calc_area()<1e-9]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.normal_update();bm.to_mesh(o.data);bm.free();o.data.update()
thick=next(m for m in o.modifiers if m.type=='SOLIDIFY')
thick.use_even_offset=False;thick.use_quality_normals=False;thick.thickness=.0025;thick.offset=0.
thick.thickness_clamp=1.;thick.show_viewport=True;thick.show_render=True
s['boas_v13_finish_applied']=True
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.shading.show_shadows=False
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
rp=r/'docs/reports/blender/hilux_carroceria_v13.json';report=json.loads(rp.read_text(encoding='utf-8'))
report['finish']={'removed_components':remove,'removed_faces':removed,'new_components':new,'sheet_thickness_candidate_m':.0025,'constant_thickness':True}
report['base_vertices']=len(o.data.vertices);report['base_faces']=len(o.data.polygons)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();report['source_reopened']=False;report['visual_review']='pending'
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf-8'));data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return None
bpy.app.timers.register(reopen,first_interval=.5)
