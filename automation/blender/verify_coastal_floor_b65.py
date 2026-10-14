"""Conferência B65 reaberta; sem alteração geométrica."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Euler
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];sc=bpy.context.scene;cat=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'));src=cat['validation_source'];assert src['revision'] in ('R30B.65','R30B.66'),('Fonte',src['revision']);assert Path(bpy.data.filepath).resolve()==(r/src['file']).resolve(),'Arquivo aberto diverge';assert hashlib.file_digest((r/src['file']).open('rb'),'sha256').hexdigest()==src['sha256'],'Hash da revisão diverge'
proof=json.loads((r/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'));assert proof['file']==src['file'] and proof['sha256']==src['sha256'] and proof['load_post_completed'],'Reabertura não confirmada'
wa=sc.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'];wa.data.calc_loop_triangles();wt=BVHTree.FromPolygons([wa.matrix_world@v.co for v in wa.data.vertices],[list(t.vertices) for t in wa.data.loop_triangles],all_triangles=True)
rows=[]
for ob in sc.objects:
 if ob.type!='MESH' or ob.hide_viewport or not(ob.name.startswith('B63 | VISUAL |') or ob.name=='CAIS | contenção costeira alinhada à linha de costa'):continue
 ob.data.calc_loop_triangles();bad=sum(t.area<1e-9 for t in ob.data.loop_triangles);bm=bmesh.new();bm.from_mesh(ob.data);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
 partner=sc.objects.get(ob.get('boas_collision_partner',''));equal=partner is not None and len(partner.data.vertices)==len(ob.data.vertices) and [tuple(f.vertices) for f in partner.data.polygons]==[tuple(f.vertices) for f in ob.data.polygons] and all((partner.matrix_world@b.co-ob.matrix_world@a.co).length<1e-6 for a,b in zip(ob.data.vertices,partner.data.vertices))
 wet=0;wrong_outward=0;unknown_outward=0
 if ob.name=='B63 | VISUAL | piso contínuo até o cais':
  for f in ob.data.polygons:
   p=ob.matrix_world@f.center;h=wt.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),300)[0]
   if h is not None and abs(h.z-.35)<.001:wet+=1
 if ob.name=='CAIS | contenção costeira alinhada à linha de costa':
  for f in ob.data.polygons:
   p=ob.matrix_world@f.center;n=ob.matrix_world.to_3x3().inverted().transposed()@f.normal;n.z=0;n.normalize();hits=[]
   for sign in (1,-1):
    q=p+n*sign*.15;h=wt.ray_cast(Vector((q.x,q.y,150)),Vector((0,0,-1)),300)[0];hits.append(h is not None and abs(h.z-.35)<.001)
   if hits==[False,True]:wrong_outward+=1
   elif hits[0]==hits[1]:unknown_outward+=1
 rows.append({'object':ob.name,'degenerate':bad,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'collision_equal':equal,'floor_faces_over_water':wet,'wrong_outward_faces':wrong_outward,'uncertain_outward_faces':unknown_outward})
report={'schema':'boas/coastal-floor-b65-validation-v1','source':src,'reopened':True,'geometry':rows,'all_generated_visible_meshes_checked':True,'local_geometry_checks_passed':all(x['degenerate']==0 and x['collision_equal'] and x['floor_faces_over_water']==0 and x['wrong_outward_faces']==0 and (x['nonmanifold_edges']==0 if 'canteiro' in x['object'] or 'meios-fios' in x['object'] else True) for x in rows),'real_fidelity_approved':False,'pending_bridge_osm_id':1426173327,'source_reference_review':'docs/reports/blender/waterfront_real_reference_review.json'}
(r/('docs/reports/blender/coastal_floor_r30b'+src['revision'].split('.')[-1]+'_validation.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for win in bpy.context.window_manager.windows:
 for ar in win.screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;sp.overlay.show_extras=False;sp.overlay.show_outline_selected=False;sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.region_3d.view_location=Vector((-165,175,16));sp.region_3d.view_distance=380;sp.region_3d.view_rotation=Euler((math.radians(48),0,math.radians(-38)),'XYZ').to_quaternion();sp.region_3d.view_perspective='ORTHO'
print(json.dumps(report,ensure_ascii=False))
