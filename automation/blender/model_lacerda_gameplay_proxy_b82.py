"""B82 separada: proxy funcional; nenhuma malha histórica é editada."""
import bpy, json, math, hashlib, os, runpy, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-gameplay-proxy'
sys.path.insert(0,str(ROOT/'tools/world'))
from lacerda_gameplay_proxy import validate_round_trip
config=json.loads((ROOT/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json').read_text(encoding='utf8'))
source=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(ROOT/config['source_file']).resolve()
assert not bpy.data.is_dirty, 'Preservar sessão antes de construir o proxy'
assert not (ROOT/config['scene_file']).exists(), 'Não sobrescrever revisão proxy existente'
assert config['scene_name'] not in bpy.data.scenes
sig=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature']
def signature(ob):
    try:return sig(ob)
    except RuntimeError:return {'type':ob.type,'basis':[list(r) for r in ob.matrix_basis],'data':ob.data.name if ob.data else None}
protected={o.name:signature(o) for o in source.objects}
(OUT/'protected_original_components.json').write_text(json.dumps(protected,ensure_ascii=False)+'\n',encoding='utf8')
original_visibility={o.name:o.visible_get(view_layer=source.view_layers[0]) for o in source.objects}
scene=bpy.data.scenes.new(config['scene_name']);scene.frame_set(source.frame_current)
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.
scene.world=source.world
for col in source.collection.children:scene.collection.children.link(col)
layer=scene.view_layers[0]
col=bpy.data.collections.new('GAMEPLAY_PROXY | Lacerda B82');scene.collection.children.link(col)
col['status']='GAMEPLAY_PROXY';col['accuracy']='APPROXIMATE';col['replacement_required']=True
col['boas_detail_level']='PLAYABLE_CORE';col['boas_collision_profile_id']='lacerda-gameplay-proxy-b82'
bpy.context.window.scene=scene
a=config['local_frame']['angle'];c,s=math.cos(a),math.sin(a);origin=config['local_frame']['origin_xy']
def world(p):return (origin[0]+c*p[0]-s*p[1],origin[1]+s*p[0]+c*p[1],p[2])
def mark(ob,role,src=None):
    ob['status']='GAMEPLAY_PROXY';ob['accuracy']='APPROXIMATE';ob['replacement_required']=True
    ob['boas_role']=role;ob['boas_generated_revision']='R30B.82'
    ob['boas_collision_profile_id']='lacerda-gameplay-proxy-b82'
    ob['boas_provenance_ids']=json.dumps(['derived:lacerda-gameplay-proxy-b82'])
    ob['boas_pending_gate']=config['historical_gate'];ob['boas_geographic_ssot_id']='salvador-geographic-reference-v1'
    ob['boas_production_ready']=False
    if src:ob['boas_derived_from_object']=src
    return ob
def material(name,color):
    m=bpy.data.materials.new('B82 | '+name);m.diffuse_color=(*color,1.);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1.);p.inputs['Roughness'].default_value=.65
    return m
floor_mat=material('piso proxy',(.38,.45,.50));wall_mat=material('estrutura proxy',(.72,.74,.76))
door_mat=material('portas proxy',(.10,.32,.47));guide_mat=material('gradil proxy',(.21,.24,.26));person_mat=material('personagem',(.95,.40,.05))
faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
added=[]
def box(id,center,size,angle=0.,mat=wall_mat,role='STATIC_OBSTACLE',src=None,slope=0.):
    hx,hy,hz=[v/2 for v in size]
    verts=[(x,y,z+x*slope) for z in (-hz,hz) for x,y in [(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)]]
    data=bpy.data.meshes.new('B82 | '+id);data.from_pydata(verts,[],faces);data.update()
    ob=bpy.data.objects.new('B82 | '+id,data);col.objects.link(ob);ob.location=world(center);ob.rotation_euler.z=a+angle
    data.materials.append(mat);mark(ob,role,src);ob['boas_proxy_id']=id
    added.append(ob.name);return ob
for f in config['floors']:
    p=f['center'][:];p[2]-=.09
    box(f['id'],p,[*f['size'],.18],f['angle'],floor_mat,'WALKABLE_FLOOR',f.get('source'),f.get('slope',0.))
for b in config['obstacles']:box(b['id'],b['center'],b['size'],b.get('angle',0.),guide_mat if 'queue' in b['id'] else wall_mat,src=b.get('source'))
def dynamic(id,center,size,tag,mat=wall_mat,**props):
    original=center[:];p=center[:]
    if tag.startswith('cabin_'):p[2]+=config['levels']['upper']
    ob=box(id,p,size,mat=mat,role='DYNAMIC_CABIN' if tag.startswith('cabin_') else 'DYNAMIC_DOOR')
    ob['boas_proxy_dynamic']=tag;ob['boas_proxy_local_center']=json.dumps(original)
    for k,v in props.items():ob[k]=v
    return ob
dynamic('cabin_floor',[0,0,-.09],[3.4,2.6,.18],'cabin_floor',floor_mat)
for side in (-1,1):dynamic(f'cabin_wall_{side}',[0,side*1.36,1.35],[3.52,.12,2.7],'cabin_wall')
dynamic('cabin_roof',[0,0,2.76],[3.64,2.84,.12],'cabin_roof')
for landing,z in config['levels'].items():
    side=1 if landing=='upper' else -1
    for leaf in (-1,1):
        dynamic(f'landing_{landing}_{leaf}',[side*1.76,leaf*.4,z+1.25],[.12,.8,2.5],'landing_door',door_mat,boas_proxy_landing=landing,boas_proxy_leaf=leaf)
        dynamic(f'cabin_door_{landing}_{leaf}',[side*1.7,leaf*.4,1.25],[.10,.8,2.5],'cabin_door',door_mat,boas_proxy_side=side,boas_proxy_leaf=leaf)
# Cápsula visível: a geometria corresponde ao envelope do controller.
verts=[(0,0,0.)];rings=[]
for center_z,angles in [(.3,[-math.pi/2+i*math.pi/10 for i in range(1,6)]),(1.5,[i*math.pi/10 for i in range(5)])]:
    for t in angles:
        ring=[]
        for i in range(16):
            ring.append(len(verts));phi=2*math.pi*i/16;verts.append((.3*math.cos(t)*math.cos(phi),.3*math.cos(t)*math.sin(phi),center_z+.3*math.sin(t)))
        rings.append(ring)
polys=[(0,rings[0][(i+1)%16],rings[0][i]) for i in range(16)]
for ra,rb in zip(rings,rings[1:]):polys.extend((ra[i],ra[(i+1)%16],rb[(i+1)%16],rb[i]) for i in range(16))
top=len(verts);verts.append((0,0,1.8));polys.extend((rings[-1][i],rings[-1][(i+1)%16],top) for i in range(16))
mesh=bpy.data.meshes.new('B82 | cápsula');mesh.from_pydata(verts,[],polys);mesh.update()
player=bpy.data.objects.new('B82 | personagem proxy',mesh);col.objects.link(player);mesh.materials.append(person_mat)
player.location=world([*config['spawn'][:2],config['spawn'][2]+.015]);mark(player,'PLAYER');player['boas_proxy_dynamic']='player';player['boas_proxy_local_center']='[0,0,0]';added.append(player.name)
# Finalização única, também reutilizável após interrupção anterior ao save.
runpy.run_path(str(ROOT/'automation/blender/finalize_lacerda_gameplay_proxy_b82.py'),run_name='__main__')
