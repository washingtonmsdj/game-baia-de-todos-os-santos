"""Normais/espessuras das chapas, medição direta e salvamento da fonte explícita."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert scene.name=='VIATURA | Rondesp Hilux marrom v04'
root=scene.objects['RDP01_ROOT | viatura']
for o in scene.objects:
    if o.type!='MESH' or 'HILUX04' not in o.name or 'RODAS' in ';'.join(c.name for c in o.users_collection):continue
    if any(m.type=='SOLIDIFY' for m in o.modifiers):
        bm=bmesh.new();bm.from_mesh(o.data)
        for f in bm.faces:
            c=f.calc_center_median()
            if any(w in o.name for w in ['Teto','Capô','Capota topo','Ombro capô','Painel cowl']):desired=Vector((0,0,1))
            elif any(w in o.name for w in ['Tampa caçamba','Aro tampa capota','lanterna Hilux']):desired=Vector((0,1,0))
            elif any(w in o.name for w in ['Porta estampada','Lateral caçamba','Para-lama dianteiro','Coluna','Aro porta','Vidro porta','Retorno arco']):desired=Vector((1 if c.x>0 else -1,0,0))
            elif c.y<-1.9:desired=Vector((c.x*.25,-1,0))
            elif c.y>2.5:desired=Vector((c.x*.25,1,0))
            else:desired=Vector((c.x,0,c.z-1))
            if f.normal.dot(desired)<0:f.normal_flip()
        bm.to_mesh(o.data);bm.free();o.data.update()
        for m in o.modifiers:
            if m.type=='SOLIDIFY':m.offset=-1

bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
# As inscrições seguem a superfície avaliada, inclusive abaulamento e espessura.
vs=[];fs=[]
for o in scene.objects:
    if o.type!='MESH' or not any(c.name in ['RDP01 | CARROCERIA','RDP01 | PORTAS'] for c in o.users_collection):continue
    ev=o.evaluated_get(dg);me=ev.to_mesh();base=len(vs)
    vs.extend(ev.matrix_world@v.co for v in me.vertices);fs.extend(tuple(base+i for i in p.vertices) for p in me.polygons);ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(vs,fs)
for o in scene.objects:
    if o.type!='MESH' or not o.get('boas_inscription_text'):continue
    for v in o.data.vertices:
        p=o.matrix_world@v.co;side=1 if p.x>0 else -1
        hit,normal,index,distance=bvh.ray_cast(Vector((side*2,p.y,p.z)),Vector((-side,0,0)),2)
        if hit is not None:v.co=o.matrix_world.inverted()@(hit+Vector((side*.001,0,0)))
    o.data.update();o['boas_decal_clearance_m']=.001
bpy.context.view_layer.update()
measure={}
for label,parts in [('roof',[o for o in scene.objects if 'Teto cabine curvatura' in o.name]),('body_panels',[o for o in scene.objects if o.type=='MESH' and bpy.data.collections['RDP01 | CARROCERIA'] in o.users_collection])]:
    pts=[]
    for o in parts:
        ev=o.evaluated_get(dg);me=ev.to_mesh();pts.extend(ev.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
    if pts:measure[label]={'min_xyz_m':[min(p[a] for p in pts) for a in range(3)],'max_xyz_m':[max(p[a] for p in pts) for a in range(3)],'size_xyz_m':[max(p[a] for p in pts)-min(p[a] for p in pts) for a in range(3)]}
measure['axle_centers']=[list(scene.objects[f'RDP01 | Eixo giro roda {i} +1'].matrix_world.translation) for i in (0,1)]
measure['wheelbase_m']=Vector(measure['axle_centers'][1]).y-Vector(measure['axle_centers'][0]).y
measure['notes']='Chapas medidas diretamente na cena avaliada. Medidas nominais do fabricante separadas; acessórios policiais não incluídos na largura/altura stock. Não é escaneamento da viatura.'
scene['boas_actual_geometry_measurements']=json.dumps(measure)
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v04.blend'
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
path=repo/'docs/reports/blender/rondesp_marrom_v04.json';r=json.loads(path.read_text(encoding='utf-8'))
r.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),actual_mesh_measurements=measure,saved=True)
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
