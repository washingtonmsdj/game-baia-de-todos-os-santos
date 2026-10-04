"""V22: encaixes reais de acessórios e circuitos de iluminação no Blender visível.

Não altera carroceria/folhas V20. Medidas das novas fixações são autorais candidatas.
"""
import bpy,bmesh,json,hashlib,struct,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='marrom_v21_montada.blend'
assert not bpy.app.is_job_running('RENDER') and not s.get('boas_v22_lights_applied')
source=Path(bpy.data.filepath);body=s.objects['HILUX | CARROCERIA PRINCIPAL'];root=s.objects['RDP01_ROOT | viatura']
checkpoint=r/'artifacts/vehicles/rondesp/v22-live-before.blend'
if not checkpoint.exists():bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
protected=json.loads((r/'docs/reports/blender/rondesp_marrom_v21.json').read_text(encoding='utf8'))['protected_mesh_hashes']
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
assert all(fingerprint(s.objects[n])==h for n,h in protected.items())
bpy.context.view_layer.update()
def tree(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear();return t
bt=tree(body);cap_tree=tree(s.objects['RDP01 | HILUX06 | Tampa traseira capota'])
black=bpy.data.materials['RDP01 | Polímero preto'];steel=bpy.data.materials['RDP01 | Aço preto rodas']
changes=[];added=[];contacts=[];edge_contacts=[]
def side_support(p,side):
 hit,*_=bt.ray_cast(Vector((side*2,p.y,p.z)),Vector((-side,0,0)),3)
 if hit is None or side*hit.x<.6:
  near,normal,index,distance=bt.find_nearest(p)
  assert near is not None and distance<.13 and side*near.x>.6 and near.y>2.4,("Sem suporte no canto traseiro",list(p))
  hit=near;edge_contacts.append({"point":list(p),"contact":list(hit),"distance_m":distance})
 return hit
def worldverts(ob):return [ob.matrix_world@v.co for v in ob.data.vertices]
def fit(ob,fn):
 mw=ob.matrix_world.copy();im=mw.inverted();dis=[]
 for v in ob.data.vertices:
  p=mw@v.co;q=fn(p);dis.append((q-p).length);v.co=im@q
 ob.data.update();ob['boas_v22_fit']='Conformed to current assembly; authored mounting dimensions'
 changes.append(ob.name);contacts.append({'object':ob.name,'max_vertex_displacement_m':max(dis,default=0)})
def inward(ob,thickness):
 mod=next((m for m in ob.modifiers if m.type=='SOLIDIFY'),None)
 if not mod:mod=ob.modifiers.new('Espessura interna da peça','SOLIDIFY')
 mod.offset=-1;mod.thickness=thickness;mod.use_quality_normals=True;mod.use_even_offset=False
# Corpos laterais assentados sobre a chapa, não no campo antigo da V06.
for side in [-1,1]:
 for key,offset,thickness in [('Base lanterna traseira',.010,.012),('Lente vermelha traseira',.014,.005)]:
  ob=s.objects[f'RDP01 | HILUX06 | {key} {side}']
  def sidefit(p):
   hit=side_support(p,side)
   return hit+Vector((side*offset,0,0))
  fit(ob,sidefit);inward(ob,thickness)
 for z in [1.095,.943,.767]:
  ob=s.objects[f'RDP01 | HILUX06 | Segmento lanterna {str((side,z))}']
  def segmentfit(p):
   hit=side_support(p,side)
   return hit+Vector((side*.0148,0,0))
  fit(ob,segmentfit)
 # Faixa posterior contorna o canto atual da caçamba, com alojamento próprio.
 ob=s.objects[f'RDP01 | HILUX06 | Retorno lanterna {side}'];vs=worldverts(ob)
 oldmin=min(abs(p.x) for p in vs);oldmax=max(abs(p.x) for p in vs)
 def backfit(p):
  hit=side_support(Vector((p.x,2.745,p.z)),side)
  outer=side*hit.x+.009;u=(abs(p.x)-oldmin)/(oldmax-oldmin)
  x=side*(outer-.122+.122*u)
  support,*_=bt.ray_cast(Vector((x,3.4,p.z)),Vector((0,-1,0)),3)
  assert support is not None and support.y>2.6
  return support+Vector((0,.014,0))
 fit(ob,backfit);inward(ob,.005)
 # A base posterior une lente e superfície da chapa; preserva o retorno separado.
 base=ob.copy();base.data=ob.data.copy();base.name=f'HILUX22 | Alojamento posterior lanterna {side}'
 bpy.data.collections['RDP01 | LUZES'].objects.link(base);base.data.materials.clear();base.data.materials.append(black)
 for v in base.data.vertices:
  p=base.matrix_world@v.co;p.y-=.004;v.co=base.matrix_world.inverted()@p
 inward(base,.012);base['boas_asset_id']='vehicle-rondesp-pickup';base['boas_component']='rear_light_housing';added.append(base.name)
# Puxador e terceira luz deixam de flutuar 12 cm atrás do conjunto.
ob=s.objects['RDP01 | Puxador tampa caçamba'];pv=worldverts(ob);lo,hi=min(p.y for p in pv),max(p.y for p in pv)
def handlefit(p):
 hit,*_=bt.ray_cast(Vector((p.x,3.4,p.z)),Vector((0,-1,0)),3);assert hit is not None and hit.y>2.7
 return hit+Vector((0,.001+(p.y-lo)/(hi-lo)*.027,0))
fit(ob,handlefit)
ob=s.objects['RDP01 | Terceira luz freio'];pv=worldverts(ob);lo,hi=min(p.y for p in pv),max(p.y for p in pv);zc=(min(p.z for p in pv)+max(p.z for p in pv))/2
# Apoio no quadro inferior da capota, abaixo do vidro; não atrás de um vão.
def brakefit(p):
 z=p.z-zc+1.326
 hit,*_=cap_tree.ray_cast(Vector((p.x,3.4,z)),Vector((0,-1,0)),3);assert hit is not None and hit.y>2.5
 return hit+Vector((0,.001+(p.y-lo)/(hi-lo)*.016,0))
fit(ob,brakefit)
# Para-choque com largura ajustada ao canto inferior, mantendo seu volume.
bumper_width=[]
for side in [-1,1]:
 hit,*_=bt.ray_cast(Vector((side*2,2.70,.630)),Vector((-side,0,0)),3);assert hit is not None
 outer=abs(hit.x)+.035;inner=.265;bumper_width.append(outer)
 for key in ['Asa para-choque','Piso antiderrapante']:
  ob=s.objects[f'RDP01 | HILUX10 | {key} {side}'];pv=worldverts(ob)
  def bumperfit(p):
   u=(abs(p.x)-.295)/.630
   return Vector((side*(inner+(outer-inner)*u),p.y,p.z))
  fit(ob,bumperfit)
# Fixações estruturalmente ligadas às longarinas existentes.
def box(name,center,dims,col,mat,bevel=.006):
 x,y,z=center;dx,dy,dz=[a/2 for a in dims]
 vs=[(x+a*dx,y+b*dy,z+c*dz) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.materials.append(mat);o=bpy.data.objects.new(name,me);col.objects.link(o);o.parent=root
 m=o.modifiers.new('Raios de fabricação candidatos','BEVEL');m.width=bevel;m.segments=3
 m=o.modifiers.new('Normais da peça','WEIGHTED_NORMAL');m.keep_sharp=True
 o['boas_asset_id']='vehicle-rondesp-pickup';o['boas_component']='mounting_support';o['boas_shape_status']='candidate; mounting geometry, not measured industrial dimensions';added.append(o.name);return o
col=bpy.data.collections['RDP01 | CHASSIS'];extensions=[]
for side in [-1,1]:
 rail=s.objects[f'RDP01 | Longarina {str(side*.51)}'];rv=worldverts(rail);end=max(p.y for p in rv);x=sum(p.x for p in rv)/len(rv);zlo,zhi=min(p.z for p in rv),max(p.z for p in rv)
 low=end-.025;high=2.785
 extension=box(f'HILUX22 | Prolongamento fixacao traseira {side}',(x,(low+high)/2,(zlo+zhi)/2),(.10,high-low,zhi-zlo),col,steel,.004)
 extensions.append({'object':extension.name,'source_rail':rail.name,'overlap_m':.025,'rear_end_m':high})
box('HILUX22 | Travessa suporte parachoque e engate',(0,2.700,.445),(1.16,.080,.130),col,steel,.005)
# Engate encurtado e ligado à travessa, sem bloco solto atrás do para-choque.
ob=s.objects['RDP01 | Engate reboque'];pv=worldverts(ob);lo,hi=min(p.y for p in pv),max(p.y for p in pv)
fit(ob,lambda p:Vector((p.x,2.660+(p.y-lo)/(hi-lo)*.366,p.z)))
ob=s.objects['RDP01 | Esfera engate'];pv=worldverts(ob);cy=sum(p.y for p in pv)/len(pv)
fit(ob,lambda p:Vector((p.x,p.y+3.015-cy,p.z)))
# Terminações dos suportes frontais agora alcançam as longarinas.
for side in [-1,1]:
 ob=s.objects[f'RDP01 | HILUX08 | Suporte estrutural {side}']
 fit(ob,lambda p:Vector((p.x+side*.08 if p.y> -2.21 else p.x,-2.045 if p.y> -2.21 else p.y,p.z)))
# Circuitos persistentes: propriedades nativas do Blender, sem dependência runtime.
controls={'giroflex_ligado':(1.,0.,1.,'Liga o sinalizador azul/vermelho; 0 desligado, 1 ligado.'),'giroflex_velocidade':(1.,.25,4.,'Velocidade das piscadas; controle visual, não frequência certificada.'),'farois_ligados':(1.,0.,1.,'Acende os faróis dianteiros e seus feixes.'),'lanternas_ligadas':(1.,0.,1.,'Acende as lanternas de posição traseiras.'),'freio':(0.,0.,1.,'0 sem freio; 1 acende luzes de freio e terceira luz.')}
for key,(val,lo,hi,desc) in controls.items():
 root[key]=val;root.id_properties_ui(key).update(min=lo,max=hi,soft_min=lo,soft_max=hi,description=desc)
root['boas_lighting_controls']='giroflex_ligado; giroflex_velocidade; farois_ligados; lanternas_ligadas; freio'
def driver(socket,expr,variables):
 d=socket.driver_add('default_value').driver;d.type='SCRIPTED'
 for symbol,key in variables:
  v=d.variables.new();v.name=symbol;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+key+'"]'
 d.expression=expr;return d
lighting=[]
def emitting(name,source_mat,color,expr,variables,base=None):
 m=source_mat.copy();m.name=name;bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Emission Color'].default_value=(*color,1)
 if base is not None:bs.inputs['Base Color'].default_value=(*base,1);m.diffuse_color=(*base,1)
 driver(bs.inputs['Emission Strength'],expr,variables);lighting.append({'material':m.name,'expression':expr,'controls':variables});return m
pulse={-1:'(((frame-1)*vel)%16<3 or 6<=((frame-1)*vel)%16<9)',1:'(8<=((frame-1)*vel)%16<11 or 14<=((frame-1)*vel)%16<16)'}
bar_led={};bar_lens={}
for side,color,base,label in [(-1,(.003,.035,1),(.004,.055,.48),'AZUL ESQUERDO'),(1,(1,.002,.005),(.48,.004,.008),'VERMELHO DIREITO')]:
 var=[('liga','giroflex_ligado'),('vel','giroflex_velocidade')]
 bar_led[side]=emitting('HILUX22 | LED '+label,bpy.data.materials['RDP01 | HILUX10 LED vermelho'],color,'liga*(.02+5*'+pulse[side]+')',var,base)
 bar_lens[side]=emitting('HILUX22 | Lente '+label,bpy.data.materials['RDP01 | Lentes vermelhas'],color,'liga*(.01+1.6*'+pulse[side]+')',var,base)
# Usar a posição efetiva, pois o primeiro número dos módulos indica frente/trás.
for ob in s.objects:
 if any(t in ob.name for t in ['Módulo sinalizador','LED lateral','Lente externa vermelha','Extremidade vermelha']):
  vs=worldverts(ob);side=-1 if sum(p.x for p in vs)/len(vs)<0 else 1
  ob.data.materials[0]=bar_led[side] if ('Módulo' in ob.name or 'LED lateral' in ob.name) else bar_lens[side]
  ob['boas_light_role']='lightbar';ob['boas_light_color']='blue' if side==-1 else 'red'
rearpos=emitting('HILUX22 | Lanterna posicao vermelha',bpy.data.materials['RDP01 | Lentes vermelhas'],(1,.003,.006),'1.4*pos', [('pos','lanternas_ligadas')])
rearbrake=emitting('HILUX22 | Lanterna e freio vermelhos',bpy.data.materials['RDP01 | Lentes vermelhas'],(1,.003,.006),'1.0*pos+6.0*freia',[('pos','lanternas_ligadas'),('freia','freio')])
third=emitting('HILUX22 | Terceira luz freio',bpy.data.materials['RDP01 | Lentes vermelhas'],(1,.003,.006),'6.0*freia',[('freia','freio')])
white=emitting('HILUX22 | Nucleo farol branco',bpy.data.materials['RDP01 | Metal acetinado'],(1,.94,.82),'8.0*aceso',[('aceso','farois_ligados')],(.70,.72,.75))
white.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.1
whiteguide=emitting('HILUX22 | Guia optica branca',bpy.data.materials['RDP01 | Metal acetinado'],(1,.94,.84),'4.0*aceso',[('aceso','farois_ligados')])
frontglass=emitting('HILUX22 | Lente farol iluminada',bpy.data.materials['RDP01 | Lentes transparentes'],(1,.94,.84),'.6*aceso',[('aceso','farois_ligados')])
for side in [-1,1]:
 for key in ['Lente vermelha traseira','Retorno lanterna']:s.objects[f'RDP01 | HILUX06 | {key} {side}'].data.materials[0]=rearbrake
 for z in [1.095,.767]:s.objects[f'RDP01 | HILUX06 | Segmento lanterna {str((side,z))}'].data.materials[0]=rearbrake if z==1.095 else rearpos
 for j in [0,1]:s.objects[f'RDP01 | HILUX06 | Núcleo óptico {str((side,j))}'].data.materials[0]=white
 s.objects[f'RDP01 | HILUX06 | Guia óptica {side}'].data.materials[0]=whiteguide
 s.objects[f'RDP01 | HILUX06 | Lente óptica transparente {side}'].data.materials[0]=frontglass
s.objects['RDP01 | Terceira luz freio'].data.materials[0]=third
# Luzes reais além da emissão das lentes; feixes dianteiros e reflexo do giroflex.
def light_driver(data,expr,variables):
 d=data.driver_add('energy').driver;d.type='SCRIPTED'
 for symbol,key in variables:
  v=d.variables.new();v.name=symbol;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+key+'"]'
 d.expression=expr
lightscol=bpy.data.collections['RDP01 | LUZES'];lightobjs=[]
for side in [-1,1]:
 bulb=s.objects[f'RDP01 | HILUX06 | Núcleo óptico {str((side,0))}'];pts=worldverts(bulb);center=sum(pts,Vector((0,0,0)))/len(pts)
 data=bpy.data.lights.new(f'HILUX22 | Feixe farol {side}','SPOT');data.color=(1,.94,.83);data.spot_size=math.radians(52);data.spot_blend=.50;data.shadow_soft_size=.055
 ob=bpy.data.objects.new(data.name,data);lightscol.objects.link(ob);ob.parent=root;ob.location=center+Vector((0,-.045,0));ob.rotation_euler=(Vector((side*.8,-12,.02))-ob.location).to_track_quat('-Z','Y').to_euler();light_driver(data,'120*aceso',[('aceso','farois_ligados')]);added.append(ob.name);lightobjs.append(ob.name)
 data=bpy.data.lights.new(f'HILUX22 | Reflexo giroflex {side}','POINT');data.color=(.003,.035,1) if side==-1 else (1,.002,.005);data.shadow_soft_size=.08
 ob=bpy.data.objects.new(data.name,data);lightscol.objects.link(ob);ob.parent=root;ob.location=(side*.40,.035,1.985);light_driver(data,'18*liga*'+pulse[side],[('liga','giroflex_ligado'),('vel','giroflex_velocidade')]);added.append(ob.name);lightobjs.append(ob.name)
notes=bpy.data.texts.new('HILUX22 | CONTROLES DAS LUZES');notes.write('Controles no objeto RDP01_ROOT | viatura, em Propriedades personalizadas.\nGiroflex: giroflex_ligado 0/1; giroflex_velocidade 0,25–4. Pressione Espaço para animar.\nAzul no lado esquerdo do veículo (X negativo), vermelho no direito (X positivo).\nFaróis: farois_ligados 0/1. Traseiras: lanternas_ligadas 0/1. Freio: freio 0–1.\nFreio intensifica as lanternas e liga a terceira luz. Feixes reais independentes.\nV22 candidata: fixações autorais, sem medidas industriais ou integração runtime.\n')
s.frame_start=1;s.frame_end=32;s.render.fps=24;s.frame_set(1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='MATERIAL';area.spaces.active.shading.use_scene_lights=True;area.spaces.active.shading.use_scene_world=True
for ob in s.objects:ob.select_set(False)
root.select_set(True);bpy.context.view_layer.objects.active=root
# Recriar dependências dos drivers após ligar materiais aos objetos.
root.update_tag()
for mat in bpy.data.materials:
 if mat.name.startswith('HILUX22') and mat.use_nodes and mat.node_tree.animation_data:
  for curve in mat.node_tree.animation_data.drivers:curve.driver.expression=curve.driver.expression
  mat.node_tree.update_tag();mat.update_tag()
s.frame_set(2);s.frame_set(1)
s['boas_v22_lights_applied']=True;s['boas_authoring_mode']='assembled_review';s['boas_next_scope']='Revisão dos circuitos de luz e encaixes traseiros; fidelidade fina da forma continua candidata.'
bpy.context.view_layer.update()
assert all(fingerprint(s.objects[n])==h for n,h in protected.items())
report={'asset_id':'vehicle-rondesp-pickup','status':'candidate','parent':source.relative_to(r).as_posix(),'parent_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'base_body_and_doors_unchanged':True,'protected_mesh_hashes':protected,'changed_attachments':changes,'added_components':added,'attachment_displacements':contacts,'corner_contacts':edge_contacts,'rear_rail_extensions':extensions,'bumper_outer_width_per_side_m':bumper_width,'controls':{k:{'default':v[0],'min':v[1],'max':v[2],'description':v[3]} for k,v in controls.items()},'lighting_materials':lighting,'projection_lights':lightobjs,'lightbar_sides':{'left_negative_x':'blue','right_positive_x':'red'},'source_reopened':False,'runtime_exported':False,'visual_review':'pending','pending':['Dimensões de fixação e forma finais candidatas.','Brasão detalhado e desenho exato da camuflagem pendentes.','Circuitos Blender ainda sem adaptação a runtime.']}
(r/'docs/reports/blender/rondesp_marrom_v22.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'attachment_changes':len(changes),'added_components':len(added),'lighting_materials':len(lighting),'body_and_doors_unchanged':True}))
