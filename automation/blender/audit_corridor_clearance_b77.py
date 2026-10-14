"""Sondagens de personagem no espaço geométrico visível; não simula engine."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];folder=root/'docs/reports/blender/lacerda-corridor'
dg=bpy.context.evaluated_depsgraph_get();vertices=[];polys=[];owners=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or not ob.visible_get() or ob.hide_render:continue
    if ob.name.startswith(('NAV |','QA |','R30A','B74 |','B75 |')):continue
    if any(c.name.startswith(('SOURCE_GEOREF','33.','34.','37.','QA |')) for c in ob.users_collection):continue
    bb=[ob.matrix_world@Vector(p) for p in ob.bound_box]
    if max(v.x for v in bb)<-140 or min(v.x for v in bb)>25 or max(v.y for v in bb)<-15 or min(v.y for v in bb)>175:continue
    evaluated=ob.evaluated_get(dg);mesh=evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles();base=len(vertices);vertices.extend(evaluated.matrix_world@v.co for v in mesh.vertices)
        for t in mesh.loop_triangles:polys.append(tuple(base+i for i in t.vertices));owners.append(ob.name)
    finally:evaluated.to_mesh_clear()
tree=BVHTree.FromPolygons(vertices,polys,all_triangles=True)
heights=json.loads((folder/'height_profiles_b76.json').read_text(encoding='utf8'))
def support(sample,stage):
    preferred=[h for h in sample['hits'] if not h['object'].startswith(('NAV |','R30A5')) and (h['z']>69 if stage in ('upper','bridge') else h['z']<10)]
    return max(preferred,key=lambda h:h['z']) if preferred else None
radius=.3;height=1.8;epsilon=.015
profiles=[]
for route in heights['profiles']:
    probes=[]
    for sample in route['samples']:
        h=support(sample,route['name'])
        if h is None:probes.append({'xy':sample['xy'],'support':None,'blockers':[]});continue
        x,y=sample['xy'];blocks={}
        for j in range(9):
            center=Vector((x,y,h['z']+radius+j*(height-2*radius)/8))
            hit=tree.find_nearest(center,radius)
            if hit[0] is not None and hit[3]<radius-epsilon:blocks[owners[hit[2]]]=min(hit[3],blocks.get(owners[hit[2]],radius))
        probes.append({'xy':sample['xy'],'support':h,'blockers':blocks})
    profiles.append({'name':route['name'],'probes':probes,'unsupported':sum(p['support'] is None for p in probes),'blocked':sum(bool(p['blockers']) for p in probes)})
result={'schema':'boas/corridor-clearance-v1','character_design':{'radius':radius,'height':height,'contact_tolerance':epsilon,'vertical_sphere_samples':9,'profile_step':.5},'method':'Nove esferas sobre eixo vertical da cápsula; nearest BVH de malhas avaliadas visíveis. Triagem estática amostrada, sem sweep contínuo ou física. Guias de NAV/runtime excluídos.','triangles':len(polys),'profiles':profiles,'geometry_changed':False}
(folder/'clearance_before_b77.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'triangles':len(polys),'profiles':[{'name':p['name'],'unsupported':p['unsupported'],'blocked':p['blocked'],'blocking_objects':sorted({name for sample in p['probes'] for name in sample['blockers']})} for p in profiles]},ensure_ascii=False))
