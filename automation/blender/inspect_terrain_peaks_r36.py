"""Localiza vértices presos na interface terreno/circulação do passe R36."""
import bpy,json,runpy
import numpy as np
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2];r=json.loads((root/'docs/reports/blender/terracos_palacio_r30b36.json').read_text(encoding='utf8'));wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix'];S=Matrix(r['layout']['frame_world']);SI=S.inverted();rows=[]
for item in r['terrain']:
    o=bpy.context.scene.objects[item['object']];me=o.data;v=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',v);A=np.array(SI@wm(o));local=v.reshape((-1,3))@A[:3,:3].T+A[:3,3]
    # Local do pico visível diante das galerias e dentro da colunata.
    ids=np.flatnonzero((local[:,0]>2)&(local[:,0]<54)&(local[:,1]>0)&(local[:,1]<34)&(local[:,2]>51))
    idx=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',idx);starts=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('loop_start',starts);marked=np.zeros(len(me.vertices),dtype=bool);marked[ids]=True;faces=np.flatnonzero(np.logical_or.reduceat(marked[idx],starts));adj={int(i):set() for i in ids}
    for fi in faces:
        f=me.polygons[int(fi)]
        for vid in f.vertices:
            if vid in adj:adj[vid].add(f.material_index)
    knots=r['garden_profile_refinement']['profile_candidate_y_z'];expected=np.interp(local[ids,1],[k[0] for k in knots],[k[1] for k in knots]);errors=local[ids,2]-expected
    worst=[]
    for j in np.argsort(-errors)[:40]:
        vid=int(ids[j]);worst.append({'vertex':vid,'local':local[vid].tolist(),'profile_excess':float(errors[j]),'materials':[me.materials[i].name if i<len(me.materials) else str(i) for i in adj[vid]]})
    rows.append({'object':o.name,'worst':worst})
out=root/'artifacts/palacio-rio-branco/terrain_peaks_r36.json';out.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{'object':x['object'],'worst':x['worst'][:12]} for x in rows],ensure_ascii=False))
