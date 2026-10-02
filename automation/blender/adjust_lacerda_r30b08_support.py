"""Ajusta a largura do apoio R30B08 depois de comparação visual."""
import bpy, bmesh, json
from pathlib import Path
from mathutils import Matrix, Vector

root = Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b08_apoio_passarela.blend')
rotation = Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z, 4, 'Z')
inverse = rotation.inverted()
body = bpy.data.objects['LAC R30B08 | apoio oposto | corpo estrutural afunilado']
rings = [
    (-26.10, -18.20, .78, 7.72, 21.00),
    (-25.30, -17.30, .78, 7.72, 39.00),
    (-24.55, -16.65, .78, 7.72, 58.00),
    (-24.25, -16.25, .78, 7.72, 65.40),
    (-26.60, -11.85, .63, 7.87, 68.85),
]
verts = []
for x0,x1,y0,y1,z in rings:
    verts.extend([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)])
faces = [(3,2,1,0)]
for k in range(len(rings)-1):
    a = k*4; b = a+4
    faces.extend([(a+i,a+(i+1)%4,b+(i+1)%4,b+i) for i in range(4)])
faces.append(tuple(range((len(rings)-1)*4,len(rings)*4)))
mesh = body.data
mesh.clear_geometry()
mesh.from_pydata([tuple(rotation @ Vector(v)) for v in verts],[],faces)
mesh.update()
bm = bmesh.new(); bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(mesh); bm.free()
body['ground_sample_min_z'] = 21.0

def reshape_box(name, center, size):
    obj = bpy.data.objects['LAC R30B08 | ' + name]
    old = [inverse @ v.co for v in obj.data.vertices]
    mins = [min(v[i] for v in old) for i in range(3)]
    maxs = [max(v[i] for v in old) for i in range(3)]
    new_min = [center[i]-size[i]/2 for i in range(3)]
    new_max = [center[i]+size[i]/2 for i in range(3)]
    for v in obj.data.vertices:
        p = inverse @ v.co
        q = Vector([new_min[i]+(p[i]-mins[i])/(maxs[i]-mins[i])*(new_max[i]-new_min[i]) for i in range(3)])
        v.co = rotation @ q
    obj.data.update()

reshape_box('apoio oposto | capitel sob passarela',(-19.225,4.25,68.96),(15.,7.45,.44))
reshape_box('apoio oposto | ressalto transversal',(-19.225,4.25,68.58),(14.50,7.18,.24))
bpy.ops.wm.save_mainfile()
report = root / 'artifacts/lacerda/r30b08_support_report.json'
data = json.loads(report.read_text(encoding='utf8'))
data['visual_revision'] = 'Apoio alargado conforme proporção da foto; base acompanha a encosta.'
report.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print('R30B08 apoio alargado e salvo')
