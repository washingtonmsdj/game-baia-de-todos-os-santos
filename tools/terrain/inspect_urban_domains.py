import json,numpy as np
from pathlib import Path
r=Path('.')
j=json.loads((r/'artifacts/waterfront/urban_scene_b62.json').read_text(encoding='utf8'))
q=np.array(j['quay_vertices']);print('quay first',q[:12].tolist());print('quay last',q[-12:].tolist())
for k,rd,pd in [('core',[2,5],[1,3,4,7]),('hq',[3,4],[5])]:
 a=np.load(r/f'artifacts/waterfront/urban_{k}_b62.npz');m=a['materials'];li=a['loop_edges'];loopmat=np.repeat(m,a['counts']);erc=np.bincount(li[np.isin(loopmat,rd)],minlength=len(a['edges']));epc=np.bincount(li[np.isin(loopmat,pd)],minlength=len(a['edges']));bs=np.where((erc>0)&(epc>0))[0];v=a['vertices'];ed=a['edges'][bs];lens=np.linalg.norm(v[ed[:,0]]-v[ed[:,1]],axis=1);print(k,'road/ped boundaries',len(bs),'length',float(lens.sum()),'matcounts',dict(zip(*np.unique(m,return_counts=True))))
ls=json.loads((r/'artifacts/waterfront/urban_landscape_source.json').read_text(encoding='utf8'));print('landscape',[(f['osm_id'],f['tags'],f['bbox']) for f in ls['features']])
ref=json.loads((r/'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json').read_text())
print('roads along gap',[(f['osm_id'],f['tags'].get('name'),f['blender_xy'][:2]) for f in ref['features'] if f['layer']=='roads' and any(-388<p[0]<-285 and -95<p[1]<334 for p in f['blender_xy'])])
