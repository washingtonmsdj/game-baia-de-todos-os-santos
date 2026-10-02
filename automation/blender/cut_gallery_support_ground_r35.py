"""Escavação sob galerias e perfil da encosta pelo apoio corrigido.

O piso superior é estrutural: lajes mantêm a cota. O heightfield não ocupa
o volume dos vãos. Fonte DEM, traçado e vértices de pistas são preservados.
"""
import bpy,bmesh,json,math,hashlib,runpy
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2];scene=bpy.context.scene;path=root/'docs/reports/blender/torre_galerias_r30b35.json';r=json.loads(path.read_text(encoding='utf8'))
assert r['terrain_stage']=='pending','Perfil já aplicado'
helpers=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=helpers['signature'];wm=helpers['world_matrix']
source=scene.objects[r['terrain_names'][0]];me=source.data;me.calc_loop_triangles()
M=wm(source);triangles=list(me.loop_triangles);tri_materials=[me.polygons[t.polygon_index].material_index for t in triangles]
bvh=BVHTree.FromPolygons([M@v.co for v in me.vertices],[list(t.vertices) for t in triangles],all_triangles=True)
allowed={i for i,m in enumerate(me.materials) if any(k in m.name.lower() for k in ('terreno','conten','encosta')) and not any(k in m.name.lower() for k in ('asfalto','pedonal','percurso','passeio','calçada','calcada','chile'))}
road_indices=set(range(len(me.materials)))-allowed
def road_points(mesh):
    ids={i for p in mesh.polygons if p.material_index in road_indices for i in p.vertices}
    return {tuple(round(c,5) for c in mesh.vertices[i].co) for i in ids}
road_before=road_points(me)
R=Matrix(r['tower_alignment']['rotation_world']);RI=R.inverted();rear=r['tower_alignment']['sea_face_x_from_upper_wall_m'];cy=r['tower_alignment']['center_y_from_upper_floor_m']
survey=json.loads((root/'artifacts/palacio-rio-branco/support_ground_r35.json').read_text(encoding='utf8'))
anchors=[{'y':s['y'],'z30':next(p['z'] for p in s['samples'] if p['x']==-30),'z22':next(p['z'] for p in s['samples'] if p['x']==-22),'z20':next(p['z'] for p in s['samples'] if p['x']==-20)} for s in survey]
def line_z(y,key):
    if y<=anchors[0]['y']:return anchors[0][key]
    if y>=anchors[-1]['y']:return anchors[-1][key]
    for a,b in zip(anchors,anchors[1:]):
        if a['y']<=y<=b['y']:return a[key]+(b[key]-a[key])*(y-a['y'])/(b['y']-a['y'])
def ease(v):v=max(0,min(1,v));return v*v*(3-2*v)
domains=[]
for s in r['galleries']['segments']:
    domains.append({'name':s['name'],'kind':'gallery','p':Vector(s['origin_world']),'u':Vector(s['along_world']),'n':Vector(s['outward_world']),'x0':0,'x1':s['length_from_existing_controls_m'],'y0':-s['depth_candidate_m']-.15,'y1':0,'floor_z':s['origin_world'][2]-.22})
domains.append({'name':'Apoio Cidade Alta','kind':'support','p':Vector((0,0,0)),'u':R@Vector((1,0,0)),'n':R@Vector((0,1,0)),'x0':-30,'x1':rear+.25,'y0':cy-5.47,'y1':cy+5.47})
rows=[]
for name in r['terrain_names']:
    o=scene.objects[name];o.data=o.data.copy();mesh=o.data;M=wm(o);I=M.inverted();before=sig(o)
    coords=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',coords);mat=np.array(M,dtype=np.float64);world=coords.reshape((-1,3))@mat[:3,:3].T+mat[:3,3]
    loops=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('vertex_index',loops);starts=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('loop_start',starts)
    indices=[]
    for d in domains:
        delta=world-np.array(d['p']);x=delta@np.array(d['u']);y=delta@np.array(d['n'])
        mask=(x>d['x0']-2)&(x<d['x1']+2)&(y>d['y0']-2)&(y<d['y1']+2)
        indices.append(np.flatnonzero(np.logical_or.reduceat(mask[loops],starts)))
    bm=bmesh.new();bm.from_mesh(mesh);bm.faces.ensure_lookup_table();regions=[{bm.faces[int(i)] for i in ids} for ids in indices]
    cache={}
    def permitted(f):
        if o==source:return f.material_index in allowed
        if f not in cache:
            w=M@f.calc_center_median();hit=bvh.ray_cast(Vector((w.x,w.y,150)),Vector((0,0,-1)),240)
            cache[f]=hit[0] is not None and tri_materials[hit[2]] in allowed
        return cache[f]
    locked={v for f in bm.faces if o==source and f.material_index not in allowed for v in f.verts}
    splits=0
    for d,region in zip(domains,regions):
        for axis,value in ((d['u'],d['x0']),(d['u'],d['x1']),(d['n'],d['y0']),(d['n'],d['y1'])):
            faces=[f for f in region if f.is_valid and permitted(f)]
            if not faces:continue
            geom=set(faces)
            for f in faces:geom.update(f.edges);geom.update(f.verts)
            result=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(d['p']+axis*value),plane_no=M.to_3x3().transposed()@axis,clear_inner=False,clear_outer=False)
            splits+=len(result['geom_cut'])
            for item in result['geom_cut']:
                if isinstance(item,bmesh.types.BMEdge):region.update(item.link_faces)
                elif isinstance(item,bmesh.types.BMVert):region.update(item.link_faces)
        if d['kind']=='support':
            faces=[f for f in region if f.is_valid and permitted(f)];geom=set(faces)
            for f in faces:geom.update(f.edges);geom.update(f.verts)
            result=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(d['u']*rear),plane_no=M.to_3x3().transposed()@d['u'],clear_inner=False,clear_outer=False)
            for item in result['geom_cut']:
                if hasattr(item,'link_faces'):region.update(item.link_faces)
    for region in regions:
        locked.update(v for f in region if f.is_valid and not permitted(f) for v in f.verts)
    changed={};maximum=0
    for d,region in zip(domains,regions):
        vertices={v for f in region if f.is_valid for v in f.verts};count=0
        for v in vertices:
            if v in locked:continue
            w=M@v.co;delta=w-d['p'];x=delta.dot(d['u']);y=delta.dot(d['n'])
            if not(d['x0']-.0001<=x<=d['x1']+.0001 and d['y0']-.0001<=y<=d['y1']+.0001):continue
            old_z=w.z
            if d['kind']=='gallery':
                if old_z<d['floor_z']:continue
                w.z=d['floor_z']
            else:
                if x<=-22:z=line_z(y,'z30')+(line_z(y,'z22')-line_z(y,'z30'))*(x+30)/8
                else:z=line_z(y,'z22')+(line_z(y,'z20')-line_z(y,'z22'))*min(1,(x+22)/(rear+22))
                weight=ease(min((y-d['y0'])/2,(d['y1']-y)/2))
                if x>rear:weight*=1-ease((x-rear)/.25)
                w.z=old_z+(z-old_z)*weight
            if abs(w.z-old_z)<.00001:continue
            maximum=max(maximum,abs(w.z-old_z));v.co=I@w;count+=1
        changed[d['name']]=count
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
    o['r35_profile_reason']='Galerias escavadas sob laje; encosta recomposta entre perfil amostrado da ladeira e face do apoio alinhado. Sem alterar DEM-fonte ou pista.'
    rows.append({'object':name,'before':before,'after':sig(o),'changed_vertices_by_region':changed,'max_abs_z_delta_m':maximum,'bisect_elements':splits})
missing=road_before-road_points(source.data);assert not missing,'Pista alterada: '+str(len(missing))
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items()),'Mudança fora do escopo'
r['terrain_stage']='applied_candidate';r['status']='modeling_candidate';r['terrain_refinement']={'geometry':rows,'source_road_positions_preserved':len(road_before),'missing_road_positions':0,'source_DEM_or_global_Z_changed':False,'support_profile_anchors':anchors,'support_profile_classification':'ADAPT_LOCAL','support_profile_reason':'Elimina depressão da implantação antiga e abre a face do apoio; interpolação entre amostras existentes (-30,-22,-20) com encontro na estrutura. Não representa levantamento topográfico.','gallery_depth_candidate_m':4.2,'gallery_floor_clearance_m':.22,'plaza_top_supported_by_separate_slabs':True,'runtime_validation':'pending','visual_review':'pending'}
scene['architecture_revision']='R30B.35 | apoio alinhado, galerias escavadas e encosta recomposta'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source_after':r['source_after'],'terrain':[(x['object'],x['changed_vertices_by_region']) for x in rows],'road_positions_preserved':len(road_before)},ensure_ascii=False))
