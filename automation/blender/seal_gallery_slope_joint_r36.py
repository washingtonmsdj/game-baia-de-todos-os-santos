"""Perfil contínuo no encontro angular entre galeria original e ligação R36."""
import bpy,json,runpy,hashlib,math
import numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));scene=bpy.context.scene
assert 'complete_gallery_slope' in r and 'gallery_slope_joint' not in r
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];source=scene.objects[r['terrain'][0]['object']]
allowed={i for i,m in enumerate(source.data.materials) if m and any(k in m.name.lower() for k in ('terreno','encosta','conten','solo e vegetação')) and not any(k in m.name.lower() for k in ('asfalto','passeio','pedonal','chile'))}
roadids=sorted({v for f in source.data.polygons if f.material_index not in allowed for v in f.vertices});road_before=[tuple(source.data.vertices[i].co) for i in roadids]
segments=[r['preserved_gallery_connection']['segment'],r['access_connection_correction']['gallery_before']];angle=math.acos(float(np.clip(np.dot(segments[0]['along_world'],segments[1]['along_world']),-1,1)));tangent=math.tan(angle);rows=[]
for item in r['terrain']:
    o=scene.objects[item['object']];me=o.data;M=wm(o);A=np.array(M);I=np.array(M.inverted());before=sig(o);raw=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',raw);co=raw.reshape((-1,3));world=co@A[:3,:3].T+A[:3,3];target=world[:,2].copy();movable=np.ones(len(me.vertices),dtype=bool)
    if o==source:movable[roadids]=False
    for j,(s,control) in enumerate(zip(segments,r['final_slope_profile']['road_edge_controls'])):
        a=np.array(control['anchors_local_t_distance_z']);d=world-np.array(s['origin_world']);xx=d@np.array(s['along_world']);yy=d@np.array(s['outward_world']);L=s['length_from_existing_controls_m'];edge=np.interp(xx,a[:,0],a[:,1]);edgez=np.interp(xx,a[:,0],a[:,2]);split=np.maximum(1,edge-3.2);upper=s['origin_world'][2]-.22;low=edgez+5.5
        desired=np.where(yy<=.7,upper,np.where(yy<=split,upper+(low-upper)*(yy-.7)/np.maximum(.1,split-.7),low+(edgez-low)*(yy-split)/np.maximum(.1,edge-split)))
        # Os taludes se encontram em uma quina: estender os planos até sua
        # interseção, sem misturar com o pico legado nos extremos compartilhados.
        extension=np.maximum(0,yy)*tangent+.35
        if j==0:mask=(xx>=0)&(xx<=L+extension)&(xx>=L-extension-.5)
        else:mask=(xx>=-extension)&(xx<=extension+.5)&(xx<=L)
        mask&=movable&(yy>=0)&(yy<edge-.001);target[mask]=np.minimum(target[mask],desired[mask])
    changed=np.flatnonzero(np.abs(target-world[:,2])>1e-5);world[changed,2]=target[changed];co[changed]=world[changed]@I[:3,:3].T+I[:3,3];me.vertices.foreach_set('co',co.astype(np.float32).ravel());me.update();item['after']=sig(o);rows.append({'object':o.name,'before':before,'after':item['after'],'changed_vertices':len(changed)})
assert [tuple(source.data.vertices[i].co) for i in roadids]==road_before,'Via alterada'
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
r['gallery_slope_joint']={'classification':'ADAPT_LOCAL','reason':'Extremos de duas bandas angulares deixavam um pico entre os perfis. Fechado o encontro pelos planos de talude derivados das fachadas e borda existente da pista, sem deslocar galerias.','angle_radians':angle,'terrain':rows,'road_positions_preserved':len(roadids),'road_width_xy_dem_changed':False,'visual_review':'pending'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'changed':[t['changed_vertices'] for t in rows],'saved':r['source_after']},ensure_ascii=False))
