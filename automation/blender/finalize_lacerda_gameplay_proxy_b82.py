"""Finaliza objetos proxy já construídos, inclusive aplicação interrompida antes do save."""
import bpy,json,math,hashlib,runpy,sys,os,traceback
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-gameplay-proxy'
sys.path.insert(0,str(ROOT/'tools/world'))
from lacerda_gameplay_proxy import validate_round_trip
config=json.loads((ROOT/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json').read_text(encoding='utf8'))
source=bpy.data.scenes['SALVADOR | ESBOCO OFICIAL'];scene=bpy.data.scenes[config['scene_name']]
col=bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'];layer=scene.view_layers[0]
assert Path(bpy.data.filepath).resolve()==(ROOT/config['source_file']).resolve()
assert not (ROOT/config['scene_file']).exists(),'Não sobrescrever B82 salva'
assert len(col.objects)==70,'Inspecionar aplicação parcial divergente'
def progress(stage):
    (OUT/'model_progress.json').write_text(json.dumps({'stage':stage,'pid':os.getpid()}),encoding='utf8')
try:
    progress('cache de apresentação')
    a=config['local_frame']['angle'];c,s=math.cos(a),math.sin(a);origin=config['local_frame']['origin_xy']
    def world(p):return (origin[0]+c*p[0]-s*p[1],origin[1]+s*p[0]+c*p[1],p[2])
    def local(p):
        dx,dy=p[0]-origin[0],p[1]-origin[1]
        return (c*dx+s*dy,-s*dx+c*dy,p[2])
    regions=[]
    for f in config['floors']:
        cc,ss=math.cos(f['angle']),math.sin(f['angle']);hx,hy=[v/2 for v in f['size']]
        corners=[(f['center'][0]+cc*x-ss*y,f['center'][1]+ss*x+cc*y) for x in (-hx,hx) for y in (-hy,hy)]
        regions.append(([min(p[0] for p in corners)-.45,min(p[1] for p in corners)-.45,f['center'][2]-.25],
                        [max(p[0] for p in corners)+.45,max(p[1] for p in corners)+.45,f['center'][2]+3.3]))
    regions.append(([-2.25,-2.25,config['levels']['lower']-.3],[2.25,2.25,config['levels']['upper']+3.3]))
    masks=[];source_visibility={o.name:o.visible_get(view_layer=source.view_layers[0]) for o in source.objects}
    # Todas as consultas primeiro; não intercalar bound_box/depsgraph com hide_set.
    for ob in source.objects:
        visible=source_visibility[ob.name]
        hide=not visible or ob.type not in ('MESH','CURVE','FONT') or ob.get('elevator_id') is not None
        overlaps=False
        if visible and ob.type in ('MESH','CURVE','FONT'):
            pts=[local(ob.matrix_world@Vector(p)) for p in ob.bound_box]
            lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
            overlaps=any(all(hi[i]>=rlo[i] and lo[i]<=rhi[i] for i in range(3)) for rlo,rhi in regions)
            # AABB local não autoriza ocultar malha integral de terreno.
            keep_context=ob.name in config.get('presentation',{}).get('keep_context_visible',[])
            hide=hide or (overlaps and not keep_context)
        masks.append((ob,hide,overlaps))
    progress('máscaras somente na view layer proxy')
    layer_objects=set(layer.objects.keys())
    for ob,hide,_ in masks:
        if ob.name not in layer_objects:continue  # Coleção já excluída: sem Base nesta view layer.
        if ob.hide_get(view_layer=layer)!=hide:ob.hide_set(hide,view_layer=layer)
    progress('comparação dos 6296 componentes históricos')
    before=json.loads((OUT/'protected_original_components.json').read_text(encoding='utf8'))
    sig=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature']
    bpy.context.window.scene=source;source.view_layers[0].update()
    changed=[]
    for name,value in before.items():
        ob=bpy.data.objects[name]
        try:after=sig(ob)
        except RuntimeError:after={'type':ob.type,'basis':[list(r) for r in ob.matrix_basis],'data':ob.data.name if ob.data else None}
        if after!=value:changed.append(name)
    assert not changed,'Componentes históricos alterados: '+str(changed)
    assert all(bpy.data.objects[n].visible_get(view_layer=source.view_layers[0])==v for n,v in source_visibility.items())
    bpy.context.window.scene=scene
    scene.render.fps=source.render.fps;scene.render.fps_base=source.render.fps_base
    scene['status']='GAMEPLAY_PROXY';scene['accuracy']='APPROXIMATE';scene['replacement_required']=True
    scene['boas_geographic_ssot_sha256']=config['geographic_ssot_sha256']
    scene['historical_movement_enabled']=False;scene['gameplay_movement_enabled']=True
    scene['LACERDA_VERTICAL_HISTORICAL']='BLOCKED_EXTERNAL_EVIDENCE'
    scene['boas_proxy_contract']='world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json'
    scene['boas_proxy_bootstrap']='automation/blender/play_lacerda_gameplay_proxy.py'
    text=bpy.data.texts.get('B82 | LEIA-ME · GAMEPLAY_PROXY') or bpy.data.texts.new('B82 | LEIA-ME · GAMEPLAY_PROXY')
    text.clear();text.write('Protótipo aproximado/substituível. B76–B81 e gates históricos preservados.\nF3: BOAS Jogar Lacerda (proxy). WASD, setas para olhar, E chamar/viajar, Esc sair.\nApós reabrir, executar BOAS_JOGAR_PROXY.py no editor de texto.\nNão representa as-built nem libera produção.\n')
    bootstrap=bpy.data.texts.get('BOAS_JOGAR_PROXY.py') or bpy.data.texts.new('BOAS_JOGAR_PROXY.py')
    bootstrap.clear();bootstrap.write('import bpy,runpy\nfrom pathlib import Path\nroot=Path(bpy.data.filepath).resolve().parents[1]\nrunpy.run_path(str(root/"automation/blender/play_lacerda_gameplay_proxy.py"),run_name="__main__")\n')
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
            area.spaces.active.region_3d.view_location=Vector(world([0,0,config['levels']['upper']]))
            area.spaces.active.region_3d.view_distance=100.;area.spaces.active.show_region_ui=True
    progress('validação funcional')
    trip=validate_round_trip(config)
    report={'revision':'R30B.82','pid':os.getpid(),'source_before':config['source_file'],'scene_name':scene.name,
            'historical_scene':source.name,'historical_objects':len(before),'historical_components_changed':changed,
            'historical_visibility_preserved':True,'added_objects':[o.name for o in col.objects],
            'masked_in_proxy_view_only':[o.name for o,_,hit in masks if hit],
            'context_derivatives':[], 'controller_round_trip':trip['status'],
            'historical_fidelity_resolved':False,'production_ready':False,'source_reopened':False,
            'presentation':'Greybox independente com contexto histórico externo; máscaras por view layer, sem editar malha original'}
    progress('salvando B82')
    file=ROOT/config['scene_file'];bpy.ops.wm.save_as_mainfile(filepath=str(file),check_existing=False)
    with file.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    path=ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json';catalog=json.loads(path.read_text(encoding='utf8'))
    entry={'file':config['scene_file'],'revision':'R30B.82','sha256':digest,'parent_file':config['source_file'],
           'scene':scene.name,'status':'GAMEPLAY_PROXY','accuracy':'APPROXIMATE','replacement_required':True,
           'production_ready':False,'evidence':'docs/reports/blender/lacerda-gameplay-proxy/application_b82.json',
           'notes':'Protótipo funcional separado; alta fidelidade congelada, B80/B81 não resolvidas.'}
    catalog['gameplay_proxy_source']=entry;catalog['revisions'].append(entry)
    path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    report['sha256']=digest;(OUT/'application_b82.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    runpy.run_path(str(ROOT/'automation/blender/play_lacerda_gameplay_proxy.py'),run_name='__main__')
    progress('B82 salva, painel registrado')
    print(json.dumps({'file':config['scene_file'],'sha256':digest,'added':70,'historical_changed':len(changed),'round_trip':trip['status'],'pid':os.getpid()}))
except Exception:
    (OUT/'model_error.txt').write_text(traceback.format_exc(),encoding='utf8');raise
