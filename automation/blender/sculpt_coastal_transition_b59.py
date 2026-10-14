"""B59: remodela a faixa de encosta, conservando o núcleo e os eixos XY."""
import bpy, bmesh, numpy as np, json, math, hashlib, runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
cp=root/'world/areas/mvp-centro-lacerda/blender-revisions.json'
catalog=json.loads(cp.read_text(encoding='utf8'));src=catalog['validation_source']
assert src['revision']=='R30B.58' and Path(bpy.data.filepath).resolve()==(root/src['file']).resolve()
out=root/'blender/salvador_lacerda_r30b59_encosta_transicao_continua.blend';assert not out.exists()
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
ground=scene.objects['MVP | terreno corrigido | colisão estática']
protected_names=[ground.name,'BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro','CAIS | contenção costeira alinhada à linha de costa']+[o.name for o in scene.objects if o.name.startswith(('B56 | COLLISION | PIER |','B57 | PIER VISUAL |'))]
protected={n:sig(scene.objects[n]) for n in protected_names}
ground.data.calc_loop_triangles()
core=BVHTree.FromPolygons([ground.matrix_world@v.co for v in ground.data.vertices],[list(t.vertices) for t in ground.data.loop_triangles],all_triangles=True)
def core_z(x,y):
    p=core.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400)[0]
    return None if p is None else float(p.z)
data=np.load(root/'artifacts/waterfront/coastal_visual_hq_b57.npz')
gx=data['gx'];gy=data['gy'];original=data['H'].copy();H=original.copy();mask=np.isfinite(H)&data['mask'];road=data['road_weight'];under=data['underwater']
seam=json.loads((root/'docs/reports/blender/coastal_seam_r30b58.json').read_text(encoding='utf8'))['physical_boundary_xy'];xc=seam['x'];yc=seam['y']
# Relaxamento local de chapa DEM escalonada: não suaviza a superfície oficial,
# não modifica a fonte DEM, mantém fundo e as plataformas de via da candidata.
free=mask&(road<.05)&(~under)
for _ in range(24):
    total=np.zeros_like(H);count=np.zeros_like(H)
    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
        shifted=np.roll(H,(dy,dx),(0,1));valid=np.roll(mask,(dy,dx),(0,1))
        if dy==1:valid[0,:]=False
        if dy==-1:valid[-1,:]=False
        if dx==1:valid[:,0]=False
        if dx==-1:valid[:,-1]=False
        total+=np.where(valid,shifted,0);count+=valid
    avg=total/np.maximum(count,1)
    H[free]=.65*H[free]+.35*avg[free]
H[mask]=np.clip(H[mask],original[mask]-2.,original[mask]+2.)
def sample(grid,x,y):
    fi=(x-gx[0])/.75;fj=(y-gy[0])/.75
    i=min(len(gx)-2,max(0,int(math.floor(fi))));j=min(len(gy)-2,max(0,int(math.floor(fj))))
    tx=max(0,min(1,fi-i));ty=max(0,min(1,fj-j))
    values=[grid[j,i],grid[j,i+1],grid[j+1,i],grid[j+1,i+1]]
    weights=[(1-tx)*(1-ty),tx*(1-ty),(1-tx)*ty,tx*ty]
    pairs=[(float(v),w) for v,w in zip(values,weights) if math.isfinite(v) and w>1e-12]
    if not pairs:return None
    return sum(v*w for v,w in pairs)/sum(w for _,w in pairs)
col=bpy.data.collections.new('39.2 GAMEPLAY | B59 ENCOSTA');scene.collection.children.link(col)
old=scene.objects['B58 | GAMEPLAY TERRAIN HQ | costura sem sobreposição']
terrain=old.copy();terrain.data=old.data.copy();terrain.name='B59 | GAMEPLAY TERRAIN HQ | encosta contínua';col.objects.link(terrain)
cache={};changed=0;max_delta=0;seam_error=0
for v in terrain.data.vertices:
    x,y,previous=map(float,v.co);base=sample(H,x,y)
    if base is None:base=previous
    dx=max(0,xc-x);dy=max(0,yc-y);distance=math.hypot(dx,dy)
    if distance<75:
        ax=max(x,xc+.002);ay=max(y,yc+.002)
        key=(round(ax,4),round(ay,4))
        if key not in cache:cache[key]=core_z(ax,ay)
        target=cache[key];reference=sample(H,ax,ay)
        if target is not None and reference is not None:
            t=distance/75.;weight=1-3*t*t+2*t*t*t
            base+=(target-reference)*weight
        if distance<1e-4 and target is not None:base=target;seam_error=max(seam_error,abs(base-target))
    delta=abs(base-previous);changed+=delta>1e-5;max_delta=max(max_delta,delta);v.co.z=base
terrain.data.update();terrain['boas_revision']='R30B.59';terrain['boas_gameplay_approved']=False
# Recalcula classificação solo/rocha a partir da nova superfície física.
for face in terrain.data.polygons:
    slope=math.degrees(math.acos(min(1,max(-1,face.normal.z))))
    face.material_index=2 if slope>=35 else (1 if slope>=18 or face.center.z<.3 else 0)
    face.use_smooth=True
collision=bpy.data.objects.new('B59 | COLLISION | terreno encosta contínua',terrain.data.copy());col.objects.link(collision)
collision.hide_viewport=True;collision.hide_render=True;collision['boas_runtime_role']='terrain_collision'
collision['boas_source_surface']=terrain.name;collision['boas_geometry_identical_to_visual']=True;collision['boas_gameplay_approved']=False
terrain['boas_collision_partner']=collision.name
old.hide_viewport=True;old.hide_render=True;old['boas_superseded_by']=terrain.name
scene.objects['B58 | COLLISION | terreno HQ costurado']['boas_superseded_by']=collision.name
terrain.data.calc_loop_triangles()
tree=BVHTree.FromPolygons([v.co for v in terrain.data.vertices],[list(t.vertices) for t in terrain.data.loop_triangles],all_triangles=True)
roads=[]
for previous in list(scene.objects):
    if not previous.name.startswith('B58 | ROAD VISUAL |'):continue
    if not len(previous.data.polygons):continue
    ob=previous.copy();ob.data=previous.data.copy();ob.name=previous.name.replace('B58 |','B59 |',1);col.objects.link(ob)
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=3,use_grid_fill=True)
    bm.to_mesh(ob.data);bm.free();missing=0
    for v in ob.data.vertices:
        hit=tree.ray_cast(Vector((v.co.x,v.co.y,200)),Vector((0,0,-1)),400)[0]
        if hit is None:
            z=core_z(v.co.x,v.co.y)
            if z is None:missing+=1;continue
        else:z=float(hit.z)
        v.co.z=z+.015
    assert missing==0,(ob.name,missing)
    ob.data.update();ob['boas_revision']='R30B.59';ob['boas_collision_source']=collision.name
    ob['boas_adaptation']='ADAPT_LOCAL: drape vertical da via candidata na transição remodelada; XY/largura preservados.'
    previous.hide_render=True;previous.hide_viewport=True;previous['boas_superseded_by']=ob.name
    roads.append({'object':ob.name,'vertices':len(ob.data.vertices),'support_missing':missing})
assert not [n for n,s in protected.items() if sig(scene.objects[n])!=s]
assert all(math.isfinite(c) for v in terrain.data.vertices for c in v.co)
changed=int(changed)
scene['boas_validation_revision']='R30B.59'
scene['boas_b59_adaptation']='ADAPT_LOCAL: escarpa costeira ancorada ao núcleo, faixa até 75m; DEM-fonte, vias do núcleo e costa preservados.'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.file_digest(out.open('rb'),'sha256').hexdigest()
report={'schema':'boas/coastal-sculpt-b59-v1','source_before':src,'source_after':{'file':out.relative_to(root).as_posix(),'revision':'R30B.59','sha256':sha},'classification':'ADAPT_LOCAL','collar_max_width_m':75,'relaxation_max_m':2,'changed_vertices':changed,'max_local_vertical_change_m':max_delta,'seam_error_m':seam_error,'visual_collision_identical':True,'road_surfaces':roads,'protected_changes':[],'source_dem_modified':False,'source_xy_changed':False,'runtime_exported':False,'approved':False,'pending':['Auditar continuidade física e declividade das vias candidatas','Fechar lacuna histórica até o cais','Validar reabertura e aparência']}
rp=root/'docs/reports/blender/coastal_sculpt_r30b59.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
e={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(root).as_posix(),'notes':'Remodelagem de transição costeira, superfícies visuais e colisão iguais, vias candidatas redrapeadas; núcleo preservado; falta gate de circulação.'}
for r in catalog['revisions']:
    if r['file']==src['file']:r['status']='superseded_validation'
catalog['revisions'].append(e);catalog['validation_source']=e.copy();cp.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'R30B.59','changed_vertices':changed,'max_vertical_change_m':max_delta,'seam_error_m':seam_error,'roads':len(roads),'protected_changes':[]},ensure_ascii=False))
