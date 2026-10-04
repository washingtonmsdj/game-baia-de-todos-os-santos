"""Corrige transição da coluna B/teto e arredonda o capô na sessão MCP visível."""
import bpy, bmesh, json, math
from pathlib import Path
r=Path(__file__).resolve().parents[2]
s=bpy.context.scene
assert not bpy.app.background
assert Path(bpy.data.filepath).name=='hilux_portas_v18.blend'
target=r/'blender/assets/vehicles/rondesp-pickup/hilux_superficies_v19.blend'
assert not target.exists(), 'Preservar revisão existente'
o=s.objects['HILUX | CARROCERIA PRINCIPAL']
old=json.loads((r/'artifacts/vehicles/rondesp/v17-mesh-after.json').read_text(encoding='utf8'))['geometry']
assert len(old['vertices'])==len(o.data.vertices)
checkpoint=r/'artifacts/vehicles/rondesp/v19-live-before.blend'
if not checkpoint.exists():bpy.data.libraries.write(str(checkpoint),{s},fake_user=True,compress=True)
for window in bpy.context.window_manager.windows:
 if window.screen.is_animation_playing:
  with bpy.context.temp_override(window=window):bpy.ops.screen.animation_cancel(restore_frame=False)
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
restored=0
for v,co in zip(o.data.vertices,old['vertices']):
 if v.co.z>1.675 and abs(v.co.x-co[0])>1e-7:
  a=smooth((v.co.z-1.675)/.058)
  v.co.x+=(co[0]-v.co.x)*a;restored+=1
attr=o.data.attributes['boas_panel_id']
hood={i for p in o.data.polygons if attr.data[p.index].value==1 for i in p.vertices}
for i in hood:
 v=o.data.vertices[i];x,y,z=v.co
 # Inverte o parâmetro longitudinal do capô de origem, preservando as juntas.
 u=max(0.,min(1.,(y+2.435)/1.46))
 for _ in range(16):
  w=.9275-.093*u**3-.032*math.sin(math.pi*u)
  f=min(1.,abs(x)/w)
  yf=-2.435+.49*f**3.5
  u=max(0.,min(1.,(y-yf)/(-.975-yf)))
 w=.9275-.093*u**3-.032*math.sin(math.pi*u)
 f=min(1.,abs(x)/w)
 # Coroamento adicional contínuo; zero nas quatro bordas compartilhadas.
 v.co.z+=.024*math.sin(math.pi*u)**2*(1-f*f)**2
bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update()
layer=bm.faces.layers.int['boas_panel_id']
edges=[e for e in bm.edges if len(e.link_faces)==2 and 1 in {f[layer] for f in e.link_faces} and len({f[layer] for f in e.link_faces})>1 and e.calc_face_angle(0)>.22 and min(v.co.x for v in e.verts)>.015]
count=len(edges)
if edges:
 bmesh.ops.bevel(bm,geom=edges,offset=.008,segments=4,affect='EDGES',clamp_overlap=True,profile=.5)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for e in bm.edges:
 if len(e.link_faces)==2 and all(f[layer]==1 for f in e.link_faces):e.smooth=True
for f in bm.faces:f.smooth=True
bm.to_mesh(o.data);bm.free();o.data.update()
o['boas_surface_revision']='v19: cabeceira externa restaurada; recuo B termina abaixo da cabeceira; capô coroado e bordas locais arredondadas'
s.name='HILUX | superficies e portas v19'
report={'asset_id':'vehicle-rondesp-pickup','file':target.relative_to(r).as_posix(),'scene':s.name,'parent':'blender/assets/vehicles/rondesp-pickup/hilux_portas_v18.blend','parent_sha256':'0facd4dd74797aec7f2051d8b445019fb9ea310ee762e71677390647b0e8e260','status':'candidate','roof_vertices_corrected':restored,'hood_vertices':len(hood),'hood_boundary_edges_rounded':count,'hood_bevel_m':.008,'hood_additional_crown_m':.024,'notes':['Coluna B permanece recuada abaixo da cabeceira.','Portas, pivôs e demais peças preservados.','Dimensões de acabamento são parâmetros artísticos, não medidas de fábrica.'],'runtime_exported':False,'source_reopened':False}
(r/'docs/reports/blender/hilux_superficies_v19.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
print(json.dumps(report,ensure_ascii=False))
