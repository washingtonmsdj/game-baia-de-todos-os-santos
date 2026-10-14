"""Migração limitada do encontro B78 comprovado; B82 permanece intacta."""
import bpy,bmesh,json,runpy,hashlib,shutil,os
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-consolidation-b83';OUT.mkdir(parents=True,exist_ok=True)
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b82_gameplay_proxy.blend'
scene=bpy.data.scenes['SALVADOR | ESBOCO OFICIAL'];assert bpy.context.scene==scene
assert not bpy.app.driver_namespace.get('boas_proxy_operator') and not bpy.app.driver_namespace.get('boas_current_route_test')
destination=ROOT/'blender/salvador_lacerda_r30b83_encontro_superior_consolidado.blend';assert not destination.exists()
base=Path(bpy.data.filepath);assert shutil.disk_usage(ROOT).free>base.stat().st_size*1.3,'Espaço insuficiente; não iniciar migração'
b78=json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))
source=ROOT/b78['source_after']['file']
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==b78['source_after']['sha256']
helper=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'));sig=helper['signature'];wm=helper['world_matrix']
protected=json.loads((ROOT/'docs/reports/blender/lacerda-gameplay-proxy/protected_original_components.json').read_text(encoding='utf8'))
names=[r['object'] for r in b78['changed_meshes']]
assert len(names)==7
original={n:sig(scene.objects[n]) for n in names}
assert all(original[n]==protected[n] for n in names),'Geometria atual divergiu do baseline investigado'
M=Matrix(b78['measurement_frame']);inverse=M.inverted()
bridge=scene.objects['CALIBRADO | passarela piso 28.71 x 6.00m'];points=[inverse@wm(bridge)@v.co for v in bridge.data.vertices]
edges=[min(p.y for p in points),max(p.y for p in points)]
walls=names[0],names[3]
assert abs((edges[1]-edges[0])-6)<1e-4
assert not any(o.get('boas_derived_from_object') in walls for o in scene.objects),'Revisar collider existente antes de duplicar'
loaded=[];changes=[]
with bpy.data.libraries.load(str(source),link=False) as (available,requested):
    assert all(n in available.objects for n in names);requested.objects=list(names)
loaded=requested.objects
try:
    for name,imported in zip(names,loaded):
        ob=scene.objects[name];expected=next(r['mesh_after'] for r in b78['changed_meshes'] if r['object']==name)
        assert sig(imported)['geometry_sha256']==expected,'Mesh B78 incorreta: '+name
    for name,imported in zip(names,loaded):
        ob=scene.objects[name];materials=list(ob.data.materials);mesh=imported.data.copy();mesh.name=name+' | encontro consolidado B83'
        mesh.materials.clear()
        for material in materials:mesh.materials.append(material)
        ob.data=mesh;ob['boas_revision']='R30B.83';ob['boas_reference_status']='partial';ob['boas_provenance_ids']=json.dumps(['derived:lacerda-junction-b78','derived:lacerda-consolidation-b83'])
        ob['boas_b83_reason']='Reconciliar retorno/verga existentes com bordas da passarela; não certifica dimensão real ou poço'
        actual=sig(ob);assert actual['transform']==original[name]['transform'] and actual['materials']==original[name]['materials']
        changes.append({'object':name,'before':original[name],'after':actual})
finally:
    for ob in loaded:
        if ob and not ob.users_scene:bpy.data.objects.remove(ob,do_unlink=True)
colliders=[];col=bpy.data.collections['COLLISION | Galerias Cidade Alta R34']
for name in walls:
    ob=scene.objects[name];mesh=ob.data.copy();mesh.name='B83 collider retorno';world=wm(ob)
    for v in mesh.vertices:v.co=world@v.co
    collider=bpy.data.objects.new('B83 | COLLISION | '+name,mesh);col.objects.link(collider);collider.matrix_basis=Matrix.Identity(4)
    collider.hide_render=True;collider.hide_set(True);collider.display_type='WIRE'
    collider['boas_role']='COLLISION_STATIC_OBSTACLE_CANDIDATE';collider['boas_derived_from_object']=name;collider['boas_production_ready']=False
    collider['boas_location_id']='elevador-lacerda';collider['boas_revision']='R30B.83';collider['boas_provenance_ids']=json.dumps(['derived:lacerda-consolidation-b83'])
    colliders.append(collider.name)
# Fechamento geométrico e integridade antes do save.
checks=[]
for i,name in enumerate(walls):
    ob=scene.objects[name];pts=[inverse@wm(ob)@v.co for v in ob.data.vertices];inner=max(p.y for p in pts) if i==0 else min(p.y for p in pts)
    bm=bmesh.new();bm.from_mesh(ob.data);check={'object':name,'gap':abs(inner-edges[i]),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-8 for f in bm.faces)};bm.free()
    assert check['gap']<1e-5 and not check['nonmanifold'] and not check['degenerate'];checks.append(check)
scene.view_layers[0].update()
runpy.run_path(str(ROOT/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'consolidated-upper-gap.png'})
report={'revision':'R30B.83','pid':os.getpid(),'parent_file':base.relative_to(ROOT).as_posix(),'scene':scene.name,'migration_source':b78['source_after'],'changed_meshes':changes,'added_colliders':colliders,'checks':checks,'physical_dimensions_verified':False,'historical_vertical_gate':'BLOCKED_EXTERNAL_EVIDENCE','historical_witnesses_preserved':27,'production_ready':False,'ssot_sha256':hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest(),'reopened':False}
(OUT/'application.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True,check_existing=False)
with destination.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
report['file']=destination.relative_to(ROOT).as_posix();report['sha256']=digest
(OUT/'application.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
path=ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json';catalog=json.loads(path.read_text(encoding='utf8'))
entry={'file':report['file'],'sha256':digest,'revision':'R30B.83','parent_file':report['parent_file'],'scene':scene.name,'status':'validation_candidate','production_ready':False,'evidence':'docs/reports/blender/lacerda-consolidation-b83/application.json','notes':'Sete malhas do encontro B78 reconciliadas na B82; não resolve gate vertical ou Mercado.'}
catalog['validation_source']=entry;catalog['revisions'].append(entry);path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':entry,'changed':len(changes),'added_colliders':len(colliders),'checks':checks}))
