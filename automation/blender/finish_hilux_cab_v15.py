"""Regulariza a chapa da armação e dobra a borda do para-brisa na sessão visível."""
import ast,bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_carroceria_v15.blend'
assert s.get('boas_v15_applied') and not s.get('boas_v15_contours_finished')
o=s.objects['HILUX | CARROCERIA PRINCIPAL'];labels=json.loads(o['boas_panel_id_map'])
checkpoint=r/'artifacts/vehicles/rondesp/pre-v15-contours-finish.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
for fn in ast.parse((r/'automation/blender/rebuild_hilux_cab_v15.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name in {'smooth','roof_width','roof_edge_z','cab_side','radius','rear_y','cab_x'}:
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'curvas-v15','exec'),globals())
for fn in ast.parse((r/'automation/blender/rebuild_hilux_reference_v06.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name in {'interp','sidewidth'}:
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'secoes-v06','exec'),globals())
def pid(name):return next(int(k) for k,v in labels.items() if v==name)
cage=pid('HILUX15 | Armacão lateral continua A B C')
roof=pid('HILUX15 | Teto continuo ate as colunas')
jambs={pid('HILUX15 | Batente dianteiro ligado ao contorno'),pid('HILUX15 | Batente traseiro ligado ao contorno')}
bm=bmesh.new();bm.from_mesh(o.data);fl=bm.faces.layers.int.get('boas_panel_id');deform=bm.verts.layers.deform.verify()
cage_faces=[f for f in bm.faces if f[fl]==cage]
counts={}
for f in cage_faces:
    for e in f.edges:counts[e]=counts.get(e,0)+1
boundary={v for e,n in counts.items() if n==1 for v in e.verts}
outer_boundary={v for v in boundary if any(f[fl] not in ({cage}|jambs) for f in v.link_faces)}
fore=sorted({v for e,n in counts.items() if n==1 for v in e.verts
    if v.co.y<-.31 and v.co.z>=1.3259 and abs(v.co.y-(-.970+.632*(v.co.z-1.326)/.442))<.00002},key=lambda v:v.co.z)
assert len(fore)==33
# O perfil da coluna A segue o mesmo plano da borda externa. O perfil B/C é
# contínuo em Z, sem a troca abrupta entre o volume inferior e a janela.
def regular_x(y,z):
    x=cab_side(z)
    if z>.58:
        top=roof_edge_z(y)
        x+=(roof_width(y)-cab_side(top))*smooth((z-1.58)/max(.05,top-1.58))
    if z<.525:x=.830*(1-smooth((z-.489)/.036))+x*smooth((z-.489)/.036)
    if z>1.3259:
        fy=-.970+.632*(z-1.326)/.442
        fx=.803-.092*(z-1.326)/.442
        weight=1-smooth((y-fy)/.24)
        baseline=cab_side(z)
        if z>1.58:
            top=roof_edge_z(fy)
            baseline+=(roof_width(fy)-cab_side(top))*smooth((z-1.58)/max(.05,top-1.58))
        x+=(fx-baseline)*weight
    else:
        # O encontro inferior com o para-lama é mantido e a diferença diminui
        # gradualmente para dentro da armação, em vez de criar um ressalto.
        old=cab_x(y,z)
        weight=1-smooth((y+.97)/.22)
        x=x*(1-weight)+old*weight
    return x
changed=0
for v in bm.verts:
    ids={f[fl] for f in v.link_faces}
    if not ids.intersection({cage}|jambs) or v in outer_boundary:continue
    y,z=v.co.y,v.co.z
    if v in fore:continue
    if cage in ids:v.co.x=regular_x(y,z)
    else:v.co.x+=regular_x(y,z)-cab_x(y,z)
    changed+=1
# Os nós externos já têm as coordenadas corretas; o retorno usa esses mesmos
# nós e mantém a borda do para-brisa conectada à armação.
g=o.vertex_groups.new(name='HILUX15 | Retorno continuo lateral parabrisa')
labels[str(g.index+1)]=g.name
inner=[]
for v in fore:
    p=v.co+Vector((-.012,.006,-.002))
    n=bm.verts.new(p);n[deform][g.index]=1.;inner.append(n)
for i in range(len(fore)-1):
    f=bm.faces.new([fore[i],inner[i],inner[i+1],fore[i+1]])
    f[fl]=g.index+1;f.material_index=cage_faces[0].material_index;f.smooth=True
bm.normal_update()
# Pequena dobra arredondada da chapa entre teto e laterais. Não aplica bevel
# a toda a carroceria nem altera os conjuntos ocultos.
roof_edges=[e for e in bm.edges if len(e.link_faces)==2 and {f[fl] for f in e.link_faces}=={cage,roof}]
assert len(roof_edges)>=64
bevel=bmesh.ops.bevel(bm,geom=roof_edges,offset=.008,offset_type='OFFSET',segments=4,
    affect='EDGES',clamp_overlap=True,loop_slide=True,profile=.5)
for f in bevel.get('faces',[]):f.smooth=True
# Orientação coerente de todos os painéis conectados da cabine, inclusive
# retornos. A área do teto define o lado externo do conjunto.
cab_ids={int(k) for k,v in labels.items() if v.startswith('HILUX15 |')}
cab_faces=[f for f in bm.faces if f[fl] in cab_ids]
bmesh.ops.recalc_face_normals(bm,faces=cab_faces)
roof_faces=[f for f in cab_faces if f[fl]==roof]
if sum(f.normal.z*f.calc_area() for f in roof_faces)<0:
    for f in cab_faces:f.normal_flip()
bm.normal_update();bm.to_mesh(o.data);bm.free();o.data.update()
o['boas_panel_id_map']=json.dumps(labels,ensure_ascii=False)
s['boas_v15_contours_finished']=True
rp=r/'docs/reports/blender/hilux_carroceria_v15.json'
report=json.loads(rp.read_text(encoding='utf-8'))
report['contour_finish']={'regularized_vertices':changed,'rounded_roof_edges':len(roof_edges),
    'roof_roll_radius_candidate_m':.008,'windshield_side_return_candidate_m':.012}
report['notes'].extend(['Perfil da armação regularizado sem degrau nas colunas A/B.',
    'Dobra arredondada localizada no encontro teto/lateral e retorno contínuo do para-brisa.'])
report['new_components'].append(g.name)
report['visual_review']='pending';report['source_reopened']=False
report['base_vertices']=len(o.data.vertices);report['base_faces']=len(o.data.polygons)
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bpy.context.view_layer.update()
