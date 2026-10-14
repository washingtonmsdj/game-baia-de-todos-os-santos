"""Cobertura costeira OSM/Aleph: IDs explícitos e piso existente, sem editar cena."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import Counter
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
src=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
assert Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
ref=json.loads((r/'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json').read_text(encoding='utf8'))
names=['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B63 | VISUAL | piso contínuo até o cais'];trees=[]
for name in names:
 o=s.objects[name];o.data.calc_loop_triangles()
 trees.append((o,BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True),[t.polygon_index for t in o.data.loop_triangles]))
def sample(x,y):
 hits=[]
 for o,tree,indices in trees:
  p,n,i,d=tree.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),300)
  if p is not None:
   face=o.data.polygons[indices[i]];attr=o.data.attributes.get('boas_surface_role')
   role=attr.data[face.index].value if attr else None
   if o.name.startswith('MVP | terreno'):role=1 if face.material_index in (2,5) else (2 if face.material_index in (1,3,4,7) else 0)
   hits.append({'z':p.z,'object':o.name,'role':role,'material':face.material_index})
 return max(hits,key=lambda h:h['z']) if hits else None
roads=[];coast=[]
for f in ref['features']:
 pts=f['blender_xy'];tags=f['tags']
 if not pts:continue
 bb=[min(p[0] for p in pts),max(p[0] for p in pts),min(p[1] for p in pts),max(p[1] for p in pts)]
 if bb[1]<-560 or bb[0]>60 or bb[3]<-110 or bb[2]>620:continue
 if tags.get('natural')=='coastline':coast.append({'osm_id':f['osm_id'],'bounds':bb,'source_nodes':len(pts)});continue
 hw=tags.get('highway')
 if hw not in ('primary','secondary','tertiary','residential','unclassified','service','living_street','primary_link','secondary_link','tertiary_link'):continue
 counts=Counter();examples=[];levels=[]
 for a,b in zip(pts,pts[1:]):
  L=math.dist(a,b);ns=max(1,math.ceil(L/10))
  for j in range(ns):
   x=a[0]+(b[0]-a[0])*(j+.5)/ns;y=a[1]+(b[1]-a[1])*(j+.5)/ns
   if not(-560<=x<=60 and -110<=y<=620):continue
   hit=sample(x,y);status='no_ground' if hit is None else ('road_material_present' if hit['role']==1 else 'ground_without_road_material')
   counts[status]+=1
   if hit:levels.append(hit['z'])
   if status!='road_material_present' and len(examples)<5:examples.append({'xy':[x,y],'status':status,'support':hit})
 if counts:roads.append({'osm_id':f['osm_id'],'name':tags.get('name'),'highway':hw,'source_width_m':f.get('metrics',{}).get('width_m_tagged'),'bounds':bb,'samples':dict(counts),'examples':examples,'classification':'NEEDS_REVIEW','approved':False})
aleph=json.loads((r/'world/areas/mvp-centro-lacerda/aleph-quality-source.json').read_text(encoding='utf8'));verified=[]
for item in aleph['files'][:2]:
 p=Path(item['path']);exists=p.exists()
 verified.append({'kind':p.name,'expected_sha256':item['sha256'],'available':exists,'hash_matches':hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'] if exists else False})
out={'schema':'boas/coastal-region-source-coverage-v1','source':src,'xy_fit_quality':ref['fit_quality'],'source_capture':'aleph-20260924T205631Z-aqqo7pkx','aleph_inputs':verified,'coastline_source_features':coast,'roads':roads,'totals':dict(sum((Counter(x['samples']) for x in roads),Counter())),'terrain_scope':'x -560..60; y -110..620, Blender XY','limitations':['Sondagem do eixo a cada <=10m; não prova largura, faixa, quatro rodas ou tráfego','Material legado pode estar incorreto; falta material não equivale a ausência de via real','Costa atual e altimetria absoluta ainda não aprovadas','Não suavizar escarpa nem mover eixos apenas para melhorar métricas'],'geometry_changed':False,'approved':False}
(r/'docs/reports/blender/coastal_region_source_coverage_b69.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'totals':out['totals'],'roads':len(roads),'aleph_inputs':verified}))
