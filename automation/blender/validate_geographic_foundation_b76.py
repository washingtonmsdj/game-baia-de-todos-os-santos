"""Conferir reabertura e conservação de todos os objetos anteriores; read-only."""
import bpy,json,runpy,sys,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];folder=root/'docs/reports/blender/geographic-foundation'
source=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
assert source['revision']=='R30B.76' and Path(bpy.data.filepath).resolve()==(root/source['file']).resolve()
opened=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert opened['file']==source['file'] and opened['sha256']==source['sha256'] and opened['load_post_completed']
signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
snapshot=json.loads((root/'artifacts/geographic-foundation/b76_protected.json').read_text(encoding='utf8'));differences=[]
for name,before in snapshot.items():
    ob=bpy.data.objects.get(name)
    if ob is None:differences.append({'object':name,'missing':True});continue
    try:sig=signature(ob)
    except RuntimeError:sig={'type':ob.type,'transform':[list(row) for row in ob.matrix_world],'data_name':ob.data.name if ob.data else None,'constraints':[(c.name,c.type) for c in ob.constraints]}
    # JSON serializa tuples como listas; normalizar para comparação.
    actual=json.loads(json.dumps({'signature':sig,'parent':ob.parent.name if ob.parent else None,'collections':[c.name for c in ob.users_collection]}))
    if actual!=before:differences.append({'object':name,'changed_fields':[k for k in before if actual[k]!=before[k]]})
ob=bpy.data.objects['B76 | Campo da Polvora | footprint OSM']
assert ob['boas_osm_id']==257336400 and ob['boas_location_id']=='campo-da-polvora' and ob.hide_render
ssot=root/'world/geographic-reference.json';assert bpy.context.scene['boas_geographic_ssot_sha256']==hashlib.sha256(ssot.read_bytes()).hexdigest()
old=sys.argv[:]
try:
    sys.argv=['blender','--','--output',str(folder/'structural_scene_after.json')]
    runpy.run_path(str(root/'tools/blender/audit_structural_scene.py'),run_name='__main__')
finally:sys.argv=old
report={'source':source,'source_reopened':True,'preserved_objects':len(snapshot)-len(differences),'differences':differences,'added_objects':sorted(set(o.name for o in bpy.context.scene.objects)-set(snapshot)),'scene_objects':len(bpy.context.scene.objects),'ssot_hash_matches':True,'scope':'Malha/curvas/materiais/transforms/hierarquia; constraints usam snapshot reduzido. Sem física, navegação ou prova de datum absoluto.','production_ready':False}
(folder/'validation_b76.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not differences, 'Conservação falhou; não aprovar revisão'
print(json.dumps({'preserved_objects':report['preserved_objects'],'differences':len(differences),'source_reopened':True,'added_objects':report['added_objects']}))
