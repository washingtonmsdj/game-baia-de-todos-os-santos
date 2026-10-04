"""V14: continuidade dos vãos, flanges frontais e encontro da tampa da caçamba.

Somente sessão visível. Contornos autorais candidatos; V13 e peças reservadas
preservadas. As faces são identificadas por boas_panel_id, não por nome parecido.
"""
import ast,bpy,bmesh,math,json,hashlib,collections
from pathlib import Path
from mathutils import Vector

r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cat=json.loads((r/'world/vehicles/catalog.json').read_text(encoding='utf-8'))
vehicle=next(v for v in cat['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')
source=r/vehicle['authoring_base']['file'];out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v14.blend'
assert not bpy.app.background and source.name=='hilux_carroceria_v13.blend'
assert Path(bpy.data.filepath).resolve()==source.resolve() and not out.exists()
assert hashlib.sha256(source.read_bytes()).hexdigest()==vehicle['authoring_base']['sha256']
o=s.objects['HILUX | CARROCERIA PRINCIPAL']
checkpoint=r/'artifacts/vehicles/rondesp/pre-v14-visible-session.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
for filename,functions in [('rebuild_hilux_reference_v06.py',{'interp','sidewidth','arch'}),('refine_hilux_body_v09.py',{'upper','hermite'})]:
    tree=ast.parse((r/'automation/blender'/filename).read_text(encoding='utf-8'))
    for fn in tree.body:
        if isinstance(fn,ast.FunctionDef) and fn.name in functions:
            exec(compile(ast.Module(body=[fn],type_ignores=[]),filename,'exec'),globals())
attr=o.data.attributes['boas_panel_id'];labels=json.loads(o['boas_panel_id_map'])
def panel_id(name):return next(int(k) for k,v in labels.items() if v==name)
def edge_ids(name):
    pid=panel_id(name);counts=collections.Counter();direct={}
    for p in o.data.polygons:
        if attr.data[p.index].value!=pid:continue
        vv=list(p.vertices)
        for a,b in zip(vv,vv[1:]+vv[:1]):
            key=tuple(sorted((a,b)));counts[key]+=1;direct[key]=(a,b)
    return [direct[k] for k,n in counts.items() if n==1]
def edges(name):return [(o.data.vertices[a].co.copy(),o.data.vertices[b].co.copy()) for a,b in edge_ids(name)]
def linear(nodes,x):
    if x<=nodes[0][0]:return nodes[0][1]
    if x>=nodes[-1][0]:return nodes[-1][1]
    for a,b in zip(nodes,nodes[1:]):
        if a[0]<=x<=b[0]:return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

fascia=edges('HILUX06 | Para-choque e testa esculpidos')
fascia_ids=edge_ids('HILUX06 | Para-choque e testa esculpidos')
adj=collections.defaultdict(list)
for a,b in fascia_ids:adj[a].append(b);adj[b].append(a)
seen=set();rings=[]
for start in adj:
    if start in seen:continue
    ring=[];prev=None;cur=start
    while cur not in seen:
        seen.add(cur);ring.append(cur)
        candidates=[i for i in adj[cur] if i!=prev]
        if not candidates:break
        prev,cur=cur,candidates[0]
    rings.append([o.data.vertices[i].co.copy() for i in ring])
lamp_ring=next(loop for loop in rings if min(p.x for p in loop)>.50 and min(p.z for p in loop)>.98)
lamp_keys={tuple(round(c,6) for c in p) for p in lamp_ring}
lamp_edges=[(a,b) for a,b in fascia if tuple(round(c,6) for c in a) in lamp_keys and tuple(round(c,6) for c in b) in lamp_keys]
mask_edges=[(a,b) for a,b in fascia if min(a.z,b.z)>.592 and max(a.z,b.z)<1.130 and max(a.x,b.x)<.60 and min(a.x,b.x)>1e-6]
c_front={}
for a,b in edges('HILUX13 | Coluna C e canto posterior'):
    for p in (a,b):
        k=round(p.z,6)
        if k not in c_front or p.y<c_front[k].y:c_front[k]=p
c_front=sorted(c_front.values(),key=lambda p:p.z)

# Suavizar a seção B sem engrossar nem mudar os vãos das portas.
old_nodes=[(.488,.827),(.8,.883),(1.10,.87),(1.29,.813),(1.5,.777),(1.68,.737),(1.78,.710)]
new_nodes=old_nodes[:-1]+[(1.78,.705)]
b_ids={panel_id(n) for n in ['HILUX13 | Coluna B com cantos arredondados','HILUX13 | Retorno batente B -1','HILUX13 | Retorno batente B 1']}
b_verts={i for p in o.data.polygons if attr.data[p.index].value in b_ids for i in p.vertices}
for i in b_verts:
    v=o.data.vertices[i];v.co.x+=interp(new_nodes,v.co.z)-linear(old_nodes,v.co.z)

# A tampa acompanha a largura real da borda lateral em cada altura, com junta.
bed_tail=[]
for a,b in edges('HILUX06 | Lateral caçamba 1'):
    for p in (a,b):
        if p.y>2.73:bed_tail.append(p)
width_nodes=[(.535,.800),(.62,.825),(.69,.831),(.80,.820),(.90,.817),(1.03,.839),(1.16,.849),(1.24,.828),(1.285,.799)]
def gate_width(z):return interp(width_nodes,z)-.004
gate_id=panel_id('HILUX06 | Tampa caçamba')
gate_verts={i for p in o.data.polygons if attr.data[p.index].value==gate_id for i in p.vertices}
for i in gate_verts:
    v=o.data.vertices[i];v.co.x*=gate_width(v.co.z)/.839

replace=['HILUX06 | Para-lama dianteiro 1','HILUX13 | Retorno recorte Para-lama dianteiro 1',
         'HILUX09 | Retorno farol 1','HILUX13 | Retorno dianteiro sem chapas duplicadas',
         'HILUX06 | Soleira 1','HILUX13 | Face interna tampa caçamba','HILUX13 | Retorno superior tampa caçamba']
retired={panel_id(n) for n in replace}|{0}
bm=bmesh.new();bm.from_mesh(o.data);fl=bm.faces.layers.int.get('boas_panel_id')
assert fl is not None
remove=[f for f in bm.faces if f[fl] in retired]
removed=len(remove);bmesh.ops.delete(bm,geom=remove,context='FACES')
deform=bm.verts.layers.deform.verify()
mat=list(o.data.materials).index(bpy.data.materials['RDP01 | Pintura marrom Rondesp'])
new=[]
def patch(name,vs,fs,normal=None):
    g=o.vertex_groups.new(name='HILUX14 | '+name);new.append(g.name);labels[str(g.index+1)]=g.name
    vv=[bm.verts.new(Vector(p)) for p in vs]
    for v in vv:v[deform][g.index]=1.
    for indices in fs:
        try:f=bm.faces.new([vv[k] for k in indices])
        except ValueError:continue
        f.normal_update()
        if normal is not None and f.normal.dot(Vector(normal))<0:f.normal_flip()
        f[fl]=g.index+1;f.material_index=mat;f.smooth=True
    return vv
def strip(name,rows,normal=None):
    nv=len(rows[0]);return patch(name,[p for row in rows for p in row],
        [(i*nv+j,(i+1)*nv+j,(i+1)*nv+j+1,i*nv+j+1) for i in range(len(rows)-1) for j in range(nv-1)],normal)

# O recorte da roda chega à soleira, enquanto o ombro mantém a borda do capô.
rows=[];low_edge=[];fore_edge=[];aft_edge=[]
for i in range(67):
    u=i/66;top=upper(u,1);shift=.080*smooth((u-.70)/.30)
    bottom_y=top.y+shift;low=arch(bottom_y,-1.43);row=[]
    for j in range(41):
        t=j/40;y=top.y+shift*(1-t)**4;z=low+(top.z-low)*t
        co=Vector((sidewidth(y,z),y,z))
        if t>.66:
            zj=low+(top.z-low)*.66;yj=top.y+shift*(1-.66)**4
            a=Vector((sidewidth(yj,zj),yj,zj));near=upper(u,.998)
            length=max((top-a).length,.025)
            co=hermite(a,top,Vector((0,0,length)),(near-top).normalized()*length,(t-.66)/.34)
        row.append(co)
    rows.append(row);low_edge.append(row[0])
fore_edge=rows[0];aft_edge=rows[-1]
strip('Para-lama continuo ate soleira',rows,(1,0,0))
strip('Retorno recorte dianteiro',[[p+Vector((-.026*j/8,0,-.002*math.sin(math.pi*j/8))) for j in range(9)] for p in low_edge],(0,0,-1))

def fascia_at(z):
    hits=[]
    for a,b in fascia:
        if abs(a.z-b.z)>1e-9 and min(a.z,b.z)<=z<=max(a.z,b.z):hits.append(a.lerp(b,(z-a.z)/(b.z-a.z)))
    return max(hits,key=lambda p:p.x) if hits else min((p for e in fascia for p in e),key=lambda p:abs(p.z-z))
strip('Retorno frontal alinhado ao para-lama',[[fascia_at(p.z).lerp(p,j/8) for j in range(9)] for p in fore_edge],(1,0,0))
# Chapa curta no batente A: substitui a tira solta que ficava dentro do vão.
aft_edge=aft_edge+[Vector((.837,-.981,1.322))]
strip('Batente A integrado ao para-lama',[[p+Vector((-.030*j/8,.002*math.sin(math.pi*j/8),0)) for j in range(9)] for p in aft_edge],(0,1,0))
strip('Batente C com retorno interno',[[p+Vector((-.025*j/8,-.002*math.sin(math.pi*j/8),0)) for j in range(9)] for p in c_front],(0,-1,0))
# Soleira com retorno ligado à borda do piso, sem abas penduradas.
profile=[(.793,.485),(.808,.490),(.823,.496),(.830,.494),(.831,.480),(.824,.466),(.810,.465)]
ys=sorted(set([-.895,1.080,.118,.232,1.060]+[-.895+1.975*i/64 for i in range(65)]))
strip('Soleira dobrada e retorno do piso',[[(x,y,z) for x,z in profile] for y in ys],(1,0,0))
strip('Ligacao dianteira soleira batente',[[Vector((.831,-.895,.488)),aft_edge[0]],[Vector((.793,-.895,.485)),aft_edge[0]+Vector((-.030,0,0))]],(0,0,1))

# Flanges curtas dos encaixes: preservam a abertura e dão espessura à chapa.
for name,es,depth in [('Encaixe farol com flange',lamp_edges,.018),('Encaixe grade com flange',mask_edges,.026)]:
    vs=[];fs=[]
    for a,b in es:
        k=len(vs);vs.extend([a,b,b+Vector((0,depth,0)),a+Vector((0,depth,0))]);fs.append((k,k+1,k+2,k+3))
    patch(name,vs,fs)

# Lado interno da tampa e lábios superior/lateral têm a mesma seção da chapa externa.
zr=[.535+(1.285-.535)*i/40 for i in range(41)]
gate_rows=[[(gate_width(z)*u/40,2.789-.045*(u/40)**4,z) for u in range(41)] for z in zr]
inner_rows=[[(max(.001,gate_width(z)-.025)*u/40,2.738,z) for u in range(41)] for z in zr]
strip('Face interna tampa alinhada',inner_rows,(0,-1,0))
strip('Dobra lateral tampa',[[gate_rows[i][-1],inner_rows[i][-1]] for i in range(len(zr))],(1,0,0))
strip('Dobra inferior tampa',[[gate_rows[0][i],inner_rows[0][i]] for i in range(41)],(0,0,-1))
strip('Borda superior tampa arredondada',[
    [Vector(inner_rows[-1][i]).lerp(Vector(gate_rows[-1][i]),j/12)+Vector((0,0,.004*math.sin(math.pi*j/12))) for j in range(13)] for i in range(41)],(0,0,1))

bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00006)
bad=[f for f in bm.faces if f.calc_area()<1e-10]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.normal_update();bm.to_mesh(o.data);bm.free();o.data.update()
o['boas_panel_id_map']=json.dumps(labels,ensure_ascii=False)
o['boas_v14_changes']='Vãos A/C, transição para-lama/soleira, flanges farol/grade, seção B suave e tampa da caçamba.'
s.name='HILUX | carroceria isolada v14';s['boas_revision_parent']=source.relative_to(r).as_posix();s['boas_v14_applied']=True
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.color_type='OBJECT';sp.shading.show_shadows=False;sp.shading.show_cavity=False
            sp.region_3d.view_rotation=(Vector((0,.12,1.1))-Vector((7,-8,3.8))).to_track_quat('-Z','Y')
            sp.region_3d.view_location=(0,.12,1.1);sp.region_3d.view_distance=5.8
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
report={'asset_id':'vehicle-rondesp-pickup','file':out.relative_to(r).as_posix(),'scene':s.name,'parent':source.relative_to(r).as_posix(),
    'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'candidate','authoring_mode':'body_only','body_mesh':o.name,
    'removed_components':replace+['batente A sem identificação'],'removed_faces':removed,'new_components':new,
    'base_vertices':len(o.data.vertices),'base_faces':len(o.data.polygons),'visible_meshes':[ob.name for ob in s.objects if ob.type=='MESH' and ob.visible_get()],
    'source_reopened':False,'visual_review':'pending','runtime_exported':False,'rig_applied':False,
    'reference_ids':['hilux-2024-std-dealer-side','hilux-std-stock-front','hilux-srx-user-rear'],
    'notes':['Seções, flanges e juntas são parâmetros autorais candidatos, não medidas de fábrica.','Peças reservadas preservadas; sem npm, testes, build, exportação runtime ou commit.','boas_panel_id preserva a identidade das faces após a solda.']}
rp=r/'docs/reports/blender/hilux_carroceria_v14.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf-8'));data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return None
bpy.app.timers.register(reopen,first_interval=.5)
