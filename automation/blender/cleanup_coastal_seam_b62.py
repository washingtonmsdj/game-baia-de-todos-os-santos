"""B62: repara exclusivamente faces com triangulação degenerada da costura refinada."""
import bpy,bmesh,json,hashlib,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
p=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(p.read_text(encoding='utf8'));src=cat['validation_source'];assert src['revision']=='R30B.61'
out=root/'blender/salvador_lacerda_r30b62_pavimento_costura_limpa.blend';assert not out.exists()
old=scene.objects['B61 | GAMEPLAY TERRAIN HQ | pavimento integrado'];old.data.calc_loop_triangles()
bad={t.polygon_index for t in old.data.loop_triangles if t.area<1e-10};assert len(bad)<100
col=bpy.data.collections.new('39.5 GAMEPLAY | B62 COSTURA LIMPA');scene.collection.children.link(col)
me=old.data.copy();bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table()
bmesh.ops.triangulate(bm,faces=[bm.faces[i] for i in bad],quad_method='BEAUTY',ngon_method='BEAUTY')
zero=[f for f in bm.faces if f.calc_area()<1e-10];removed=len(zero);bmesh.ops.delete(bm,geom=zero,context='FACES_ONLY')
wire=[e for e in bm.edges if not e.link_faces]
if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(me);bm.free();me.update();me.calc_loop_triangles();assert not any(t.area<1e-10 for t in me.loop_triangles)
terrain=bpy.data.objects.new('B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa',me);col.objects.link(terrain)
for k in old.keys():terrain[k]=old[k]
terrain['boas_revision']='R30B.62';collision=bpy.data.objects.new('B62 | COLLISION | pavimento e costura limpa',me.copy());col.objects.link(collision);collision.hide_viewport=True;collision.hide_render=True
collision['boas_runtime_role']='terrain_collision';collision['boas_source_surface']=terrain.name;collision['boas_geometry_identical_to_visual']=True;collision['boas_gameplay_approved']=False;terrain['boas_collision_partner']=collision.name
old.hide_viewport=True;old.hide_render=True;old['boas_superseded_by']=terrain.name;scene.objects['B61 | COLLISION | terreno e pavimento integrado']['boas_superseded_by']=collision.name
scene['boas_validation_revision']='R30B.62';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report={'schema':'boas/coastal-cleanup-b62-v1','source_before':src,'source_after':{'file':out.relative_to(root).as_posix(),'revision':'R30B.62','sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()},'retriangulated_polygon_count':len(bad),'removed_zero_area_triangles':removed,'degenerate_triangles_after':0,'visual_collision_identical':True,'core_quay_water_unchanged':True,'approved':False,'pending':['Lacuna até o cais','Navegação e travessia completa na engine']}
rp=root/'docs/reports/blender/coastal_cleanup_r30b62.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
e={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(root).as_posix(),'notes':'Limpeza local da triangulação da costura; pavimento integrado e colisão igual; núcleo e cais preservados.'}
for r in cat['revisions']:
 if r['file']==src['file']:r['status']='superseded_validation'
cat['revisions'].append(e);cat['validation_source']=e.copy();p.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'R30B.62','retriangulated_faces':len(bad),'zero_area_removed':removed,'degenerate_after':0}))
