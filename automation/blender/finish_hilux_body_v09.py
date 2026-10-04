"""Continuidade das chapas e acabamento de forma da V09 na janela visível."""
import ast
import bpy
import bmesh
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

repo = Path(__file__).resolve().parents[2]
s = bpy.context.scene
assert not bpy.app.background
assert Path(bpy.data.filepath).name == 'marrom_v09.blend'
assert not s.get('boas_v09_finish_applied')
root = s.objects['RDP01_ROOT | viatura']
pfx = 'RDP01 | HILUX06 | '
checkpoint = repo / 'artifacts/vehicles/rondesp/v09-before-finish.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint), {s}, path_remap='RELATIVE', fake_user=True, compress=True)
for filename, names in [('rebuild_hilux_reference_v06.py', ['interp']), ('finish_hilux_reference_v06.py', ['nose'])]:
    for fn in ast.parse((repo / 'automation/blender' / filename).read_text(encoding='utf-8')).body:
        if isinstance(fn, ast.FunctionDef) and fn.name in names:
            exec(compile(ast.Module(body=[fn], type_ignores=[]), '<v09-helpers>', 'exec'), globals())

changed = []
def touch(o):
    o.data.update()
    o['boas_v09_finish'] = 'candidate; continuidade das chapas interpretada das referências'
    changed.append(o.name)

def new_sheet(name, vs, fs, material, collection):
    m = bpy.data.meshes.new(name)
    m.from_pydata(vs, [], fs)
    bm = bmesh.new(); bm.from_mesh(m)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.00001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(m); bm.free()
    o = bpy.data.objects.new(name, m)
    bpy.data.collections[collection].objects.link(o)
    o.parent = root
    m.materials.append(material)
    for p in m.polygons: p.use_smooth = True
    mod = o.modifiers.new('Espessura chapa', 'SOLIDIFY'); mod.thickness = .008
    touch(o)
    return o

# Remover o deslocamento longitudinal do raio transversal: a estação Y do
# para-lama deve continuar casando com o capô, sem uma torção junto ao farol.
hood = s.objects[pfx + 'Capô e ombros estampados']
for side in (-1,1):
    o = s.objects[pfx + 'Para-lama dianteiro ' + str(side)]
    for i in range(73):
        for j in range(31):
            o.data.vertices[i*31+j].co.y = -1.945 + .970*i/72
    touch(o)
    # Retorno lateral real entre duas bordas existentes. Fecha a abertura
    # observada; não é uma placa plana colocada por cima do conjunto.
    vs = []
    for j in range(31):
        p = o.data.vertices[j].co.copy()
        a = Vector((side*.9275, nose(side*.9275,p.z), p.z))
        for k in range(5):
            v = a.lerp(p,k/4)
            vs.append(tuple(v))
    fs = [(j*5+k,(j+1)*5+k,(j+1)*5+k+1,j*5+k+1) for j in range(30) for k in range(4)]
    new_sheet('RDP01 | HILUX09 | Retorno farol '+str(side),vs,fs,hood.data.materials[0],'RDP01 | CARROCERIA')

# Curvatura longitudinal contínua da região de portas. Mesma transformação
# em chapas, juntas, inscrições e ferragens; pivôs e matrizes permanecem.
allowed = {'RDP01 | CARROCERIA','RDP01 | PORTAS','RDP01 | INSCRICOES'}
def curve_side(p):
    x,y,z = p
    if not (-.975 < y < 1.145 and .49 < z < 1.302 and abs(x)>.74):
        return p
    a = (y+.975)/2.12
    b = (z-.49)/.812
    dx = .024*math.sin(math.pi*a)**2*math.sin(math.pi*b)**2
    return Vector((x+math.copysign(dx,x),y,z))

for o in list(s.objects):
    if not any(c.name in allowed for c in o.users_collection): continue
    if o.type not in ('MESH','CURVE'): continue
    if 'HILUX09' in o.name or 'Capô' in o.name or 'Para-lama' in o.name: continue
    to_root = root.matrix_world.inverted() @ o.matrix_world
    to_local = to_root.inverted()
    modified = False
    if o.type == 'MESH':
        for v in o.data.vertices:
            p = to_root @ v.co; q = curve_side(p)
            if (q-p).length > 1e-8: v.co=to_local@q; modified=True
    else:
        for spline in o.data.splines:
            for v in spline.points:
                p = to_root @ Vector(v.co[:3]); q = curve_side(p)
                if (q-p).length > 1e-8: v.co=(*(to_local@q),v.co.w); modified=True
    if modified:
        if o.type == 'MESH': touch(o)
        else: changed.append(o.name)

# Encontro traseiro do teto: elevar apenas a faixa que antes descia abaixo
# da armação lateral. Largura e altura seguem os limites da cabine existente.
roof = s.objects[pfx + 'Teto curvatura dupla']
for v in roof.data.vertices:
    x,y,z = v.co
    if y > .86:
        t = min(1,(y-.86)/.253)
        e = t*t*(3-2*t)
        v.co.z += .065*e
        v.co.x *= 1+.052*e
touch(roof)

# Faces internas das caixas devem bloquear a vista através da carroceria.
# Mantém rodas e raios de giro; acrescenta fechamento do lado do chassis.
black = bpy.data.materials['RDP01 | Polímero preto']
for side in (-1,1):
    for axle in (-1.43,1.655):
        vs=[(side*.555,axle,.38815)]
        vs += [(side*.555,axle+.52*math.cos(i*math.pi/48),.38815+.52*math.sin(i*math.pi/48)) for i in range(49)]
        fs=[(0,i+1,i+2) for i in range(48)]
        new_sheet('RDP01 | HILUX09 | Fecho interno caixa '+str((side,axle)),vs,fs,black,'RDP01 | CHASSIS')

s['boas_v09_finish_applied'] = True
s['boas_review_status'] = 'candidate; forma revista, brasão e camuflagem exata pendentes'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            space.shading.type = 'SOLID'; space.shading.color_type = 'MATERIAL'
            space.shading.light = 'STUDIO'; space.shading.studio_light = 'paint.sl'
            space.shading.show_cavity = False; space.overlay.show_overlays = False
            space.region_3d.view_rotation = (Vector((0,.16,1.03))-Vector((-7,-8,3.1))).to_track_quat('-Z','Y')
            space.region_3d.view_location = (0,.16,1.03); space.region_3d.view_distance = 5.8
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v09.blend'
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
rp=repo/'docs/reports/blender/rondesp_marrom_v09.json'
r=json.loads(rp.read_text(encoding='utf-8'))
r['finish_changed_objects']=changed
r['changes'] += ['retorno lateral dos faróis fechado','coroa longitudinal das portas e inscrições conformadas','encaixe posterior do teto','fechamento interno das caixas de roda']
r['sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
r['source_reopened']=False
r['pending']=['comparação visual final','brasão PMBA detalhado','camuflagem exata','animação e runtime']
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out))
    r=json.loads(rp.read_text(encoding='utf-8'))
    r['source_reopened']=Path(bpy.data.filepath).resolve()==out.resolve()
    rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return None
bpy.app.timers.register(reopen,first_interval=.5)
