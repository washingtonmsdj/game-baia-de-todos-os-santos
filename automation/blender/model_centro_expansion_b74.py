"""B74: expansão candidata ao vivo; geografia-fonte separada de arte final."""
import bpy,json,numpy as np,hashlib,runpy,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
catalog_path=root/'world/areas/mvp-centro-lacerda/blender-revisions.json'
catalog=json.loads(catalog_path.read_text(encoding='utf8'));source=catalog['validation_source']
assert source['revision']=='R30B.73' and Path(bpy.data.filepath).resolve()==(root/source['file']).resolve()
output=root/'blender/salvador_lacerda_r30b74_expansao_lapa_tororo_fonte_nova.blend';assert not output.exists()
art=root/'artifacts/structural-pipeline/centro-lapa-tororo-fontenova'
data=json.loads((art/'candidate_scene.json').read_text(encoding='utf8'))
derivation=json.loads((root/'docs/reports/blender/centro-expansion/candidate_derivation.json').read_text(encoding='utf8'))
signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
names=['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro','CAIS | contenção costeira alinhada à linha de costa']
names += [o.name for o in scene.objects if o.name.startswith('PIER OSM |')]
protected={n:signature(scene.objects[n]) for n in names};before_names=set(scene.objects.keys())
def collection(name,role):
    col=bpy.data.collections.get(name)
    if col:
        assert not col.objects and col.get('boas_role')==role, 'Retomada exige coleção candidata vazia'
    else:
        col=bpy.data.collections.new(name);scene.collection.children.link(col)
    col['boas_role']=role;col['boas_production_ready']=False
    return col
terrain_col=collection('40 | EXPANSAO CENTRO | REFERENCE_TERRAIN','REFERENCE_TERRAIN')
reference_col=collection('SOURCE_GEOREF | CENTRO LAPA TORORO FONTE NOVA','REFERENCE_OSM')
water_col=collection('WATER | Dique do Tororo | candidato B74','WATER_REFERENCE')
qa_col=collection('QA | RONDESP | expansao centro B74','REVIEW_ONLY')
def material(name,color):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) or m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.85
    return m
mats={'terrain':material('B74 | terra | candidato',(.31,.36,.28)),'roads':material('B74 | eixo viario OSM | sem largura',(.075,.08,.085)),'buildings':material('B74 | footprint OSM',(.55,.53,.44)),'pedestrian':material('B74 | referencia pedonal',(.65,.57,.40)),'steps':material('B74 | referencia escadarias',(.6,.38,.16)),'water':material('B74 | Dique | nivel candidato',(.045,.25,.29)),'target':material('B74 | marcos de referencia',(.71,.65,.48)),'unverified':material('B74 | passagem em nivel pendente',(.7,.20,.06))}
def mesh_object(name,vertices,faces,col,mat):
    me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat)
    ob['boas_revision']='R30B.74';ob['boas_production_ready']=False
    return ob
terrain=np.load(art/'candidate_terrain.npz')
ground=mesh_object('B74 | TERRENO | Lapa Tororo Fonte Nova | candidato',terrain['vertices'].tolist(),terrain['faces'].tolist(),terrain_col,mats['terrain'])
ground['boas_terrain_surface']=True;ground['boas_vertical_absolute_approved']=False
ground['boas_source_summary']=data['source_summary'];ground['boas_classification']='ADAPT_LOCAL'
ground['boas_transition_design_width_m']=derivation['local_transition']['width_design_m']
ground['boas_reference_only']=True
curves={};index=[]
for trace in data['traces']:
    tags=trace['tags'];key=trace['layer']
    if key=='roads' and (tags.get('bridge') not in (None,'no') or tags.get('tunnel') not in (None,'no') or tags.get('layer','0')!='0'):key='unverified'
    if key not in curves:
        curve=bpy.data.curves.new('B74 | OSM | '+key,'CURVE');curve.dimensions='3D';curve.bevel_depth=.11 if key=='buildings' else .18;curve.bevel_resolution=0
        ob=bpy.data.objects.new(curve.name,curve);reference_col.objects.link(ob);curve.materials.append(mats[key]);ob.hide_render=True
        ob['boas_reference_only']=True;ob['boas_width_is_axis_marker_not_road']=True;curves[key]=curve
    curve=curves[key];sp=curve.splines.new('POLY');sp.points.add(len(trace['points'])-1)
    coords=np.column_stack((np.array(trace['points']),np.ones(len(trace['points']))));sp.points.foreach_set('co',coords.flatten())
    index.append({'object':curve.name,'spline':len(curve.splines)-1,'osm_id':trace['osm_id'],'osm_type':trace['osm_type'],'layer':trace['layer'],'tags':tags,'width_m_verified':trace['width_m_verified'],'layer_z_verified':False})
text=bpy.data.texts.new('B74 | SOURCE_GEOREF INDEX');text.write(json.dumps({'capture_id':'osm-mapzen-20261005T045222Z','features':index},ensure_ascii=False))
targets=[]
for target in data['targets']:
    name='B74 | '+target['location_id']+' | referencia'
    points=target['outer'];base=target['base_z_candidate']
    if target['location_id']=='dique-do-tororo':
        verts=[];faces=[]
        for tri in target['triangles']:
            k=len(verts);verts.extend([[p[0],p[1],target['water_z_candidate']] for p in tri]);faces.append([k,k+1,k+2])
        ob=mesh_object(name,verts,faces,water_col,mats['water']);ob['boas_water_level_verified']=False;ob['boas_water_level_candidate']=target['water_z_candidate']
    else:
        curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=.35;curve.bevel_resolution=0;curve.materials.append(mats['target'])
        ob=bpy.data.objects.new(name,curve);reference_col.objects.link(ob)
        for ring in [points,*target['inner']]:
            for z in ([base,base+target['height_m_tagged']] if target['height_m_tagged'] is not None else [base+.2]):
                sp=curve.splines.new('POLY');sp.points.add(len(ring)-1)
                sp.points.foreach_set('co',np.array([[p[0],p[1],z,1] for p in ring]).flatten())
        if target['height_m_tagged'] is not None:ob['boas_height_m_tagged']=target['height_m_tagged']
        ob['boas_height_status']='OSM tag' if target['height_m_tagged'] is not None else 'pending'
    ob['boas_osm_id']=target['osm_id'];ob['boas_osm_type']=target['osm_type'];ob['boas_location_id']=target['location_id'];ob['boas_reference_only']=True;ob['boas_model_status']='reference_proxy'
    targets.append(ob.name)
    font=bpy.data.curves.new(name+' | nome','FONT');font.body=target['name'];font.size=14;font.align_x='CENTER';font.materials.append(mats['target'])
    label=bpy.data.objects.new(font.name,font);reference_col.objects.link(label);label.location=(float(np.mean(np.array(points)[:,0])),float(np.mean(np.array(points)[:,1])),base+35);label['boas_reference_only']=True;label.hide_render=True
scene['boas_validation_revision']='R30B.74';scene['boas_expansion_area']='centro-lapa-tororo-fontenova'
readme=bpy.data.texts.new('B74 | ESTADO DA EXPANSAO');readme.write('Terreno relativo candidato e eixos/footprints OSM. Não é mapa final. Não existem larguras inventadas. Dique recortado por relation 15601931; água tem nível candidato. Arena preserva anel interno real. Altimetria absoluta, pavimentos, faixas, pontes/túneis e acessos permanecem pendentes. Dados originais, núcleo, costa, cais e píeres preservados.')
qa=runpy.run_path(str(root/'automation/blender/probe_rondesp_centro_b74.py'),init_globals={'BOAS_NEW_GROUND':ground,'BOAS_ROUTES':data['routes'],'BOAS_QA_COLLECTION':qa_col})['result']
changed=[n for n,v in protected.items() if signature(scene.objects[n])!=v];assert not changed
assert before_names<=set(scene.objects.keys())
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.region_3d.view_location=(470,-690,25);sp.region_3d.view_distance=2550
            sp.region_3d.view_rotation=Vector((.3,-.65,1.6)).to_track_quat('Z','Y');sp.region_3d.view_perspective='ORTHO'
            sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.overlay.show_overlays=False
scene.frame_set(qa['overview_frame'])
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
after={'file':output.relative_to(root).as_posix(),'sha256':hashlib.file_digest(output.open('rb'),'sha256').hexdigest(),'revision':'R30B.74'}
report={'schema':'boas/centro-expansion-b74-scene-v1','source_before':source,'source_after':after,'derivation':'docs/reports/blender/centro-expansion/candidate_derivation.json','terrain_object':ground.name,'terrain_vertices':len(ground.data.vertices),'terrain_triangles':len(ground.data.polygons),'reference_traces':len(index),'target_objects':targets,'preservation_signatures':protected,'protected_changes':changed,'existing_objects_removed':False,'qa':qa,'source_reopened':False,'production_ready':False,'roads_final_built':False,'runtime_exported':False}
(root/'docs/reports/blender/centro-expansion/scene_b74.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={**after,'parent_file':source['file'],'status':'validation_candidate','evidence':'docs/reports/blender/centro-expansion/scene_b74.json','notes':'Expansão candidata de terreno e referências OSM; vias finais/larguras/altimetria pendentes. Não aprovada para produção.','source_reopened':False}
for e in catalog['revisions']:
    if e['file']==source['file']:e['status']='superseded_validation'
catalog['revisions'].append(entry);catalog['validation_source']=entry;catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source':after,'terrain_vertices':report['terrain_vertices'],'terrain_triangles':report['terrain_triangles'],'targets':targets,'protected_changes':changed,'qa':qa},ensure_ascii=False))
