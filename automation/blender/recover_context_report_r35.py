"""Recupera metadados após erro de serialização; não repete a modelagem."""
import bpy,json,runpy,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];path=root/'docs/reports/blender/torre_galerias_r30b35.json';r=json.loads(path.read_text(encoding='utf8'));scene=bpy.context.scene
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature']
archive=bpy.data.collections.get('REFERENCE | Apoio e terreno substituídos R35');assert archive and 'context_structure_refinement' not in r
assert 'escalonada' in scene.objects[r['tower_alignment']['objects'][0]]['r35_shaft_profile']
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
oldcontext=json.loads((root/'artifacts/palacio-rio-branco/context_r35.json').read_text(encoding='utf8'));oldrows={row['name']:row for row in oldcontext['objects']}
archived=[{'object':o.name,'geometry_preserved':sig(o),'collections_before':oldrows.get(o.name,{}).get('collections'),'reason':o.get('boas_archive_reason')} for o in archive.objects]
rows=[]
for item in r['terrain_refinement']['geometry']:
    rows.append({'object':item['object'],'before':item['after'],'after':sig(scene.objects[item['object']])});item['after']=rows[-1]['after']
ring=r['tower_alignment']['rings_local'][0];front=r['tower_alignment']['rings_local'][-1][1];land=ring[1]
steps=[(21,land),(39,land),(39,land+(front-land)*.28),(58,land+(front-land)*.28),(58,land+(front-land)*.68),(65.4000015258789,land+(front-land)*.68),(68.85,front)]
r['context_structure_refinement']={'classification':'ADAPT_LOCAL','support_back_profile_local_z_x_candidate_m':steps,'support_profile_verified_real_dimensions':None,'support_after':sig(scene.objects[r['tower_alignment']['objects'][0]]),'archived_overlapping_legacy_objects':archived,'terrain':rows,'terrain_method':'Contenção e talude entre a borda interior amostrada da ladeira e o pé das galerias/laje; remove depressões da posição antiga do apoio. Perfil fotográfico candidato, não levantamento topográfico.','implementation':'automation/blender/refine_context_structure_r35.py','road_xy_width_dem_changed':False,'visual_review':'pending','report_recovery':'Modelagem executada e salva; relatório recomposto após erro float32 no JSON final. Nenhuma mutação geométrica foi repetida.'}
r.pop('localized_scene_review',None)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(root/'automation/blender/review_support_only_r35.py'))
