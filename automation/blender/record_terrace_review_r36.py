"""Conferência local, relatório e enquadramento; sem exportar runtime."""
import bpy,json,runpy,hashlib
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));scene=bpy.context.scene
assert 'opening_finish' in r and Path(bpy.data.filepath).resolve()==(root/r['source_after']['file']).resolve()
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];S=Matrix(r['layout']['frame_world']);SI=S.inverted();rooms=[r['preserved_gallery_connection']['segment'],r['access_connection_correction']['gallery_before']];samples=[]
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
def cropped_bvh(o):
    me=o.data;M=wm(o);v=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',v);A=np.array(SI@M);local=v.reshape((-1,3))@A[:3,:3].T+A[:3,3];me.calc_loop_triangles();idx=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',idx);idx=idx.reshape((-1,3));pts=local[idx];mask=(pts[:,:,0].max(axis=1)>1)&(pts[:,:,0].min(axis=1)<56)&(pts[:,:,1].max(axis=1)>-2)&(pts[:,:,1].min(axis=1)<34);selected=idx[mask];used,inv=np.unique(selected,return_inverse=True)
    return BVHTree.FromPolygons([M@me.vertices[int(i)].co for i in used],inv.reshape((-1,3)).tolist(),all_triangles=True)
for item in r['terrain']:
    o=scene.objects[item['object']];b=cropped_bvh(o);checks=[]
    for s in rooms:
        p,u,n=Vector(s['origin_world']),Vector(s['along_world']),Vector(s['outward_world']);pitch=s['length_from_existing_controls_m']/s['arch_count']
        for j in range(s['arch_count']):
            for depth in (.35,2.,s['depth_candidate_m']-.35):
                origin=p+u*(j+.5)*pitch-n*depth+Vector((0,0,3.2));hit=b.ray_cast(origin,Vector((0,0,-1)),3.4);blocked=hit[0] is not None and hit[0].z>p.z+.02
                checks.append({'segment':s['name'],'bay':j,'depth_m':depth,'soil_z':hit[0].z if hit[0] is not None else None,'soil_above_gallery_floor':bool(blocked)})
    x0,x1,back,front=r['layout']['colonnade_extent_candidate'];floor=r['layout']['colonnade_floor_candidate_m']
    for x in np.linspace(x0+1,x1-1,7):
        for y in (28,30,32):
            hit=b.ray_cast(S@Vector((float(x),y,floor+2.5)),Vector((0,0,-1)),2.8);blocked=hit[0] is not None and hit[0].z>floor+.02
            checks.append({'segment':'Colunata','local_xy':[float(x),y],'soil_z':hit[0].z if hit[0] is not None else None,'soil_above_gallery_floor':bool(blocked)})
    samples.append({'object':o.name,'samples':checks,'soil_intersections':sum(x['soil_above_gallery_floor'] for x in checks)})
    if samples[-1]['soil_intersections']:
        failed={'object':o.name,'blocked':[c for c in checks if c['soil_above_gallery_floor']]}
        (root/'artifacts/palacio-rio-branco/terrace_soil_intersections_r36.json').write_text(json.dumps(failed,ensure_ascii=False,indent=2),encoding='utf8')
    assert not samples[-1]['soil_intersections'],'Solo ainda presente no interior: '+o.name
    assert sig(o)==item['after'],'Malha mudou após a última correção'
# Abertura real da laje superior, conferida somente contra essa peça.
o=scene.objects['RIO R36 | Laje superior da colunata'];me=o.data;me.calc_loop_triangles();b=BVHTree.FromPolygons([wm(o)@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True);hole=r['access_connection_correction']['internal_stair']['opening_local'];roof=r['layout']['colonnade_roof_candidate_m'];center=Vector(((hole[0]+hole[1])/2,(hole[2]+hole[3])/2,roof+1));hit=b.ray_cast(S@center,Vector((0,0,-1)),2);assert hit[0] is None,'Laje fecha a escada'
r['final_layout']={'upper_gallery_preservation':'Componentes B35 restaurados e verificados; não removidos ou deslocados.','connection_segment':r['preserved_gallery_connection']['segment'],'garden_flights':r['access_connection_correction']['garden_flights'],'garden_landings':r['access_connection_correction']['garden_landings'],'internal_stair':r['access_connection_correction']['internal_stair'],'real_dimensions_verified':None}
r['local_geometry_review']={'protected_components_unchanged':len(r['protected_signatures']),'restored_gallery_components':len(r['preserved_gallery_connection']['restored_components']),'soil_clearance':samples,'roof_has_real_stair_opening':True,'scope':'Conferência de modelagem, não teste automatizado do jogo ou aprovação de circulação no runtime.','main_scene':scene.name,'main_scene_objects':len(scene.objects)}
r['visual_review']={'status':'reviewed_local_candidate','views':['terracos','retaguarda','colunata','escada_interna','encontro'],'capture_directory':'artifacts/palacio-rio-branco','finding':'Galerias anteriores preservadas; encontro acrescentado; abertura e escada dentro da laje. Talude recomposto pelos limites das estruturas e pista existente. Acabamento/implantação fina ainda candidatos.'}
for key in ('garden_profile_refinement','access_connection_correction','preserved_gallery_connection','final_slope_profile','opening_finish','complete_gallery_slope','gallery_slope_joint','gallery_slope_surface','colonnade_soil_volume'):
    if key in r:r[key]['visual_review']='reviewed_local_candidate'
r['status']='modeling_candidate_reviewed';r['limitations']=['Medidas e ritmo do trecho acrescido são candidatos; a região encoberta exige referência mais legível para confirmação. Não declarar contagem de arcos ou dimensões como medidas reais.','Retaguarda não documentada suficientemente: corpo anterior preservado; detalhes não inventados.','Circulação/colliders dos terraços ainda precisam de validação de gameplay antes de exportar.','Entorno e terreno fora do recorte, jardins/vegetação e detalhes esculpidos ainda parciais. Este passe não conclui a fidelidade de toda a cidade.']
for o in bpy.context.selected_objects:o.select_set(False)
focus=scene.objects['RIO R36 | Laje superior da colunata'];focus.select_set(True);bpy.context.view_layer.objects.active=focus
eye=S@Vector((-25,74,81));target=S@Vector((17,15,65))
for area in bpy.context.screen.areas:
    if area.type!='VIEW_3D':continue
    space=area.spaces.active
    if space.local_view:
        region=next(q for q in area.regions if q.type=='WINDOW')
        with bpy.context.temp_override(area=area,region=region):bpy.ops.view3d.localview(frame_selected=False)
    space.clip_end=2500;view=space.region_3d;view.view_location=target;view.view_rotation=(eye-target).to_track_quat('Z','Y');view.view_distance=(eye-target).length;view.view_perspective='PERSP';area.tag_redraw()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
r['final_scene_signatures']={n:sig(scene.objects[n]) for n in set(r['created_objects']+r['colliders'])};r['presentation']='Terraços, palácio e galerias enquadrados na janela e no arquivo.'
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':r['source_after'],'restored_gallery_components':r['local_geometry_review']['restored_gallery_components'],'soil_intersections':[s['soil_intersections'] for s in samples],'roof_opening':True},ensure_ascii=False))
