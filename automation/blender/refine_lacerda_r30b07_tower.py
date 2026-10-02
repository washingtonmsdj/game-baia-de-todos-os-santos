"""Refino visual da torre e acesso baixo, preservando implantação e mecanismos."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b06_espaco_publico.blend')
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
col=bpy.data.collections.new('HERO | Lacerda | torre e entrada R30B07');bpy.context.scene.collection.children.link(col)
ivory=bpy.data.materials['LAC R30B | reboco marfim fino'];dark=bpy.data.materials['LAC R30B | sombra veneziana'];frame=bpy.data.materials['LAC R30B | esquadria clara acetinada']
def mesh(name,v,f,mat):
 me=bpy.data.meshes.new(name);me.from_pydata([R@Vector(p) for p in v],[],f);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mat)
 o=bpy.data.objects.new('LAC R30B07 | '+name,me);col.objects.link(o);o['boas_location_id']='elevador-lacerda';o['boas_role']='visual_architecture';o['classification']='ADAPT_LOCAL';o['reference_status']='partial';return o
def boxes(name,items,mat):
 v=[];f=[]
 for p,s in items:
  k=len(v);x,y,z=[n/2 for n in s];v.extend(tuple(Vector(p)+Vector(q)) for q in [(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)])
  f.extend(tuple(k+i for i in q) for q in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])
 return mesh(name,v,f,mat)
hidden=[]
def supersede(o):
 o.hide_render=True;o.hide_set(True);o['superseded_by']='R30B07';hidden.append(o.name)
for o in list(bpy.context.scene.objects):
 if o.name.startswith(('CALIBRADO | vão vertical torre','TORRE | janela técnica','LAC R30B | TORRE | janela técnica','TORRE | consolo ')):supersede(o)
 if o.name.startswith(('TORRE | fresta tecnica superior','LAC R30B | TORRE | fresta tecnica superior')):supersede(o)
# Cinco patamares de venezianas em dois grupos triplos: proporções visuais, não levantamento.
slots=[];blades=[];backs=[]
for z,h in [(16.0,2.8),(27.2,3.2),(39.0,3.1),(51.0,3.0),(62.4,2.8)]:
 for yc in [2.20,6.20]:
  for j in [-1,0,1]:
   y=yc+j*.49;slots.append(((-70.36,y,z),(.8,.34,h)))
   backs.append(((-70.265,y,z),(.016,.34,h)))
   n=round(h/.105)
   for k in range(n):blades.append(((-70.475,y,z-h/2+(k+.5)*h/n),(.065,.325,.038)))
wall=bpy.data.objects['CASCA | fachada poço']
bm=bmesh.new();bm.from_mesh(wall.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(wall.data);bm.free()
cutter=boxes('cortador venezianas',slots,ivory);mod=wall.modifiers.new('Venezianas agrupadas R30B07','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
bpy.context.view_layer.objects.active=wall;bpy.ops.object.modifier_apply(modifier=mod.name);me=cutter.data;bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(me)
boxes('torre | fundos recuados',backs,dark);boxes('torre | laminas venezianas',blades,frame)
# Corpo técnico: mesma linguagem dos grupos de três, com três registros verticais.
blades=[];backs=[]
for x in [-70.49,-66.90]:
 for z,h in [(75.3,.60),(78.3,1.65),(81.8,1.65)]:
  for yc in [2.20,6.20]:
   for j in [-1,0,1]:
    y=yc+j*.49;backs.append(((x,y,z),(.025,.34,h)))
    for k in range(round(h/.10)):blades.append(((x+(-.018 if x<-68 else .018),y,z-h/2+.05+k*.10),(.045,.325,.035)))
boxes('corpo tecnico | fundos venezianas',backs,dark);boxes('corpo tecnico | laminas',blades,frame)
# Consolo contínuo em vez de três caixas empilhadas; mesmas cotas de ligação.
rings=[(-70.55,-66.85,.35,8.14,67.2),(-73.1,-64.3,-.86,9.34,69.9)]
v=[]
for a,b,c,d,z in rings:v.extend([(a,c,z),(b,c,z),(b,d,z),(a,d,z)])
mesh('galeria | consolo inclinado',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ivory)
# Frisos de pouca projeção, sem nervuras duplicadas da revisão calibrada.
for o in bpy.context.scene.objects:
 if o.name.startswith('CALIBRADO | friso vertical torre'):supersede(o)
 if o.name.startswith('TORRE | nervura vertical'):
  inv=o.matrix_world.inverted()
  for vertex in o.data.vertices:
   p=I@o.matrix_world@vertex.co
   if p.x<-68:p.x=-70.47+(p.x+70.54)*.25
   else:p.x=-66.92+(p.x+66.85)*.25
   vertex.co=inv@R@p
# Portais existentes conservam passagem livre; revestimento canelado nos pilares.
items=[]
for yc in [-.69,2.59,5.89,9.14]:
 items.append(((-82.37,yc,9.64),(.14,.46,4.47)))
 for j in [-2,-1,0,1,2]:items.append(((-82.46,yc+j*.08,9.64),(.035,.034,4.47)))
boxes('Cidade Baixa | pilastras caneladas',items,ivory)
boxes('Cidade Baixa | linhas do forro',[((-82.9,y,11.91),(1.75,.045,.045)) for y in [-1.7,-.6,.5,1.6,2.7,3.8,4.9,6.,7.1,8.2,9.3,10.4]],ivory)
boxes('Cidade Baixa | arremates laterais marquise',[((-82.45,y,12.12),(3.,.12,.26)) for y in [-2.60,11.08]],ivory)
for o in bpy.data.objects:
 if o.name.startswith('FACHADA INFERIOR | bandeira'):
  o.data.materials.clear();o.data.materials.append(bpy.data.materials['LAC R30B | vidro incolor transparente'])
 if o.name.startswith('FACHADA INFERIOR | pilastra'):o.data.materials.clear();o.data.materials.append(ivory)
bpy.context.scene['lacerda_revision']='R30B.07 | torre e entrada baixa'
dest=ROOT/'blender/salvador_lacerda_r30b07_torre_entrada.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'revision':dest.name,'new_objects':len(col.objects),'superseded':hidden,'references':['elevador-lacerda-oblique_left-ca2c56d9b78b','elevador-lacerda-front-2d9b4031ff6a'],'status':'partial','geography_changed':False,'tower_openings':len(slots)}
(ROOT/'artifacts/lacerda/r30b07_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'saved':dest.name,'openings':len(slots),'objects':len(col.objects)}))
