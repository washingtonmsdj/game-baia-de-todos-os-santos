"""B58: elimina superfície duplicada e costura HQ ao limite físico do núcleo."""
import bpy, json, math, hashlib, runpy
from pathlib import Path
from mathutils import Vector, Euler
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
catalog_path = root / 'world/areas/mvp-centro-lacerda/blender-revisions.json'
catalog = json.loads(catalog_path.read_text(encoding='utf8'))
source = catalog['validation_source']
assert source['revision'] == 'R30B.57'
assert Path(bpy.data.filepath).resolve() == (root/source['file']).resolve()
output = root/'blender/salvador_lacerda_r30b58_costura_encosta_gameplay.blend'
assert not output.exists()
signature = runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
ground = scene.objects['MVP | terreno corrigido | colisão estática']
protected_objects = [ground, scene.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'], scene.objects['CAIS | contenção costeira alinhada à linha de costa']]
protected_objects += [o for o in scene.objects if o.name.startswith(('B56 | COLLISION | PIER |', 'B57 | PIER VISUAL |'))]
protected = {o.name: signature(o) for o in protected_objects}
ground.data.calc_loop_triangles()
tree = BVHTree.FromPolygons([ground.matrix_world@v.co for v in ground.data.vertices], [list(t.vertices) for t in ground.data.loop_triangles], all_triangles=True)
def floor(x,y):
    hit = tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400)[0]
    return None if hit is None else float(hit.z)

xcut = min((ground.matrix_world@Vector(v)).x for v in ground.bound_box)
lo,hi = -290.0,-280.0
assert floor(xcut+.01,lo) is None and floor(xcut+.01,hi) is not None
for _ in range(32):
    mid = (lo+hi)/2
    if floor(xcut+.01,mid) is None: lo=mid
    else: hi=mid
ycut=hi
# A geometria do núcleo deve cobrir o retângulo que será removido, sem atalhos
# que presumam que um bounding box é uma superfície real.
coverage=[]
for k in range(math.ceil((9.75-ycut)/.75)+1):
    y=min(9.75,ycut+.002+k*.75)
    for x in (xcut+.002,-284.,-275.,-261.):
        if floor(x,y) is None: coverage.append((x,y))
assert not coverage, ('Cobertura irregular; não recortar automaticamente',coverage[:10])

def clip(poly,axis,value,keep_less):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ina=a[axis]<=value if keep_less else a[axis]>=value
        inb=b[axis]<=value if keep_less else b[axis]>=value
        if ina: result.append(a)
        if ina != inb:
            t=(value-a[axis])/(b[axis]-a[axis])
            p=[a[q]+t*(b[q]-a[q]) for q in range(3)];p[axis]=value
            result.append(p)
    return result

collection=bpy.data.collections.new('39.1 GAMEPLAY | B58 COSTURA')
scene.collection.children.link(collection)
seam_deltas=[]
def rebuild(old,name,is_terrain=False):
    coords=[];faces=[];indices=[];smooth=[];lookup={};removed=0;split=0
    for face in old.data.polygons:
        points=[list(old.matrix_world@old.data.vertices[i].co) for i in face.vertices]
        pieces=[]
        if max(p[1] for p in points)<=ycut:pieces=[points]
        elif min(p[1] for p in points)>=ycut:
            p=clip(points,0,xcut,True)
            if len(p)>=3:pieces=[p]
        else:
            a=clip(points,1,ycut,True)
            b=clip(clip(points,1,ycut,False),0,xcut,True)
            pieces=[p for p in (a,b) if len(p)>=3]
        if not pieces:removed+=1
        if len(pieces)!=1 or (pieces and len(pieces[0])!=len(points)):split+=1
        for piece in pieces:
            ids=[]
            for p in piece:
                on_x=abs(p[0]-xcut)<1e-5 and p[1]>=ycut-1e-5
                on_y=abs(p[1]-ycut)<1e-5 and p[0]>=xcut-1e-5
                if on_x or on_y:
                    z=floor(max(xcut+.002,p[0]),max(ycut+.002,p[1]))
                    assert z is not None,(p,'Costura sem apoio')
                    target=z+(0 if is_terrain else .015)
                    if is_terrain:seam_deltas.append(abs(p[2]-target))
                    p[2]=target
                key=tuple(round(v,6) for v in p)
                if key not in lookup:lookup[key]=len(coords);coords.append(p)
                ids.append(lookup[key])
            if len(set(ids))<3:continue
            area=sum((Vector(coords[ids[q]])-Vector(coords[ids[0]])).cross(Vector(coords[ids[q+1]])-Vector(coords[ids[0]])).length/2 for q in range(1,len(ids)-1))
            if area<1e-10:continue
            faces.append(ids);indices.append(face.material_index);smooth.append(face.use_smooth)
    mesh=bpy.data.meshes.new(name+' | malha')
    mesh.from_pydata(coords,[],faces);mesh.update()
    for material in old.data.materials:mesh.materials.append(material)
    for p,mi,sm in zip(mesh.polygons,indices,smooth):p.material_index=mi;p.use_smooth=sm
    ob=bpy.data.objects.new(name,mesh);collection.objects.link(ob)
    for key in old.keys():ob[key]=old[key]
    ob['boas_revision']='R30B.58';ob['boas_gameplay_approved']=False
    old.hide_viewport=True;old.hide_render=True;old['boas_superseded_by']=ob.name
    return ob,{'source':old.name,'result':name,'removed_faces':removed,'split_faces':split,'vertices':len(coords),'faces':len(faces)}

terrain,row=rebuild(scene.objects['B57 | GAMEPLAY TERRAIN HQ | Aleph 0.75m'],'B58 | GAMEPLAY TERRAIN HQ | costura sem sobreposição',True)
collision=bpy.data.objects.new('B58 | COLLISION | terreno HQ costurado',terrain.data.copy())
collection.objects.link(collision);collision.hide_viewport=True;collision.hide_render=True
collision['boas_runtime_role']='terrain_collision';collision['boas_source_surface']=terrain.name
collision['boas_geometry_identical_to_visual']=True;collision['boas_gameplay_approved']=False
terrain['boas_collision_partner']=collision.name
scene.objects['B57 | COLLISION | terrain HQ 0.75m']['boas_superseded_by']=collision.name
roads=[]
for old in list(scene.objects):
    if old.name.startswith('B57 | ROAD VISUAL |'):
        ob,r=rebuild(old,old.name.replace('B57 |','B58 |',1))
        ob['boas_collision_source']=collision.name;roads.append(r)
changed=[n for n,b in protected.items() if signature(scene.objects[n])!=b]
assert not changed,changed
assert len(terrain.data.vertices)==len(collision.data.vertices)
assert all(math.isfinite(c) for v in terrain.data.vertices for c in v.co)
for ob in scene.objects:
    if ob.select_get():ob.select_set(False)
scene.camera=None
for win in bpy.context.window_manager.windows:
    for area in win.screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='PERSP'
            area.spaces.active.region_3d.view_location=Vector((-291,-170,22))
            area.spaces.active.region_3d.view_distance=230
            area.spaces.active.region_3d.view_rotation=Euler((math.radians(55),0,math.radians(-35)),'XYZ').to_quaternion()
scene['boas_validation_revision']='R30B.58'
scene['boas_b58_correction']='ERROR: duplicação da HQ no domínio do terreno validado; costura ancorada à superfície preservada.'
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
sha=hashlib.file_digest(output.open('rb'),'sha256').hexdigest()
report={'schema':'boas/coastal-seam-b58-v1','source_before':source,'source_after':{'file':output.relative_to(root).as_posix(),'revision':'R30B.58','sha256':sha},'classification':'ERROR','terrain':row,'roads':roads,'physical_boundary_xy':{'x':xcut,'y':ycut},'core_coverage_missing':coverage,'seam_vertex_max_adjustment_m':max(seam_deltas,default=0),'visual_collision_identical':True,'protected_changes':changed,'runtime_exported':False,'approved':False,'pending':['Reabertura e inspeção visual','Preenchimento de lacunas restantes entre o limite histórico e o cais','Travessia física na engine ainda não integrada']}
report_path=root/'docs/reports/blender/coastal_seam_r30b58.json'
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={**report['source_after'],'status':'validation_candidate','parent_file':source['file'],'evidence':report_path.relative_to(root).as_posix(),'notes':'Remove duplicação HQ no núcleo preservado e ancora costura física; visual/colisão correspondentes; não promove runtime.'}
for r in catalog['revisions']:
    if r['file']==source['file']:r['status']='superseded_validation'
catalog['revisions'].append(entry);catalog['validation_source']=entry.copy()
catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'R30B.58','terrain':row,'roads':len(roads),'seam_max_adjustment':report['seam_vertex_max_adjustment_m'],'protected_changes':changed},ensure_ascii=False))
