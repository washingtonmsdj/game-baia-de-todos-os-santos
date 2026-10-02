"""Travessia, abrigo e pavimentos; executar na janela Blender por MCP."""
import bpy, json
from pathlib import Path
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b05_comercio.blend')
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z'); I=R.inverted()
col=bpy.data.collections.new('ENVIRONMENT_FINAL | espaco publico Lacerda R30B06'); bpy.context.scene.collection.children.link(col)
report={'classification':{},'ground_faces':0,'references':['elevador-lacerda-front-2d9b4031ff6a','elevador-lacerda-front-97e36e6f289f']}
def material(name,color,rough=.75):
 m=bpy.data.materials.new('LAC R30B06 | '+name); m.use_nodes=True; m.diffuse_color=(*color,1)
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 return m
green=material('pintura verde travessia',(.30,.40,.12));white=material('pintura branca travessia',(.88,.87,.79));metal=material('metal abrigo',(.13,.16,.17),.4)
def mesh(name,vertices,faces,mat,location):
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update();me.materials.append(mat)
 o=bpy.data.objects.new('LAC R30B06 | '+name,me);col.objects.link(o);o['boas_location_id']=location;o['boas_role']='visual_environment';o['reference_status']='partial';return o
# Usa o contorno convexo da pintura existente, sem deslocar a travessia OSM.
cross=bpy.data.objects['VIAS | travessia OSM 3178050253'];vs=[cross.matrix_world@v.co for v in cross.data.vertices]
pts=sorted(set((round(v.x,5),round(v.y,5)) for v in vs))
def turn(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
lo=[];hi=[]
for p in pts:
 while len(lo)>1 and turn(lo[-2],lo[-1],p)<=0:lo.pop()
 lo.append(p)
for p in reversed(pts):
 while len(hi)>1 and turn(hi[-2],hi[-1],p)<=0:hi.pop()
 hi.append(p)
hull=lo[:-1]+hi[:-1];z=min(v.z for v in vs)-.003
paint=mesh('fundo verde travessia 3178050253',[(x,y,z) for x,y in hull],[tuple(range(len(hull)))],green,'elevador-lacerda')
paint['osm_node_id']='3178050253';paint['classification']='KEEP_REAL_REFERENCE';paint['source_media_id']=report['references'][0];paint['surface_separation_m']=.003
cross.data.materials.clear();cross.data.materials.append(white)
# Corrige somente a geometria do mobiliário; posição XY e terreno permanecem intactos.
terrain=bpy.data.objects['MVP | terreno corrigido | colisão estática']
def ground(x,y):
 p=R@Vector((x,y,100));inv=terrain.matrix_world.inverted();hit,loc,_,_=terrain.ray_cast(inv@p,inv.to_3x3()@Vector((0,0,-1)))
 if not hit:raise RuntimeError('Sem piso sob abrigo')
 return (terrain.matrix_world@loc).z
base=ground(-95.80,.2)
def zrange(o,bottom,top):
 old=[o.matrix_world@v.co for v in o.data.vertices];a=min(v.z for v in old);b=max(v.z for v in old);inv=o.matrix_world.inverted()
 for v,p in zip(o.data.vertices,old):p.z=bottom+(p.z-a)/(b-a)*(top-bottom);v.co=inv@p
 o['classification']='ERROR';o['revision_fix']='R30B06: alturas do abrigo recompostas sobre terreno existente';o['previous_world_z_range']=[a,b];o['ground_world_z']=base
 report['classification'][o.name]='ERROR: descontinuidade vertical do mobiliario'
for o in list(bpy.context.scene.objects):
 if o.name.startswith('CAIRU | abrigo pilar'):zrange(o,base,base+2.50)
 elif o.name=='CAIRU | abrigo cobertura OSM':zrange(o,base+2.50,base+2.65)
 elif o.name.startswith('CAIRU | banco do abrigo OSM apoio'):zrange(o,base,base+.44)
 elif o.name=='CAIRU | banco do abrigo OSM assento':zrange(o,base+.44,base+.50)
 elif o.name=='CAIRU | banco do abrigo OSM encosto':zrange(o,base+.52,base+1.05)
 else:continue
 if 'assento' not in o.name and 'encosto' not in o.name:o.data.materials.clear();o.data.materials.append(metal)
 mod=o.modifiers.new('Arestas mobiliario R30B06','BEVEL');mod.width=.018;mod.segments=2
# Acabamento dos passeios já identificados, sem modificar asfalto ou colisão.
mosaic=bpy.data.materials['ENTORNO LAC | pedra portuguesa calcada']
ids={i for i,m in enumerate(terrain.data.materials) if m and any(t in m.name.lower() for t in ['passeio','percurso pedonal','pedra portuguesa'])}
idx=next((i for i,m in enumerate(terrain.data.materials) if m==mosaic),None)
if idx is None:terrain.data.materials.append(mosaic);idx=len(terrain.data.materials)-1
for p in terrain.data.polygons:
 c=I@terrain.matrix_world@p.center
 if p.material_index in ids and -366<c.x<-76 and -85<c.y<89 and c.z<12:
  if p.material_index!=idx:report['ground_faces']+=1
  p.material_index=idx
# As juntas esquemáticas de 3 m pertencem ao piso anterior; a paginação agora está no material.
access=bpy.data.objects['MVP | praça ao acesso alto | caminho OSM 1429934820']
access.data.materials.clear();access.data.materials.append(bpy.data.materials['ENTORNO LAC | pedra irregular da praca'])
for o in bpy.context.scene.objects:
 if o.name.startswith('PRAÇA | junta de pavimento'):
  o.hide_render=True;o.hide_set(True);o['superseded_by']='ENTORNO LAC | pedra irregular da praca';o['classification']='ADAPT_LOCAL'
report['shelter_ground_z']=base;report['new_objects']=len(col.objects);report['geography_changed']=False
bpy.context.scene['lacerda_revision']='R30B.06 | travessia, abrigo e pavimentos'
dest=ROOT/'blender/salvador_lacerda_r30b06_espaco_publico.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
(ROOT/'artifacts/lacerda/r30b06_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
