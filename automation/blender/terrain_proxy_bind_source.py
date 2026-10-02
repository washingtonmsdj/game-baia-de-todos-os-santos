"""Corrige o binding do proxy: local XY coincide com terreno, world matrix não.

Restaura o proxy preservado, confirma os limites locais, aplica o transform
EXISTENTE da fonte e só então atualiza Z por suporte autoral. Não move a cidade.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text())
if c['world_source']['revision']!='R30B.25':raise RuntimeError('Revisão R30B25 esperada')
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():bpy.ops.wm.open_mainfile(filepath=str(root/c['world_source']['file']))
scene=bpy.context.scene;source=scene.objects[c['export']['road_object']];proxy=scene.objects[c['export']['terrain_proxy']]
with bpy.data.libraries.load(str(root/'blender/salvador_lacerda_r30b23_fachada_praca.blend'),link=False) as (src,dst):dst.objects=[proxy.name]
original=dst.objects[0]
def bounds(mesh):return [[min(v.co[i] for v in mesh.vertices) for i in range(2)],[max(v.co[i] for v in mesh.vertices) for i in range(2)]]
a=bounds(source.data);b=bounds(original.data)
if max(abs(a[i][j]-b[i][j]) for i in range(2) for j in range(2))>.01:
    bpy.data.objects.remove(original,do_unlink=True);raise RuntimeError('Limites locais não coincidem: não aplicar transform da fonte')
old_matrix=[list(row) for row in proxy.matrix_world]
proxy.data=original.data.copy();bpy.data.objects.remove(original,do_unlink=True);proxy.matrix_world=source.matrix_world.copy();bpy.context.view_layer.update()
source.data.calc_loop_triangles();tree=BVHTree.FromPolygons([source.matrix_world@v.co for v in source.data.vertices],[list(t.vertices) for t in source.data.loop_triangles],all_triangles=True);inverse=proxy.matrix_world.inverted();missing=[];changed=0;maxdelta=0
for v in proxy.data.vertices:
    p=proxy.matrix_world@v.co;q=tree.ray_cast(Vector((p.x,p.y,160)),Vector((0,0,-1)),350)[0]
    if q is None:
        # Shared outer edges are prone to float ray cancellation: use inward
        # probes of 2 mm only, covering measured sub-millimeter overshoot in
        # original boundary vertices; never introduce a new ground surface.
        found=[]
        for dx,dy in [(.002,0),(-.002,0),(0,.002),(0,-.002),(.002,.002),(-.002,.002),(.002,-.002),(-.002,-.002)]:
            hit=tree.ray_cast(Vector((p.x+dx,p.y+dy,160)),Vector((0,0,-1)),350)[0]
            if hit:found.append(hit)
        if found:q=min(found,key=lambda point:abs(point.z-p.z))
    if q is None:missing.append(v.index);continue
    delta=abs(q.z-p.z);maxdelta=max(maxdelta,delta)
    if delta>1e-5:v.co.z=(inverse@Vector((p.x,p.y,q.z))).z;changed+=1
proxy.data.update();proxy['boas_support_source']=source.name;proxy['boas_transform_binding']='SOURCE_MATRIX: bounds local XY match verified; source world transform applied, then individual Z support samples';proxy['boas_missing_support']=len(missing)
r={'source_before':c['world_source'].copy(),'classification':'ERROR','visual_geometry_changed':False,'city_xy_changed':False,'road_widths_changed':False,'source_local_xy_bounds':a,'proxy_local_xy_bounds_before':b,'proxy_world_matrix_before':old_matrix,'proxy_world_matrix_after':[list(row) for row in proxy.matrix_world],'height_samples_changed':changed,'max_resample_delta_m':maxdelta,'missing_support_count':len(missing),'missing_support_ids':missing,'edge_probe_tolerance_m':.002,'method':'apply confirmed source transform to preserved proxy, then resample current terrain; no guessed geographic offset','runtime_exported':False,'vehicle_retest':'pending'}
if missing:
    r['missing_positions']=[list(proxy.matrix_world@proxy.data.vertices[id].co) for id in missing];(root/'artifacts/terrain-vehicle/proxy-binding-pending.json').write_text(json.dumps(r,indent=2),encoding='utf8');raise RuntimeError('Proxy ainda sem fonte em '+str(len(missing))+' pontos; não promover')
out=root/'blender/salvador_lacerda_r30b26_terreno_colisao_alinhados.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));c['world_source'].update(file=out.relative_to(root).as_posix(),sha256=hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),revision='R30B.26',selection_reason='Derivada da R30B23: encontro Montanha/Pau da Bandeira contínuo e binding confirmado do colisor ao transform do terreno. Larguras/implantação visual preservadas. Revisão parcial da cidade.');cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8');r['source_after']=c['world_source'];(root/'docs/reports/blender/terrain_proxy_binding.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in r.items() if k!='missing_support_ids'},ensure_ascii=False))
