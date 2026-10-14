"""Consolidar contrato e referência real na única sessão visível, sem mover o núcleo."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
registry=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))
source=registry['validation_source']
assert source['revision']=='R30B.75' and Path(bpy.data.filepath).resolve()==(root/source['file']).resolve()
contract_path=root/'world/geographic-reference.json';contract=json.loads(contract_path.read_text(encoding='utf8'))
sha=hashlib.sha256(contract_path.read_bytes()).hexdigest()
scene=bpy.context.scene
assert scene.unit_settings.scale_length==1
assert not bpy.data.objects.get('B76 | Campo da Polvora | footprint OSM')
role_map={
 'WORLD':('19 MVP | terreno DEM e acessos corrigidos','21 MVP | ruas e calçadas OSM Aleph','24 ORLA | Baía de Todos-os-Santos e cais OSM','26 RELEVO | revisão completa','36 VISUAL | OCEANO R30A8','40 | EXPANSAO CENTRO | REFERENCE_TERRAIN','WATER | Dique do Tororo | candidato B74'),
 'CITY_MASSING':('20 MVP | edifícios OSM do Aleph',),
 'PLAYABLE_CORE':('32 GAMEPLAY | SEMANTIC LAYERS R30A4','33 GAMEPLAY | RUNTIME PROXIES R30A5','34 GAMEPLAY | COLLISION CHUNKS R30A6','37 GAMEPLAY | NAV HINTS R30A9','09 CIDADE BAIXA | vias calcadas mercado modelo','15 PRACA ALTA | contorno e acesso','23 PRAÇA CAIRU | implantação OSM e mobiliário'),
 'HERO_ASSETS':('06 PREFEITURA | Palacio Thome de Souza','07 PRACA E PALACIO RIO BRANCO | esboco','08 ELEVADOR E TERRENO | dimensoes calibradas','10 MERCADO MODELO | interior e subsolo','11 ELEVADOR LACERDA | interior jogavel','12 LACERDA | exterior fotografico','17 MERCADO | casca MCP','18 FRENTE DO ELEVADOR | Palacio e Camara')}
changed=[];missing=[]
for role,names in role_map.items():
    for name in names:
        c=bpy.data.collections.get(name)
        if not c:missing.append(name);continue
        c['boas_detail_level']=role;c['boas_geographic_ssot_id']=contract['ssot_id'];changed.append({'collection':name,'detail_level':role,'existing_role_preserved':c.get('boas_role')})
for c in bpy.data.collections:
    if not c.library and c.name.startswith('HERO |'):
        c['boas_detail_level']='HERO_ASSETS';c['boas_geographic_ssot_id']=contract['ssot_id']
reference=bpy.data.collections.get('SOURCE_GEOREF | CENTRO LAPA TORORO FONTE NOVA')
assert reference is not None
reference['boas_detail_level']='GEOGRAPHIC_REFERENCE';reference['boas_geographic_ssot_id']=contract['ssot_id']
trees=[]
for ob in scene.objects:
    if ob.type=='MESH' and (ob.name in ('MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B74 | TERRENO | Lapa Tororo Fonte Nova | candidato') or ob.name.startswith('B75 | passeio OSM ')):
        trees.append(BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]))
data=json.loads((root/'artifacts/geographic-foundation/campo-da-polvora.json').read_text(encoding='utf8'))
points=[]
for a,b in zip(data['blender_xy'],data['blender_xy'][1:]):
    count=max(1,math.ceil(math.dist(a,b)/5))
    for i in range(count):
        t=i/count;x=a[0]+t*(b[0]-a[0]);y=a[1]+t*(b[1]-a[1])
        hits=[tree.ray_cast(Vector((x,y,500)),Vector((0,0,-1)),1000)[0] for tree in trees]
        hits=[h.z for h in hits if h is not None]
        assert hits, 'Campo sem terreno existente; não inventar altitude'
        points.append((x,y,max(hits)))
curve=bpy.data.curves.new('B76 | Campo da Polvora | fonte','CURVE');curve.dimensions='3D'
curve.bevel_depth=.12 # espessura visual de guia, não largura real
spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
for p,co in zip(spline.points,points):p.co=(*co,1)
spline.use_cyclic_u=True
ob=bpy.data.objects.new('B76 | Campo da Polvora | footprint OSM',curve);reference.objects.link(ob)
ob.hide_render=True;ob['boas_location_id']='campo-da-polvora';ob['boas_osm_id']=257336400;ob['boas_osm_type']='way'
ob['boas_role']='REFERENCE_OSM';ob['boas_source_reference']=True;ob['boas_production_ready']=False
ob['boas_geographic_ssot_id']=contract['ssot_id'];ob['boas_source_capture_id']=data['capture_id'];ob['boas_altitude_status']='sampled_existing_candidate_ground'
scene['boas_geographic_ssot']='world/geographic-reference.json';scene['boas_geographic_ssot_id']=contract['ssot_id'];scene['boas_geographic_ssot_sha256']=sha
scene['boas_geographic_absolute_status']='candidate';scene['boas_expansion_detail_status']='greybox_only'
text=bpy.data.texts.new('B76 | CONTRATO GEOGRAFICO')
text.write(contract_path.read_text(encoding='utf8'))
destination=root/'blender/salvador_lacerda_r30b76_fundacao_geografica.blend'
assert not destination.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
report={'revision':'R30B.76','parent':source['file'],'file':destination.relative_to(root).as_posix(),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'ssot_sha256':sha,'classified_existing_collections':changed,'missing_optional_collection_names':missing,'added_object':ob.name,'campo_points':len(points),'existing_geometry_changed':False,'existing_hierarchy_changed':False,'absolute_geography_verified':False,'runtime_promoted':False}
folder=root/'docs/reports/blender/geographic-foundation';folder.mkdir(parents=True,exist_ok=True)
(folder/'application_b76.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
