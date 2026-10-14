"""Envoltória externa ampla da14, distinta do núcleo interno da17."""
import bpy,bmesh,json,runpy
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102'
cfg=json.loads((out/'controls.json').read_text());reg=json.loads((root/'docs/reports/blender/lacerda-structure-b99/controls.json').read_text())['registration']['14']['matrix_to_sheet17']
frame=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());anchor=frame['drawing_to_architecture']['origin_pdf'];scale=frame['pdf_units_per_m']
name='B102 | cidade alta | envoltória externa central';assert name not in bpy.data.objects
# Faces principais da14/526 (oeste/norte) e14/518 (leste/sul).
# O contorno abaixo é massing sem os pequenos recuos/porta; não as-built.
pdf=[[2077.68,926.08],[2283.48,926.08],[2283.48,1284.88],[2077.68,1284.88]]
outer=[]
for p in pdf:
 x=reg[0][0]*p[0]+reg[0][1]*p[1]+reg[0][2];y=reg[1][0]*p[0]+reg[1][1]*p[1]+reg[1][2]
 outer.append(Vector((5.5+(x-anchor[0])/scale,-(y-anchor[1])/scale)))
area=lambda p:sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
if area(outer)<0:outer.reverse()
inner=[]
for i,b in enumerate(outer):
 u=(b-outer[i-1]).normalized();v=(outer[(i+1)%4]-b).normalized();nu=Vector((-u.y,u.x));nv=Vector((-v.y,v.x));d=(nv-nu)*.25;cross=u.x*v.y-u.y*v.x
 inner.append(b+nu*.25+u*((d.x*v.y-d.y*v.x)/cross))
z=frame['levels']['upper_walkable'];lo=z-53.17;hi=z-19.85;vertices=[(p.x,p.y,h) for h in (lo,hi) for loop in (outer,inner) for p in loop];faces=[]
for i in range(4):
 j=(i+1)%4;faces.extend([(i,j,j+8,i+8),(i+4,i+12,j+12,j+4),(i,i+4,j+4,j),(i+8,j+8,j+12,i+12)])
mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.materials.append(bpy.data.objects['CASCA | parede lateral'].data.materials[0])
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh)
q={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'inconsistent_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'volume':bm.calc_volume(signed=True)};bm.free();assert q['nonmanifold_edges']==q['degenerate_faces']==q['inconsistent_edges']==0 and q['volume']>0
o=bpy.data.objects.new(name,mesh);bpy.data.collections['HERO | Lacerda | corpo exterior B102'].objects.link(o)
o.matrix_world=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
for k,v in {'boas_location_id':'elevador-lacerda','boas_role':'ARCHITECTURAL_MODEL_CANDIDATE','boas_generated_revision':'R30B.102',
 'boas_provenance_ids':json.dumps(['derived:lacerda-exterior-four-lifts-b102']),'accuracy':'DOCUMENT_MAJOR_XY_APPROXIMATE_LOWER_EXTRUSION',
 'replacement_required':True,'boas_production_ready':False,'boas_vertical_gate':'BLOCKED_EXTERNAL_EVIDENCE','boas_source_control':'docs/reports/blender/lacerda-exterior-b102/controls.json'}.items():o[k]=v
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature'];r=json.loads((out/'application.json').read_text())
r['added'].append({'object':name,'after':{'signature':sig(o)},'mesh':q,'role':'ARCHITECTURAL_MODEL_CANDIDATE','source':'SUCOP14 envoltória principal, SUCOP23 intervalo; não núcleo interno17'})
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cfg['outer_central_body']={'object':name,'drawing_points_pdf14':pdf,'outline_local':[list(p) for p in outer],
 'levels':[lo,hi],'thickness_candidate':.25,'source_faces':['14/526','14/518'],
 'classification':'ADAPT_LOCAL_DOCUMENT_MAJOR_ENVELOPE','not_proven':'Simplificação de pequenos recuos e extrusão abaixo da14; confrontar futuramente levantamento/elevações',
 'inner_core_separate_and_preserved':True}
(out/'controls.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'added':name,'outer_width_m':max(p.y for p in outer)-min(p.y for p in outer),'core_unmodified':True},ensure_ascii=False))
