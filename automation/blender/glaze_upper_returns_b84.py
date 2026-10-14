"""Fechamento envidraçado candidato nos dois retornos; B83 preservada."""
import bpy,bmesh,json,runpy,hashlib,os,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/reports/blender/lacerda-glazing-b84';OUT.mkdir(parents=True,exist_ok=True)
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b83_encontro_superior_consolidado.blend'
assert bpy.context.scene.name=='SALVADOR | ESBOCO OFICIAL'
assert not bpy.app.driver_namespace.get('boas_proxy_operator')
dest=ROOT/'blender/salvador_lacerda_r30b84_fechamento_envidracado.blend';assert not dest.exists()
base=Path(bpy.data.filepath)
with base.open('rb') as f:basehash=hashlib.file_digest(f,'sha256').hexdigest()
assert basehash=='7c4376037dcca58a9367f38d07d75ec8fd2f8f2106a0c68c109dbb5514c70423'
M=Matrix(json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame']);inv=M.inverted()
h=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
scene=bpy.context.scene
baseline={}
for o in scene.objects:
    try:baseline[o.name]=sig(o)
    except RuntimeError:baseline[o.name]={'type':o.type,'basis':[list(r) for r in o.matrix_basis],'data':o.data.name if o.data else None}
(OUT/'baseline.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding='utf8')
def bounds(o):
    p=[inv@wm(o)@v.co for v in o.data.vertices]
    return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
glass_source=scene.objects['PASSARELA EXTERNA | vidro'];gb=bounds(glass_source);z0,z1=gb[2]
assert abs(z0-71.225)<1e-4 and abs(z1-73.875)<1e-4
glass=glass_source.data.materials[0];frame=scene.objects['PASSARELA EXTERNA | caixilho.012'].data.materials[0]
ivory=scene.objects['SUPERIOR | posterior lateral'].data.materials[0]
facespec=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
def replace_boxes(o,boxes,materials):
    vs=[];fs=[];mi=[];to_local=wm(o).inverted()@M
    for limits,material in boxes:
        (a,b),(c,d),(e,f)=limits;k=len(vs)
        vs.extend(tuple(to_local@Vector(p)) for p in [(a,c,e),(a,c,f),(a,d,e),(a,d,f),(b,c,e),(b,c,f),(b,d,e),(b,d,f)])
        fs.extend(tuple(k+i for i in face) for face in facespec);mi.extend([material]*6)
    me=bpy.data.meshes.new(o.name+' | vidro e caixilhos B84');me.from_pydata(vs,[],fs);me.update()
    for mat in materials:me.materials.append(mat)
    for p,i in zip(me.polygons,mi):p.material_index=i
    bm=bmesh.new();bm.from_mesh(me);bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-8 for f in bm.faces);bm.free()
    assert not bad and not deg
    o.data=me
changed=[];panels=[]
for suffix in ('','.001'):
    o=scene.objects['SUPERIOR | posterior lateral'+suffix];b=bounds(o);(x0,x1),(y0,y1),(bottom,top)=b
    border=.14;a=y0+border;end=y1-border
    # A faixa é recortada de fato: não há reboco opaco atrás do vidro.
    boxes=[(((x0,x1),(y0,y1),(bottom,z0)),0),(((x0,x1),(y0,y1),(z1,top)),0),(((x0,x1),(y0,a),(z0,z1)),0),(((x0,x1),(end,y1),(z0,z1)),0)]
    # Ritmo secundário aproximado; mesmas travessas e materiais da passarela.
    n=math.ceil((end-a)/.68);ys=[a+(end-a)*j/n for j in range(n+1)];zs=[z0,71.60,72.75,z1]
    outer=x0-.01;depth=.10;thin=.04
    for left,right in zip(ys,ys[1:]):
        for low,high in zip(zs,zs[1:]):
            boxes.append((((x0+.06,x0+.10),(left+thin/2,right-thin/2),(low+thin/2,high-thin/2)),1))
    for y in ys:boxes.append((((outer,outer+depth),(y-thin/2,y+thin/2),(z0,z1)),2))
    for z in zs:boxes.append((((outer,outer+depth),(a,end),(z-thin/2,z+thin/2)),2))
    replace_boxes(o,boxes,[ivory,glass,frame]);changed.append(o.name)
    o['boas_revision']='R30B.84';o['boas_reference_status']='partial';o['accuracy']='APPROXIMATE';o['replacement_required']=True
    o['boas_provenance_ids']=json.dumps(['derived:lacerda-upper-glazing-b84'])
    o['boas_b84_reason']='Foto fornecida comprova faixa envidraçada; dimensões e ritmo adaptados ao corredor existente, não medidos'
    # O lambril inferior não pode atravessar a nova janela.
    trim=scene.objects['LAC R30B02 | Lambril marmore | '+o.name];tw=wm(trim);ti=tw.inverted();trimbase,oldtop=bounds(trim)[2]
    for v in trim.data.vertices:
        p=inv@tw@v.co
        p.z=trimbase+(p.z-trimbase)*(z0-.025-trimbase)/(oldtop-trimbase)
        v.co=ti@M@p
    trim['boas_revision']='R30B.84';trim['boas_provenance_ids']=json.dumps(['derived:lacerda-upper-glazing-b84']);changed.append(trim.name)
    panels.append({'object':o.name,'glass_z':[z0,z1],'panes':n*3,'pattern':'mesmas travessas horizontais do corredor; subdivisão vertical aproximada','previous_lambril_top':oldtop})
    collider=scene.objects['B83 | COLLISION | '+o.name]
    # Vidro fechado continua barreira: envelope simples anterior permanece válido.
    assert sig(collider)==baseline[collider.name]
scene.view_layers[0].update()
report={'revision':'R30B.84','parent_file':base.relative_to(ROOT).as_posix(),'parent_sha256':basehash,'pid':os.getpid(),'scene':scene.name,'changed_objects':changed,'panels':panels,'colliders_unchanged':True,'collider_reason':'Envelope fechado conservado: vidro físico substitui reboco sem liberar passagem','dimensions_measured':False,'historical_vertical_gate':'BLOCKED_EXTERNAL_EVIDENCE','production_ready':False,'ssot_sha256':hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest(),'file':dest.relative_to(ROOT).as_posix()}
(OUT/'application.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True,check_existing=False)
with dest.open('rb') as f:report['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(OUT/'application.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
catalogpath=ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json';catalog=json.loads(catalogpath.read_text(encoding='utf8'))
entry={'file':report['file'],'sha256':report['sha256'],'revision':'R30B.84','parent_file':report['parent_file'],'scene':scene.name,'status':'validation_candidate','production_ready':False,'evidence':'docs/reports/blender/lacerda-glazing-b84/application.json','notes':'Dois retornos envidraçados e lambris reconciliados; não certifica dimensões ou resolve gates históricos.'}
catalog['authoring_source']=entry;catalog['validation_source']=entry;catalog['revisions'].append(entry);catalogpath.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':entry,'panels':panels,'changed':changed},ensure_ascii=False))
