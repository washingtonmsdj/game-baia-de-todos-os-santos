"""Fecha o perfil local do talude em todos os vértices, sem alterar as vias."""
import bpy,json,runpy,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));scene=bpy.context.scene
assert 'opening_finish' in r and 'complete_gallery_slope' not in r
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix']
source=scene.objects[r['terrain'][0]['object']]
allowed={i for i,m in enumerate(source.data.materials) if m and any(k in m.name.lower() for k in ('terreno','encosta','conten','solo e vegetação')) and not any(k in m.name.lower() for k in ('asfalto','passeio','pedonal','chile'))}
def roads():
    return {tuple(round(k,5) for k in source.data.vertices[v].co) for f in source.data.polygons if f.material_index not in allowed for v in f.vertices}
road_before=roads();rows=[]
segments=[r['preserved_gallery_connection']['segment'],r['access_connection_correction']['gallery_before']]
for item in r['terrain']:
    o=scene.objects[item['object']];me=o.data;M=wm(o);A=np.array(M);I=np.array(M.inverted());before=sig(o)
    raw=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',raw);coords=raw.reshape((-1,3));world=coords@A[:3,:3].T+A[:3,3];target=world[:,2].copy()
    movable=np.ones(len(me.vertices),dtype=bool)
    if o==source:
        ids=sorted({v for f in me.polygons if f.material_index not in allowed for v in f.vertices});movable[ids]=False
    counts=[]
    for s,control in zip(segments,r['final_slope_profile']['road_edge_controls']):
        anchors=np.array(control['anchors_local_t_distance_z']);p=np.array(s['origin_world']);u=np.array(s['along_world']);n=np.array(s['outward_world']);d=world-p;xx=d@u;yy=d@n;L=s['length_from_existing_controls_m']
        edge=np.interp(xx,anchors[:,0],anchors[:,1]);edgez=np.interp(xx,anchors[:,0],anchors[:,2]);split=np.maximum(1,edge-3.2);upper=p[2]-.22;low=edgez+5.5
        desired=np.where(yy<=.7,upper,np.where(yy<=split,upper+(low-upper)*(yy-.7)/np.maximum(.1,split-.7),low+(edgez-low)*(yy-split)/np.maximum(.1,edge-split)))
        left=np.clip((xx+.3)/.3,0,1);right=np.clip((L+.3-xx)/.3,0,1);weight=left*left*(3-2*left)*right*right*(3-2*right)
        mask=movable&(xx>=-.3)&(xx<=L+.3)&(yy>=-.001)&(yy<edge-.001)
        value=world[:,2]+(np.minimum(world[:,2],desired)-world[:,2])*weight
        mask&=value<target-1e-5;counts.append(int(mask.sum()));target[mask]=value[mask]
    changed=np.flatnonzero(np.abs(target-world[:,2])>1e-5);world[changed,2]=target[changed];coords[changed]=world[changed]@I[:3,:3].T+I[:3,3]
    me.vertices.foreach_set('co',coords.astype(np.float32).ravel());me.update();item['after']=sig(o);rows.append({'object':o.name,'before':before,'after':item['after'],'changed_vertices':len(changed),'changed_by_segment':counts})
assert roads()==road_before,'Vértices de circulação alterados'
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items()),'Galeria ou estrutura protegida mudou'
r['complete_gallery_slope']={'classification':'ADAPT_LOCAL','reason':'Vértices de faces recém-divididas escapavam ao conjunto temporário de edição e mantinham picos. Aplicado o mesmo perfil local existente a todos os vértices elegíveis, entre a fachada e a borda amostrada da ladeira. Nenhuma arquitetura deslocada.','terrain':rows,'road_positions_preserved':len(road_before),'road_width_xy_dem_changed':False,'actual_survey':None,'visual_review':'pending'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'changed':[t['changed_vertices'] for t in rows],'saved':r['source_after']},ensure_ascii=False))
