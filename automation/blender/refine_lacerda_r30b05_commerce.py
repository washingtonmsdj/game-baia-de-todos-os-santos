"""Frente comercial adjacente: associação à foto candidata, footprint preservado."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b04_entorno.blend')
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
col=bpy.data.collections.new('ENVIRONMENT_FINAL | comercio Lacerda R30B05');bpy.context.scene.collection.children.link(col)
base=next(o for o in bpy.data.objects if str(o.get('osm_way_id',''))=='1263035779')
ivory=bpy.data.materials['LAC R30B | reboco marfim fino'];dark=bpy.data.materials['LAC R30B | sombra veneziana']
pink=bpy.data.materials.new('ENTORNO LAC | rosa comercio referencia');pink.diffuse_color=(.64,.31,.38,1);pink.use_nodes=True
p=next(n for n in pink.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=pink.diffuse_color;p.inputs['Roughness'].default_value=.8
base.data.materials.clear();base.data.materials.append(ivory)
a=Vector((-78.351,11.7,0));b=Vector((-76.243,26.987,0));t=(b-a).normalized();normal=Vector((-t.y,t.x,0));L=(b-a).length

def parts(name,items,material):
    vv=[];ff=[]
    for s,z,width,height,depth,out in items:
        center=a+t*s+normal*out+Vector((0,0,z));k=len(vv)
        for x,y,h in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:
            vv.append(tuple(R@(center+normal*x*depth/2+t*y*width/2+Vector((0,0,h*height/2)))))
        ff.extend(tuple(k+i for i in f) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])
    me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.update();me.materials.append(material)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new('ENTORNO LAC | '+name,me);col.objects.link(o)
    o['osm_way_id']='1263035779';o['boas_role']='visual_environment';o['classification']='ADAPT_LOCAL';o['reference_status']='candidate';o['reference_media_id']='elevador-lacerda-front-2d9b4031ff6a';o['identity_note']='OSM shop=bakery e posição adjacente compatíveis; identidade comercial Cayru ainda candidata.'
    return o

parts('Comercio adjacente | faixas rosadas',[(L/2,10.65,L,.9,.10,.08),(L/2,13.80,L,1.05,.10,.08)],pink)
parts('Comercio adjacente | coroamento e embasamento',[(L/2,16.13,L+.1,.25,.2,.06),(L/2,7.45,L,.28,.12,.08)],ivory)
panels=[];frames=[];lattice=[]
for j in range(3):
    s=(j+.5)*L/3;w=L/3-.4
    panels.append((s,8.85,w,2.55,.07,.035))
    for z,h in [(12.10,1.9),(15.15,1.45)]:
        panels.append((s,z,w,h,.07,.035))
        for side in [-1,1]:frames.append((s+side*(w/2+.06),z,.12,h+.12,.16,.09))
        # Painel vazado consolidado: geometria de barras; não centenas de objetos.
        for k in range(math.ceil(w/.18)):
            ss=s-w/2+(k+.5)*w/math.ceil(w/.18);lattice.append((ss,z,.045,h,.065,.105))
        for k in range(math.ceil(h/.18)):
            zz=z-h/2+(k+.5)*h/math.ceil(h/.18);lattice.append((s,zz,w,.04,.065,.105))
    frames.extend([(s-w/2-.08,8.85,.16,2.75,.18,.1),(s+w/2+.08,8.85,.16,2.75,.18,.1)])
parts('Comercio adjacente | aberturas visuais',panels,dark)
parts('Comercio adjacente | pilares e ombreiras',frames,ivory)
parts('Comercio adjacente | paineis vazados',lattice,ivory)

# Toldo Vissor: substituir a seção horizontal provisória por queda suave para a rua.
awning=bpy.data.objects.get('ENTORNO LAC | Vissor | toldo amarelo')
if awning:
    va=Vector((-73.391,40.609,0));vt=(Vector((-72.395,47.712,0))-va).normalized();vn=Vector((-vt.y,vt.x,0))
    for v in awning.data.vertices:
        q=I@v.co;d=(q-va).dot(vn);q.z-=max(0,d-.045)*.22;v.co=R@q
    awning['revision_note']='R30B05: inclinação do toldo conforme leitura da foto; dimensão aproximada.'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D' and area.spaces.active.local_view:
        with bpy.context.temp_override(area=area,region=next(r for r in area.regions if r.type=='WINDOW')):bpy.ops.view3d.localview(frame_selected=False)
bpy.context.scene['lacerda_revision']='R30B.05 | frente comercial adjacente'
dest=ROOT/'blender/salvador_lacerda_r30b05_comercio.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest))
(ROOT/'artifacts/lacerda/r30b05_report.json').write_text(json.dumps({'file':dest.name,'objects_added':len(col.objects),'footprint_unchanged':True,'height_unchanged':True,'osm_way_id':'1263035779','identity_status':'candidate','interior_accessible':False,'geometry_type':'fachada visual sobre bloco existente'},ensure_ascii=False,indent=2),encoding='utf8')
print('Salvo',dest.name,'objetos',len(col.objects))
