"""Subtrai o volume do apoio do terreno/proxy; conserva superfícies superiores.

O apoio envolve o vazio observado entre o vidro e a parede posterior.
Terreno não pode permanecer dentro dessa estrutura.
"""
import bpy,bmesh,json,hashlib,runpy
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];path=root/'docs/reports/blender/torre_galerias_r30b35.json';r=json.loads(path.read_text(encoding='utf8'));scene=bpy.context.scene
assert 'support_volume_cut' not in r
helpers=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=helpers['signature'],helpers['world_matrix'];R=Matrix(r['tower_alignment']['rotation_world']);RI=R.inverted();rx,ry,up=R@Vector((1,0,0)),R@Vector((0,1,0)),Vector((0,0,1))
ring=r['tower_alignment']['rings_local'][0];x0,x1,y0,y1,z0=ring;z1=r['tower_alignment']['cap_top_from_floor_bottom_m'];source=scene.objects[r['terrain_names'][0]]
allowed={i for i,m in enumerate(source.data.materials) if any(k in m.name.lower() for k in ('terreno','conten','encosta')) and not any(k in m.name.lower() for k in ('asfalto','pedonal','percurso','passeio','calçada','calcada','chile'))}
def roads(me):
    ids={v for p in me.polygons if p.material_index not in allowed for v in p.vertices}
    return {tuple(round(c,5) for c in me.vertices[i].co) for i in ids}
road_before=roads(source.data);rows=[]
for name in r['terrain_names']:
    o=scene.objects[name];mesh=o.data;before=sig(o);M=wm(o);I=M.inverted()
    a=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',a);m=np.array(M);world=a.reshape((-1,3))@m[:3,:3].T+m[:3,3];local=world@np.array(RI)[:3,:3].T
    loops=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('vertex_index',loops);starts=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('loop_start',starts)
    mask=np.ones(len(mesh.polygons),dtype=bool)
    for axis,low,high in ((0,x0,x1),(1,y0,y1),(2,z0,z1)):
        values=local[:,axis][loops];mask&=(np.maximum.reduceat(values,starts)>=low-.01)&(np.minimum.reduceat(values,starts)<=high+.01)
    if o==source:
        mats=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('material_index',mats);mask&=np.isin(mats,list(allowed))
    indices=np.flatnonzero(mask);bm=bmesh.new();bm.from_mesh(mesh);bm.faces.ensure_lookup_table();region={bm.faces[int(i)] for i in indices}
    for axis,value in ((rx,x0),(rx,x1),(ry,y0),(ry,y1),(up,z0),(up,z1)):
        faces=[f for f in region if f.is_valid and (o!=source or f.material_index in allowed)];geom=set(faces)
        for f in faces:geom.update(f.edges);geom.update(f.verts)
        cut=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(axis*value),plane_no=M.to_3x3().transposed()@axis,clear_inner=False,clear_outer=False)
        for g in cut['geom_cut']:
            if hasattr(g,'link_faces'):region.update(g.link_faces)
    removed=[]
    for f in region:
        if not f.is_valid or (o==source and f.material_index not in allowed):continue
        p=RI@M@f.calc_center_median()
        if x0+.00001<p.x<x1-.00001 and y0+.00001<p.y<y1-.00001 and z0+.00001<p.z<z1-.00001:removed.append(f)
    bmesh.ops.delete(bm,geom=removed,context='FACES_ONLY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();rows.append({'object':name,'before':before,'after':sig(o),'removed_faces':len(removed)})
assert not road_before-roads(source.data),'Circulação alterada'
# Piso superior simples derivado da própria laje, independente de solo.
G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry'];floor=scene.objects['SUPERIOR | piso saguão'];pts=[RI@wm(floor)@v.co for v in floor.data.vertices];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
col=bpy.data.collections['COLLISION | Galerias Cidade Alta R34'];g=G();g.box(R@Vector(tuple((a+b)/2 for a,b in zip(lo,hi))),tuple(b-a for a,b in zip(lo,hi)),(rx,ry,up));o=g.object('COLLISION R35 | Laje do saguão superior',col,floor.data.materials[0],props={'boas_role':'static_collider','boas_location_id':'elevador-lacerda','boas_revision':'R30B.35','source_object':floor.name});o.hide_render=True;o.hide_set(True);r['created_objects'].append(o.name)
# Máscara reamostrada sobre a geometria final, distinguindo solo da contenção.
me=source.data;a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);m=np.array(wm(source));world=a.reshape((-1,3))@m[:3,:3].T+m[:3,3];local=world@np.array(RI)[:3,:3].T
values=np.zeros(len(world),dtype=np.float32);trans=r['terrain_refinement']['support_lateral_transition'];a0,a1=trans['limits_y_from_upper_floor_m'];b0,b1=trans['full_weight_y_from_support_m']
def ease(t):t=np.clip(t,0,1);return t*t*(3-2*t)
region=(local[:,0]>=-30)&(local[:,0]<=x0+.25)&(local[:,1]>=a0)&(local[:,1]<=a1)
wy=np.minimum(ease((local[:,1]-a0)/(b0-a0)),ease((a1-local[:,1])/(a1-b1)))
values=np.where(region,wy*ease((local[:,0]+30)/3)*np.where(local[:,0]>x0,1-ease((local[:,0]-x0)/.25),1),0).astype(np.float32)
for s in r['galleries']['segments']:
    d=world-np.array(s['origin_world']);x=d@np.array(s['along_world']);y=d@np.array(s['outward_world']);L=s['length_from_existing_controls_m'];mask=(x>0)&(x<L)&(y>0)&(y<20)
    v=np.clip(np.minimum(x,L-x)/1.5,0,1)*np.clip(1-np.maximum(0,y-8)/12,0,1);values=np.maximum(values,np.where(mask,v,0).astype(np.float32))
road_bank_z=r['terrain_refinement']['support_profile_anchors'][1]['z30'];values*=np.clip((world[:,2]-road_bank_z)/4,0,1).astype(np.float32)
me.attributes['boas_r35_solo_encosta'].data.foreach_set('value',values)
for mat in me.materials:
    if mat.name.startswith('ENV R35 | terreno e rocha'):
        out=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL');out.is_active_output=True
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
for row in r['terrain_refinement']['geometry']:row['after']=sig(scene.objects[row['object']])
r['support_volume_cut']={'classification':'ERROR','reason':'Solo dentro da faixa envidraçada: escavação volumétrica delimitada pela estrutura, não deslocamento da estrutura para escapar ao terreno. Superfícies acima da laje superior preservadas.','bounds_local_m':[ring,[x0,x1,y0,y1,z1]],'geometry':rows,'upper_floor_collider':o.name,'upper_floor_bounds_from_object':[lo,hi],'source_road_positions_preserved':len(road_before),'ground_material_resampled_vertices':int(np.count_nonzero(values)),'review':'pending'}
for row in rows:r['reference_detail_refinement']['after'][row['object']]=sig(scene.objects[row['object']])
r['reference_detail_refinement']['localized_ground_material']['masked_vertices']=int(np.count_nonzero(values))
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'source_after':r['source_after'],'removed':[(x['object'],x['removed_faces']) for x in rows],'roads':len(road_before)},ensure_ascii=False))
