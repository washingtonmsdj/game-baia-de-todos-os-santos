"""Fecha joins e colisores, salva/reabre a revisão e exporta pelo wrapper oficial."""
import bpy,json,hashlib,runpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text());scene=bpy.context.scene
config_path=root/'prototypes/threejs-water-lab/public/data/urban_slice.json';config=json.loads(config_path.read_text())
# Replace fans by sidewalk rings: leave the middle of each join driveable.
for o in scene.objects:
    if not o.name.startswith('SLICE | transição passeio'):continue
    if len(o.data.vertices)%2==0:continue
    vs=[v.co.copy() for v in o.data.vertices];center=vs[0];outer=vs[1:];inner=[]
    for p in outer:
        d=p-center;d.z=0;inner.append(center+d*max(0,(d.length-1.7)/d.length))
    n=len(outer);vertices=[tuple(v) for v in inner+outer];faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o.data.clear_geometry();o.data.from_pydata(vertices,[],faces);o.data.update()
# Footprint convex hulls from the actual low-cost building source, avoiding AABB
# corners that can falsely block a rotated sidewalk.
for item in config['obstacles']:
    o=scene.objects.get(item['name']);pts=[o.matrix_world@v.co for v in o.data.vertices]
    xy=sorted(set((round(p.x,4),round(p.y,4)) for p in pts))
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    low=[];high=[]
    for p in xy:
        while len(low)>=2 and cross(low[-2],low[-1],p)<=0:low.pop()
        low.append(p)
    for p in reversed(xy):
        while len(high)>=2 and cross(high[-2],high[-1],p)<=0:high.pop()
        high.append(p)
    hull=low[:-1]+high[:-1];base=min(p.z for p in pts);height=max(p.z for p in pts)
    item['vertices']=[v for z in [base,height] for x,y in hull for v in (x,z,-y)]
def runtime(p):return [round(p.x,5),round(p.z,5),round(-p.y,5)]
config['surfaces']=[]
for o in bpy.data.collections['41 GAMEPLAY | URBAN SLICE'].objects:
    m=o.data;m.calc_loop_triangles();config['surfaces'].append({'name':o.name,'role':o['boas_role'],'positions':[v for p in m.vertices for v in runtime(o.matrix_world@p.co)],'indices':[v for t in m.loop_triangles for v in t.vertices]})
config_path.write_text(json.dumps(config,ensure_ascii=False,separators=(',',':')),encoding='utf8')
# Include the new geometry in canonical surface export, not only in the prototype.
c['export']['urban_slice_collection']='41 GAMEPLAY | URBAN SLICE'
c['world_source']['selection_reason']='Revisão real R30C.1: suporte reprojetado e circuito OSM jogável; R30A.11 preservada'
output=root/'blender/salvador_lacerda_mvp_r30c2_urban_slice.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
c['world_source'].update(file=output.relative_to(root).as_posix(),revision='R30C.2')
c['world_source']['sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(root/c['world_source']['file']))
assert bpy.context.scene.get('boas_urban_slice_id')==config['id']
report_path=root/'docs/reports/blender/urban_slice_scene.json';report=json.loads(report_path.read_text(encoding='utf8'));report.update(source=c['world_source'],reopened=True,gameplay_surfaces=len(config['surfaces']),footprint_colliders=len(config['obstacles']));report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
runpy.run_path(str(root/'automation/blender/export_active_world.py'),run_name='__main__')
