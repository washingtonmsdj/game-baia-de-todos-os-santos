"""Passe de fachada limitado a três parcelas já modeladas; única sessão visível."""
import bpy, bmesh, json, runpy, hashlib
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
catalog = json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))
source = catalog['authoring_source']
assert source['revision'] == 'R30B.36'
assert Path(bpy.data.filepath).resolve() == (root/source['file']).resolve()
destination = root/'blender/salvador_lacerda_r30b37_fachadas_baixa.blend'
assert not destination.exists(), 'Não repetir a mutação de uma revisão existente'
data = json.loads((root/'artifacts/cidade-baixa/frontage_controls_r37.json').read_text(encoding='utf8'))
helpers = runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))
signature, wm = helpers['signature'], helpers['world_matrix']
Geometry = runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry']
r36 = json.loads((root/'docs/reports/blender/terracos_palacio_r30b36.json').read_text(encoding='utf8'))
r32 = json.loads((root/'docs/reports/blender/cidade_baixa_r30b32.json').read_text(encoding='utf8'))
targets = {row['body'] for row in data['buildings']} | {n for row in data['buildings'] for n in row['components']}
names = set(r36['protected_signatures']) | set(r36['final_scene_signatures']) | {r['object'] for r in r36['terrain']}
names |= set(r32['restored_bodies'] + r32['restored_existing_components']) | set(r32['road_signatures'])
protected = {n: signature(scene.objects[n]) for n in names-targets if n in scene.objects}
for row in data['buildings']:
    assert signature(scene.objects[row['body']]) == row['before'], 'Fonte mudou desde a inspeção'
if bpy.context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
col = bpy.data.collections.get('ENVIRONMENT_FINAL | Fachadas Cidade Baixa R37')
if col is None:
    col = bpy.data.collections.new('ENVIRONMENT_FINAL | Fachadas Cidade Baixa R37')
    scene.collection.children.link(col)
assert not col.objects, 'Passe parcial: revisar antes de repetir'
col['boas_role'] = 'visual_environment'
media = 'elevador-lacerda-panorama-783a31279c0d'
up = Vector((0,0,1)); changed = {}; created = []; rows = []

def material(label, color, rough=.8, metallic=0):
    m = bpy.data.materials.get('BAIXA R37 | '+label) or bpy.data.materials.new('BAIXA R37 | '+label); m.use_nodes = True
    m.diffuse_color = (*color,1)
    p = next(node for node in m.node_tree.nodes if node.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = m.diffuse_color
    p.inputs['Roughness'].default_value = rough; p.inputs['Metallic'].default_value = metallic
    return m

graytrim = material('nervuras de concreto cinza', (.40,.415,.39))
grayrecess = material('painéis recuados cinza', (.25,.265,.25))
glass = material('vidro esverdeado', (.14,.22,.20), .24)
next(node for node in glass.node_tree.nodes if node.type=='BSDF_PRINCIPLED').inputs['Transmission Weight'].default_value = .45
trim = bpy.data.materials['BAIXA R33 | cornija clara']
green = bpy.data.materials['BAIXA R33 | esquadrias verdes']
rose = bpy.data.materials['BAIXA R33 | lona rosada do toldo']

def install(name, geo, mat, body, bevel=.012):
    o = scene.objects.get(name)
    if o: changed[name] = {'before': signature(o)}
    inv = wm(o).inverted() if o else wm(body).inverted()
    me = bpy.data.meshes.new(name+' | R37')
    me.from_pydata([tuple(inv@Vector(v)) for v in geo.v], [], geo.f); me.materials.append(mat)
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); bm.to_mesh(me); bm.free(); me.update()
    if o: o.data = me
    else:
        o = bpy.data.objects.new(name,me); col.objects.link(o)
        o.parent = body; created.append(name)
    if bevel and not o.modifiers.get('Arestas de fachada R37'):
        mod = o.modifiers.new('Arestas de fachada R37','BEVEL'); mod.width = bevel; mod.segments = 2
    o['boas_revision'] = 'R30B.37'; o['reference_media_id'] = media
    o['reference_status'] = 'candidate'; o['classification'] = 'ADAPT_LOCAL'
    o['boas_role'] = 'visual_environment'; o['osm_way_id'] = str(body['osm_way_id'])
    o['boas_location_candidate'] = 'edificio-baixa-osm-'+str(body['osm_way_id'])
    return o

for row in data['buildings']:
    oid = row['osm_way_id']; body = scene.objects[row['body']]
    poly = [Vector((*p,0)) for p in row['controls_xy']]
    a,b = poly[:2]; t = (b-a).normalized(); length = (b-a).length
    n = Vector((-t.y,t.x,0)); centroid = sum(poly,Vector())/len(poly)
    if n.dot(centroid-(a+b)/2)>0: n = -n
    base,top = row['base_z'],row['top_z']; height = top-base
    floors,bays = row['candidate_floors'],row['candidate_bays']; pitch = length/bays
    prefix = f'BAIXA R33 | {oid} | '
    def P(x,z,d=0): return a+t*x+up*z+n*d
    def box(g,x,z,d,w,dep,h): g.box(P(x,z,d),(w,dep,h),(t,n,up))
    gh = 3.25; rh = (height-gh-.45)/(floors-1)
    openings=[]
    for level in range(floors):
        z = base+gh*.48 if level==0 else base+gh+(level-.5)*rh
        h = 2.62 if level==0 else rh*.62
        w = pitch*(.70 if level==0 else .56)
        openings += [((j+.5)*pitch,z,w,h,level,j) for j in range(bays)]
    # Malha da parede com espessura nos vãos; planta, base e altura preservadas.
    wall = Geometry()
    wall.panel(a,t,n,0,length,base,top,.26,[(x-w/2,x+w/2,z-h/2,z+h/2) for x,z,w,h,*_ in openings])
    for p,q in zip(poly[1:],poly[2:]+poly[:1]):
        wall.poly([p+up*base,q+up*base,q+up*top,p+up*top])
    wall.poly([p+up*top for p in poly]); wall.poly([p+up*base for p in reversed(poly)])
    install(body.name,wall,body.data.materials[0],body,0)
    frames, mould, sills, glazing, shutters, recess = [Geometry() for _ in range(6)]
    gray = oid==1220650503
    for x,z,w,h,level,j in openings:
        # Caixilho dentro do vão; vidro atrás dele, sem placas opacas na frente.
        for s in (-1,1):
            box(frames,x+s*(w/2-.035),z,-.17,.07,.08,h)
            box(frames,x,z+s*(h/2-.035),-.17,w,.08,.07)
        box(frames,x,z,-.17,.055,.085,h)
        box(frames,x,z+(.23 if gray else .12),-.17,w,.085,.05)
        glazing.poly([P(x-w/2,z-h/2,-.205),P(x+w/2,z-h/2,-.205),P(x+w/2,z+h/2,-.205),P(x-w/2,z+h/2,-.205)])
        if level:
            box(sills,x,z-h/2-.08,.07,w+.26,.32,.12)
            if not gray:
                for s in (-1,1):
                    box(mould,x+s*(w/2+.08),z,.045,.12,.15,h+.27)
                    box(mould,x,z+s*(h/2+.08),.045,w+.28,.15,.12)
                box(mould,x,z+h/2+.19,.08,w+.37,.23,.09)
        if oid==1263035780 and level==1:
            # Duas folhas verdes com travessas e venezianas; padrão candidato.
            for side in (-1,1):
                sx=x+side*w*.245; sw=w*.46; sh=h-.12
                for sign in (-1,1):
                    box(shutters,sx+sign*(sw/2-.035),z,-.10,.07,.055,sh)
                    box(shutters,sx,z+sign*(sh/2-.04),-.10,sw,.055,.08)
                box(shutters,sx,z,-.10,sw,.055,.07)
                count=max(4,int(sh/.115))
                for k in range(count):
                    box(shutters,sx,z-sh/2+.08+k*(sh-.16)/(count-1),-.115,sw-.11,.045,.073)
    # Perfis contínuos com pingadeira e coroamento escalonado.
    if gray:
        for j in range(bays+1):
            x=j*pitch; width=.33 if j not in (0,bays) else .25
            box(mould,x,base+gh+(height-gh)/2,.10,width,.26,height-gh+.48)
            box(mould,x,top+.20,.10,width+.035,.30,.45)
        for level in range(1,floors):
            z=base+gh+(level-1)*rh
            box(mould,length/2,z,.035,length,.15,.13)
            if level>1:
                for j in range(bays): box(recess,(j+.5)*pitch,z+rh*.13,.015,pitch-.40,.09,rh*.24)
        box(mould,length/2,top-.15,.06,length,.24,.18)
    else:
        for z,w,dep,h in ((base+gh,length,.24,.15),(top-.38,length,.28,.12),(top-.15,length+.08,.40,.13),(top+.03,length+.14,.49,.20)):
            box(mould,length/2,z,.06,w,dep,h)
    frame_name = 'vãos em sombra' if gray else ('esquadrias verdes' if oid==1263035780 else 'esquadrias azul escuro')
    frame_mat = bpy.data.materials['BAIXA R33 | '+frame_name]
    for label,g,m in [('Caixilhos',frames,frame_mat),('Cornijas e frisos',mould,graytrim if gray else trim),('Peitoris',sills,graytrim if gray else trim),('Vidros',glazing,glass)]:
        install(prefix+label,g,m,body,0 if label=='Vidros' else .012)
    if shutters.v: install(prefix+'Folhas verdes',shutters,green,body,.006)
    if recess.v: install(f'BAIXA R37 | {oid} | Painéis entre nervuras',recess,grayrecess,body)
    if oid==1263035780:
        awning=Geometry(); width=length-.24
        q=[P(.12,base+3.15),P(length-.12,base+3.15),P(length-.12,base+2.42,2.05),P(.12,base+2.42,2.05)]
        awning.poly(q); awning.poly([v-up*.035 for v in reversed(q)])
        for p,q2 in zip(q,q[1:]+q[:1]): awning.poly([p,q2,q2-up*.035,p-up*.035])
        box(awning,length/2,base+2.26,2.035,width,.04,.32)
        install(prefix+'Toldo rosado',awning,rose,body,.006)
    rows.append({'osm_way_id':oid,'body':body.name,'footprint_controls_xy':row['controls_xy'],'base_z_preserved':base,'top_z_preserved':top,'floors_candidate':floors,'bays_candidate':bays,'height_verified_m':None,'photo_binding_status':'candidate','wall_depth_candidate_m':.26,'unseen_sides':'Mantidos sem novas aberturas ou decoração.'})

bpy.context.view_layer.update()
for name,expected in protected.items(): assert signature(scene.objects[name])==expected, 'Mudança fora do escopo: '+name
for name in set(changed)|set(created):
    changed.setdefault(name,{})['after']=signature(scene.objects[name])
target=Vector((-70,36,16)); eye=Vector((-117,91,26))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active; rv=space.region_3d
            rv.view_location=target; rv.view_distance=(eye-target).length
            rv.view_rotation=(eye-target).to_track_quat('Z','Y'); space.shading.type='MATERIAL'
scene['boas_architectural_revision']='R30B.37 | Fachadas Cidade Baixa: vãos, cornijas, nervuras, esquadrias e toldo'
bpy.ops.wm.save_as_mainfile(filepath=str(destination))
with destination.open('rb') as f: sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'schema':'boas/cidade-baixa-facades-v1','revision':'R30B.37','source_before':source,'source_after':{'file':destination.relative_to(root).as_posix(),'sha256':sha,'revision':'R30B.37'},'status':'authoring_candidate','reference_media_id':media,'buildings':rows,'created_objects':created,'changed_objects':changed,'protected_signatures':protected,'terrain_roads_and_r36_unchanged':True,'runtime_exported':False,'research_performed':False,'visual_review':'pending','saved_datablocks_readback':'pending','limitations':['Correspondência foto/parcela e alturas ainda candidatas; nenhuma medida nova apresentada como levantamento.','Sem promoção de fidelidade global; limitações B36 mantidas.','Telhado cerâmico existente preservado: geometria da cobertura não legível suficientemente para reinterpretação.','Sem alteração de colisão ou prova de circulação neste passe de fachadas.']}
(root/'docs/reports/blender/cidade_baixa_r30b37.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'saved':report['source_after'],'changed':len(changed),'created':len(created),'protected':len(protected)},ensure_ascii=False))
