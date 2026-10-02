"""Passe limitado à foto enviada: três parcelas existentes e acabamento da fonte.

Não modifica relevo, vias, proxy, obras B23 recuperadas ou asset da escultura.
Implantação OSM preservada; correspondência fotográfica e alturas candidatas.
"""
import bpy,bmesh,json,math,hashlib,runpy
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
catalog=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))
before=catalog['authoring_source'];assert before['revision']=='R30B.32'
assert Path(bpy.data.filepath).resolve()==(root/before['file']).resolve()
base=json.loads((root/'docs/reports/blender/cidade_baixa_r30b32.json').read_text(encoding='utf8'))
signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
for name,expected in base['road_signatures'].items():assert signature(scene.objects[name])==expected
preserved={n:signature(scene.objects[n]) for n in base['restored_bodies']+base['restored_existing_components']}
if bpy.context.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.update()
colname='ENVIRONMENT_FINAL | Cidade Baixa fotografia R33'
assert bpy.data.collections.get(colname) is None,'Passe já iniciado; revisar estado, não repetir'
col=bpy.data.collections.new(colname);scene.collection.children.link(col);col['boas_role']='visual_environment'
media='elevador-lacerda-panorama-783a31279c0d';created=[];rows=[]

def mat(name,color,rough=.75,metal=0,glass=0):
    m=bpy.data.materials.new('BAIXA R33 | '+name);m.use_nodes=True;m.diffuse_color=(*color,1)
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=m.diffuse_color
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Transmission Weight'].default_value=glass
    if not glass:
        noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=65
        bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.11;bump.inputs['Distance'].default_value=.009
        m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    return m
white=mat('reboco branco quente',(.80,.78,.70));trim=mat('cornija clara',(.87,.84,.75));green=mat('esquadrias verdes',(.17,.29,.21),.6)
blue=mat('esquadrias azul escuro',(.055,.16,.27),.56);gray=mat('reboco cinza',(.42,.43,.40));dark=mat('vãos em sombra',(.04,.048,.045),.8)
glass=mat('vidro de fachada',(.23,.29,.26),.25,glass=.55);rose=mat('lona rosada do toldo',(.61,.31,.29),.92)
tile=mat('telha cerâmica',(.47,.20,.10));roofgray=mat('cobertura existente cinza',(.30,.30,.28))
up=Vector((0,0,1))
def mesh(name,vv,ff,material,props,parent=None):
    me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.materials.append(material);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);col.objects.link(o)
    if parent:o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted()
    for k,v in props.items():o[k]=v
    created.append(o.name);return o

# Frente de cada parcela indicada pela aresta frontal original; não criar outra planta.
# Alturas: leitura proporcional de pavimentos na foto, não levantamento métrico.
specs=[(1263035780,3,11.3,7,white,green,'white_green_rose_awning'),(1220650507,3,10.4,3,white,blue,'narrow_blue'),(1220650503,6,21.0,4,gray,dark,'gray_vertical_ribs')]
rows=runpy.run_path(str(root/'automation/blender/photo_frontage_geometry.py'))['model_frontages'](scene,specs,{'trim':trim,'green':green,'glass':glass,'rose':rose,'tile':tile,'gray':gray},mesh,signature,media)

# Pátio circular da fonte: acabamento visual apoiado na mesh existente, não novo chão.
terrain=scene.objects['MVP | terreno corrigido | colisão estática'];terrain.data.calc_loop_triangles()
triangles=list(terrain.data.loop_triangles);ground=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in terrain.data.vertices],[list(t.vertices) for t in triangles],all_triangles=True)
basin=scene.objects['CAIRU | bacia da fonte OSM'];points=[basin.matrix_world@Vector(p) for p in basin.bound_box]
center=Vector(((min(p.x for p in points)+max(p.x for p in points))/2,(min(p.y for p in points)+max(p.y for p in points))/2,0))
radius=(max(p.x for p in points)-min(p.x for p in points))/2;vv=[];ff=[];material_indices=[];segments=128;clearance=.004
for r in (radius+.02,radius+.24,radius+1.20,radius+1.40):
    for j in range(segments):
        theta=2*math.pi*j/segments;x=center.x+r*math.cos(theta);y=center.y+r*math.sin(theta)
        hit=ground.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),300)
        assert hit[0] is not None,'Sem apoio no acabamento da fonte';vv.append((x,y,hit[0].z+clearance))
for row in range(3):
    for j in range(segments):
        ids=[row*segments+j,row*segments+(j+1)%segments,(row+1)*segments+(j+1)%segments,(row+1)*segments+j]
        middle=sum((Vector(vv[k]) for k in ids),Vector())/4;hit=ground.ray_cast(middle+up*2,Vector((0,0,-1)),4)
        material=terrain.data.materials[terrain.data.polygons[triangles[hit[2]].polygon_index].material_index] if hit[0] else None
        if material and any(word in material.name.lower() for word in ('asfalto','rua chile','ladeira')):continue
        ff.append(tuple(ids));material_indices.append(0 if row in (0,2) else 1)
props={'boas_role':'visual_surface_finish','boas_revision':'R30B.33','reference_media_id':media,'reference_status':'candidate','classification':'ADAPT_LOCAL','boas_location_candidate':'monumento-mario-cravo','surface_clearance_m':clearance,'clearance_reason':'Camada de acabamento visual conformada ao chão existente, para evitar z-fighting; sem deslocamento geográfico ou collider adicional.','ring_width_verified_m':'null','ring_width_candidate_m':1.4}
paving=mat('pavimento miúdo ao redor da fonte',(.38,.39,.36));outline=mat('faixas claras da fonte',(.84,.83,.76))
o=mesh('BAIXA R33 | Fonte | Piso e faixas concêntricas',vv,ff,outline,props);o.data.materials.append(paving)
for p,i in zip(o.data.polygons,material_indices):p.material_index=i
water=mat('água azul da fonte',(.08,.27,.36),.18,glass=.35)
n=water.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=9
bump=water.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.10;bump.inputs['Distance'].default_value=.008
water.node_tree.links.new(n.outputs['Fac'],bump.inputs['Height']);water.node_tree.links.new(bump.outputs['Normal'],next(p for p in water.node_tree.nodes if p.type=='BSDF_PRINCIPLED').inputs['Normal'])
floor=scene.objects['CAIRU | fundo da bacia'];floor.data=floor.data.copy();floor.data.materials.clear();floor.data.materials.append(water)
floor['boas_revision']='R30B.33';floor['reference_media_id']=media
# Confirmar somente o escopo que permaneceu inalterado; não é bateria de testes de jogo.
bpy.context.view_layer.update()
for name,expected in base['road_signatures'].items():assert signature(scene.objects[name])==expected
for name,expected in preserved.items():assert signature(scene.objects[name])==expected
target=Vector((-67,42,16));pos=Vector((-133,109,39))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.region_3d.view_location=target;space.region_3d.view_distance=(target-pos).length
            space.region_3d.view_rotation=(target-pos).to_track_quat('Z','Y');space.shading.type='MATERIAL';space.clip_end=3000
scene['boas_architectural_revision']='R30B.33 | Foto: fachadas a sul, toldo, acabamento da fonte; recuperação B23 e terreno B30 preservados'
destination=root/'blender/salvador_lacerda_r30b33_fachadas_foto_cairu.blend';bpy.ops.wm.save_as_mainfile(filepath=str(destination))
with destination.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
report={'source_before':before,'source_after':{'file':destination.relative_to(root).as_posix(),'sha256':sha,'revision':'R30B.33','scene':scene.name},'reference_media_id':media,'research_performed':False,'buildings':rows,'created_objects':created,'preserved_b23_components':list(preserved),'terrain_and_collision_unchanged_from_b30':True,'road_signatures':base['road_signatures'],'reopened':False,'runtime_exported':False,'status':'authoring_candidate','monument':{'linked_sculpture_changed':False,'placement_changed':False,'surface_ring_radius_m':radius,'ring_width_candidate_m':1.4,'water_material_updated':True},'deferred':['Casarão em ruína no morro: geometria visível, mas sem correspondência de footprint/implantação confirmada; não instanciado por aproximação.','Outros edifícios, fundos, interiores e ornamentos ilegíveis: aguardar outra referência.','Não aprova altura real, correspondência fotográfica das três parcelas ou asset inteiro.'],'known_road_limitations':base['known_limitations']}
(root/'docs/reports/blender/cidade_baixa_r30b33.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'saved':report['source_after']['file'],'buildings':len(rows),'created_components':len(created),'source_sha256':sha,'terrain_changed':False,'recovered_b23_preserved':True},ensure_ascii=False))
