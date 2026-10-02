"""Localiza a dobra residual visível no encontro, sem alterar a cena."""
import bpy,json,runpy
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];r=json.loads((root/'docs/reports/blender/terracos_palacio_r30b36.json').read_text(encoding='utf8'));S=Matrix(r['layout']['frame_world']);SI=S.inverted();wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
o=bpy.context.scene.objects[r['terrain'][0]['object']];me=o.data;M=wm(o);raw=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',raw);A=np.array(SI@M);lp=raw.reshape((-1,3))@A[:3,:3].T+A[:3,3];me.calc_loop_triangles();ii=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',ii);ii=ii.reshape((-1,3));p=lp[ii];ids=np.flatnonzero((p[:,:,0].max(1)>2)&(p[:,:,0].min(1)<55)&(p[:,:,1].max(1)>0)&(p[:,:,1].min(1)<40));selected=ii[ids];used,inv=np.unique(selected,return_inverse=True);b=BVHTree.FromPolygons([M@me.vertices[int(i)].co for i in used],inv.reshape((-1,3)).tolist(),all_triangles=True)
eye=S@Vector((48,45,79));target=S@Vector((26,5,65));q=(target-eye).to_track_quat('-Z','Y');rows=[]
for px,py in ((299,423),(324,463),(333,492),(301,443),(320,434)):
    ray=q@Vector(((2*px/900-1)*.45,(1-2*py/650)*.325,-1));hit=b.ray_cast(eye,ray.normalized(),150)
    if hit[0] is None:continue
    t=me.loop_triangles[int(ids[hit[2]])];f=me.polygons[t.polygon_index];segments=[]
    for s in (r['preserved_gallery_connection']['segment'],r['access_connection_correction']['gallery_before']):
        d=hit[0]-Vector(s['origin_world']);segments.append({'name':s['name'],'x':d.dot(Vector(s['along_world'])),'y':d.dot(Vector(s['outward_world'])),'length':s['length_from_existing_controls_m']})
    rows.append({'pixel':[px,py],'local':list(SI@hit[0]),'face':f.index,'material':me.materials[f.material_index].name,'vertices':[{'id':int(i),'local':lp[int(i)].tolist()} for i in f.vertices],'segments':segments})
(root/'artifacts/palacio-rio-branco/gallery_seam_r36.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(rows,ensure_ascii=False))
