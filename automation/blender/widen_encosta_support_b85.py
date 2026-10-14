"""Adequação local do apoio à largura do corpo superior, sem alterar o vão."""
import bpy,json,hashlib,runpy,bmesh,os
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-proportions-b85';OUT.mkdir(parents=True,exist_ok=True)
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b84_fechamento_envidracado.blend'
assert bpy.context.scene.name=='SALVADOR | ESBOCO OFICIAL'
assert not bpy.app.driver_namespace.get('boas_proxy_operator')
base=Path(bpy.data.filepath);dest=ROOT/'blender/salvador_lacerda_r30b85_apoio_encosta_proporcoes.blend';assert not dest.exists()
with base.open('rb') as f:basehash=hashlib.file_digest(f,'sha256').hexdigest()
catpath=ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text(encoding='utf8'));assert basehash==cat['authoring_source']['sha256']
M=Matrix(json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame']);inv=M.inverted()
h=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix'];scene=bpy.context.scene
bodyname='LAC R30B08 | apoio oposto | corpo estrutural afunilado'
names=[bodyname,'LAC R30B08 | apoio oposto | capitel sob passarela','LAC R30B08 | apoio oposto | ressalto transversal','LAC R35 | Caixilhos verticais do apoio','LAC R35 | Vidros da faixa vertical do apoio','LAC R35 | Pilastras e faixa sob os vãos']
assert all(n in scene.objects for n in names)
for o in scene.objects:
    if o.name not in names and o.type=='MESH':assert not any(o.get('boas_derived_from_object')==n for n in names),'Binding físico precisa ser reconciliado antes da edição'
def bounds(o):
    pts=[inv@wm(o)@v.co for v in o.data.vertices]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
def shallow(o):
    return {'data':o.data.as_pointer() if o.data else None,'basis':[list(r) for r in o.matrix_basis],'parent':o.parent.name if o.parent else None,'modifiers':[(m.name,m.type) for m in o.modifiers]}
protected={o.name:shallow(o) for o in scene.objects if o.name not in names}
terrain=scene.objects['MVP | terreno corrigido | colisão estática'];terrain_before=sig(terrain)
proxy_before={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects}
old={n:{'signature':sig(scene.objects[n]),'bounds':bounds(scene.objects[n])} for n in names}
control=scene.objects['EDIFICIO | parede posterior alta'];cb=bounds(control);targetwidth=cb[1][1]-cb[1][0];center=sum(cb[1])/2
bb=old[bodyname]['bounds'];oldwidth=bb[1][1]-bb[1][0];factor=targetwidth/oldwidth
assert abs(oldwidth-6.94)<1e-4 and abs(targetwidth-11.4)<1e-4
changes=[]
for name in names:
    o=scene.objects[name];o.data=o.data.copy();tw=wm(o);ti=tw.inverted();ob=old[name]['bounds']
    if name.endswith('capitel sob passarela') or name.endswith('ressalto transversal'):
        width=ob[1][1]-ob[1][0];localfactor=(targetwidth+width-oldwidth)/width
    else:localfactor=factor
    for v in o.data.vertices:
        p=inv@tw@v.co;p.y=center+(p.y-center)*localfactor;v.co=ti@M@p
    o.data.update();bm=bmesh.new();bm.from_mesh(o.data);deg=sum(f.calc_area()<1e-8 for f in bm.faces);boundary=sum(e.is_boundary for e in bm.edges);bm.free();assert not deg
    after=bounds(o)
    assert all(abs(after[k][j]-ob[k][j])<2e-4 for k in (0,2) for j in (0,1))
    assert sig(o)['transform']==old[name]['signature']['transform']
    o['boas_revision']='R30B.85';o['classification']='ADAPT_LOCAL';o['reference_status']='partial';o['accuracy']='APPROXIMATE';o['replacement_required']=True
    o['boas_provenance_ids']=json.dumps(['derived:lacerda-encosta-support-b85'])
    o['b85_reason']='Proporção do apoio compatibilizada com faces do corpo superior conforme leitura exterior; não representa dimensão levantada'
    changes.append({'object':name,'before':old[name],'after':{'signature':sig(o),'bounds':after},'degenerate':deg,'boundary_edges':boundary,'y_factor':localfactor})
scene.view_layers[0].update()
assert all(shallow(scene.objects[n])==s for n,s in protected.items())
assert sig(terrain)==terrain_before
assert all(sig(bpy.data.objects[n])==s for n,s in proxy_before.items())
ssot=hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest()
report={'revision':'R30B.85','file':dest.relative_to(ROOT).as_posix(),'parent_file':base.relative_to(ROOT).as_posix(),'parent_sha256':basehash,'pid':os.getpid(),'scene':scene.name,'changed_meshes':changes,'width_control':{'object':control.name,'bounds_local':cb,'width_candidate':targetwidth,'not_surveyed':True},'support_width_before':oldwidth,'support_width_after':targetwidth,'ssot_sha256':ssot,'protected_scene_objects':len(protected),'terrain_unchanged':True,'proxy_unchanged':True,'source_gate':'ADAPT_LOCAL_APPROXIMATE','bridge_saguão_gate':'NEEDS_CONTROLLED_XY_REGISTRATION','passarela_changed':False,'historic_vertical_gate':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses_preserved':27,'production_ready':False,'reopened':False}
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True,check_existing=False)
with dest.open('rb') as f:report['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(OUT/'application.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':report['file'],'sha256':report['sha256'],'revision':'R30B.85','parent_file':report['parent_file'],'scene':scene.name,'status':'validation_candidate','production_ready':False,'evidence':'docs/reports/blender/lacerda-proportions-b85/application.json','notes':'Adequação local aproximada da largura do apoio e dependências visuais; comprimento da passarela/saguão permanece pendente.'}
cat['authoring_source']=entry;cat['validation_source']=entry;cat['revisions'].append(entry);catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':entry,'width_before':oldwidth,'width_after':targetwidth,'changed':[c['object'] for c in changes],'passarela_changed':False,'production_ready':False},ensure_ascii=False))
