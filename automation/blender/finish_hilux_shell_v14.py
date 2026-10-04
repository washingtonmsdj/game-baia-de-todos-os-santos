"""Acabamento da coluna A e extremidades inferiores da caçamba, sessão visível."""
import ast,bpy,bmesh,math,json,hashlib,collections
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;o=s.objects['HILUX | CARROCERIA PRINCIPAL']
out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v14.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert not s.get('boas_v14_finish_applied')
checkpoint=r/'artifacts/vehicles/rondesp/pre-v14-finish.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
for fn in ast.parse((r/'automation/blender/rebuild_hilux_reference_v06.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name in {'interp','sidewidth'}:
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'secoes-v06','exec'),globals())
labels=json.loads(o['boas_panel_id_map']);attr=o.data.attributes['boas_panel_id']
def pid(name):return next(int(k) for k,v in labels.items() if v==name)
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

# A ponta inferior era uma quebra brusca da deformação de canto da V11.
# Subir a linha inferior atrás da roda e continuar a mesma seção lateral.
bed_id=pid('HILUX06 | Lateral caçamba 1')
vi={i for p in o.data.polygons if attr.data[p.index].value==bed_id for i in p.vertices}
count=0
for i in vi:
    v=o.data.vertices[i];x,y,z=v.co
    if y<=2.18:continue
    dz=.050*smooth((y-2.18)/.56)*(1-smooth((z-.485)/.42))
    v.co.z+=dz;v.co.x+=sidewidth(y,z+dz)-sidewidth(y,z)
    if y>2.70:
        blend=smooth((y-2.70)/.045)
        target=2.745+.004*smooth((v.co.z-.535)/.75)
        v.co.y=y*(1-blend)+target*blend
    count+=1

# Remover a lâmina estreita anterior e dar largura em Y/Z à coluna A.
a_id=pid('HILUX06 | Montante A curvo 1')
bm=bmesh.new();bm.from_mesh(o.data);fl=bm.faces.layers.int.get('boas_panel_id')
faces=[f for f in bm.faces if f[fl]==a_id];removed=len(faces)
bmesh.ops.delete(bm,geom=faces,context='FACES')
deform=bm.verts.layers.deform.verify();mat=list(o.data.materials).index(bpy.data.materials['RDP01 | Pintura marrom Rondesp'])
new=[]
def patch(name,vs,fs,normal):
    g=o.vertex_groups.new(name='HILUX14 | '+name);new.append(g.name);labels[str(g.index+1)]=g.name
    vv=[bm.verts.new(Vector(p)) for p in vs]
    for v in vv:v[deform][g.index]=1.
    for inds in fs:
        try:f=bm.faces.new([vv[i] for i in inds])
        except ValueError:continue
        f.normal_update()
        if f.normal.dot(Vector(normal))<0:f.normal_flip()
        f[fl]=g.index+1;f.material_index=mat;f.smooth=True
def strip(name,rows,normal):
    n=len(rows[0]);patch(name,[p for row in rows for p in row],
        [(i*n+j,(i+1)*n+j,(i+1)*n+j+1,i*n+j+1) for i in range(len(rows)-1) for j in range(n-1)],normal)

a_rows=[]
for i in range(49):
    t=i/48
    front=Vector((.803*(1-t)+.705*t,-.970*(1-t)-.338*t,1.326*(1-t)+1.767*t))
    outer=Vector((.839*(1-t)+.717*t,front.y+.022+.040*smooth(t),1.322*(1-t)+1.771*t))
    a_rows.append([front.lerp(outer,j/12)+Vector((.006*math.sin(math.pi*j/12),0,0)) for j in range(13)])
strip('Montante A com largura de chapa',a_rows,(1,-.3,.2))
strip('Retorno interno montante A',[[row[-1]+Vector((-.025*j/8,.002*math.sin(math.pi*j/8),0)) for j in range(9)] for row in a_rows],(0,1,0))
strip('Pe montante A junto ao cowl',[
    [Vector((.807+.030*j/12,-.981,1.322)) for j in range(13)],a_rows[0]],(0,0,1))

# O lado da caçamba termina com dobra para dentro; não há aba triangular livre.
# As estações acompanham a linha inferior elevada, sem alterar o recorte de roda.
bed_count=collections.Counter();direct={}
for f in bm.faces:
    if f[fl]!=bed_id:continue
    vv=list(f.verts)
    for a,b in zip(vv,vv[1:]+vv[:1]):
        key=frozenset((a,b));bed_count[key]+=1;direct[key]=(a,b)
bottom=[]
for key,n in bed_count.items():
    a,b=direct[key]
    if n==1 and min(a.co.y,b.co.y)>2.18 and max(a.co.z,b.co.z)<.60:
        bottom.append((a.co.copy(),b.co.copy()))
vs=[];fs=[]
for a,b in bottom:
    k=len(vs);vs.extend([a,b,b+Vector((-.020,0,.008)),a+Vector((-.020,0,.008))]);fs.append((k,k+1,k+2,k+3))
patch('Dobra inferior cantos cacamba',vs,fs,(0,0,-1))
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00006)
bad=[f for f in bm.faces if f.calc_area()<1e-10]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.normal_update();bm.to_mesh(o.data);bm.free();o.data.update()
o['boas_panel_id_map']=json.dumps(labels,ensure_ascii=False);s['boas_v14_finish_applied']=True
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
rp=r/'docs/reports/blender/hilux_carroceria_v14.json';report=json.loads(rp.read_text(encoding='utf-8'))
report['finish']={'removed_faces':removed,'new_components':new,'rear_lower_vertices_adjusted':count,'scope':'Largura da coluna A e dobra dos cantos inferiores da caçamba; seções autorais candidatas.'}
report['base_vertices']=len(o.data.vertices);report['base_faces']=len(o.data.polygons)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();report['source_reopened']=False
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf-8'));data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return None
bpy.app.timers.register(reopen,first_interval=.5)
