"""Escava o volume real da colunata inferior sem usar uma fachada para ocultar solo."""
import bpy,bmesh,json,runpy,hashlib
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));scene=bpy.context.scene
assert 'gallery_slope_surface' in r and 'colonnade_soil_volume' not in r
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];S=Matrix(r['layout']['frame_world']);SI=S.inverted();x0,x1,y0,y1=r['layout']['colonnade_extent_candidate'];z0=r['layout']['colonnade_floor_candidate_m']-.15;z1=r['layout']['colonnade_roof_candidate_m']-.30;lo=np.array((x0-.1,y0-.1,z0));hi=np.array((x1+.1,y1+.1,z1));source=scene.objects[r['terrain'][0]['object']]
allowed={i for i,m in enumerate(source.data.materials) if m and any(k in m.name.lower() for k in ('terreno','encosta','conten','solo e vegetação')) and not any(k in m.name.lower() for k in ('asfalto','passeio','pedonal','chile'))}
def roads():
    ids={v for f in source.data.polygons if f.material_index not in allowed for v in f.vertices}
    return {tuple(round(k,5) for k in source.data.vertices[i].co) for i in ids}
protected=roads();rows=[]
for item in r['terrain']:
    o=scene.objects[item['object']];me=o.data;M=wm(o);I=M.inverted();before=sig(o);v=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',v);A=np.array(SI@M);local=v.reshape((-1,3))@A[:3,:3].T+A[:3,3];idx=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',idx);starts=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('loop_start',starts);mask=np.ones(len(me.polygons),dtype=bool)
    for axis in range(3):mask&=(np.maximum.reduceat(local[idx,axis],starts)>lo[axis])&(np.minimum.reduceat(local[idx,axis],starts)<hi[axis])
    if o==source:
        mi=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',mi);mask&=np.isin(mi,list(allowed))
    bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();region={bm.faces[int(i)] for i in np.flatnonzero(mask)}
    for axis in range(3):
        for value in (lo[axis],hi[axis]):
            faces=[f for f in region if f.is_valid and (o!=source or f.material_index in allowed)];geom=set(faces)
            for f in faces:geom.update(f.edges);geom.update(f.verts)
            point=Vector((0,0,0));point[axis]=float(value);normal=S.col[axis].xyz
            out=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=1e-5,plane_co=I@(S@point),plane_no=M.to_3x3().transposed()@normal,clear_inner=False,clear_outer=False)
            for e in out['geom']+out['geom_cut']:
                if isinstance(e,bmesh.types.BMFace):region.add(e)
                elif hasattr(e,'link_faces'):region.update(e.link_faces)
    doomed=[]
    for f in region:
        if not f.is_valid or (o==source and f.material_index not in allowed):continue
        p=np.array(SI@(M@f.calc_center_median()))
        if np.all(p>lo-1e-5) and np.all(p<hi+1e-5):doomed.append(f)
    removed=len(doomed);bmesh.ops.delete(bm,geom=doomed,context='FACES');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();item['after']=sig(o);rows.append({'object':o.name,'before':before,'after':item['after'],'soil_faces_removed':removed})
assert roads()==protected,'Via alterada'
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
r['colonnade_soil_volume']={'classification':'ADAPT_LOCAL','reason':'Faces antigas atravessavam a colunata sem conter um vértice interno. Seleção por interseção de limites, cortes nos seis planos e retirada do solo dentro do volume; pisos/lajes/colliders próprios preservados.','bounds_local':[lo.tolist(),hi.tolist()],'terrain':rows,'road_positions_preserved':len(protected),'road_width_xy_dem_changed':False,'visual_review':'pending'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'removed':[t['soil_faces_removed'] for t in rows],'saved':r['source_after']},ensure_ascii=False))
