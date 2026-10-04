"""Encontro externo estreito das portas; coluna B estrutural recuada sob as folhas.

Correção solicitada após comparação com a lateral Hilux catalogada. V17 preservada.
As folhas cobrem a coluna, sem fechar os vãos da própria carroceria com decoração.
"""
import ast,bpy,bmesh,collections,hashlib,json,math,struct
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import delaunay_2d_cdt
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_portas_v18.blend'
assert s.get('boas_v18_doors_applied') and not s.get('boas_v18_center_seam')
before=json.loads((r/'artifacts/vehicles/rondesp/v18-doors-before.json').read_text(encoding='utf8'))
rp=r/'docs/reports/blender/hilux_portas_v18.json';report=json.loads(rp.read_text(encoding='utf8'))
body=s.objects['HILUX | CARROCERIA PRINCIPAL'];root=s.objects['RDP01_ROOT | viatura']
paint=bpy.data.materials['RDP01 | Pintura marrom Rondesp'];black=bpy.data.materials['RDP01 | Polímero preto']
gray=(.53,.55,.58,1);changed=[];added=[]
files=[('rebuild_hilux_reference_v06.py',{'interp','sidewidth'}),
 ('rebuild_hilux_cab_v15.py',{'smooth','roof_width','roof_edge_z','cab_side','radius','rear_y','cab_x','rounded'}),
 ('finish_hilux_cab_v15.py',{'regular_x'}),
 ('model_hilux_doors_v18.py',{'fingerprint','field','area','inside','inset','dense','border','move_to','mesh_object','skin','strip'})]
for file,names in files:
 for fn in ast.parse((r/'automation/blender'/file).read_text(encoding='utf8')).body:
  if isinstance(fn,ast.FunctionDef) and fn.name in names:
   exec(compile(ast.Module(body=[fn],type_ignores=[]),file,'exec'),globals())
original_border=border
def seam(z):return .174+.012*max(0,min(1,(z-.516)/1.234))
def border(label):
 loop,old=original_border(label);adjusted=[]
 for p in loop:
  y,z=p
  if label=='dianteiro':
   end=.100+.011*max(0,min(1,(z-.516)/1.234))
   weight=smooth((y+.24)/.17);y+=(seam(z)+.0015-end)*weight
  else:
   end=.244-.004*max(0,min(1,(z-.516)/1.234))
   weight=1-smooth((y-.36)/.20);y+=(seam(z)-.0015-end)*weight
  adjusted.append(Vector((y,z)))
 return adjusted,old
def window_adjust(label,points):
 result=[]
 for y,z in points:
  if label=='dianteira':y+=(seam(z)-.033-.070)*smooth((y+.12)/.15)
  else:y+=(seam(z)+.033-.283)*(1-smooth((y-.36)/.20))
  result.append((y,z))
 return result
src=(r/'automation/blender/model_hilux_doors_v18.py').read_text(encoding='utf8')
fn=next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name=='door_shape')
code=ast.get_source_segment(src,fn).replace('    window = rounded(win_points,rad=.014,n=8)',
 '    win_points=window_adjust(label,win_points)\n    window = rounded(win_points,rad=.014,n=8)')
code=code.replace("hy = -.065 if label=='dianteira' else .866","hy = -.005 if label=='dianteira' else .866")
exec(compile(code,'door-outline-v18-center-seam','exec'),globals())
assert fingerprint(body)==before['body_hash']
changed_verts=0
for v in body.data.vertices:
 y,z=v.co.y,v.co.z
 wy=smooth((y-.075)/.030)*(1-smooth((y-.254)/.032))
 wz=smooth((z-.489)/.030)*(1-smooth((z-1.756)/.040))
 depth=.078*(1-smooth((z-1.245)/.105))+.042*smooth((z-1.245)/.105)
 if wy*wz>1e-8 and v.co.x>.64:
  v.co.x-=depth*wy*wz;changed_verts+=1
body.data.update()
body['boas_v18_b_pillar']='Coluna B estrutural recuada sob as folhas; junta externa candidata de 4 mm entre portas.'
for label in ['dianteira','traseira']:
 vs,fs,outline,window,outside,inner,hy=door_shape(label)
 for side in [-1,1]:
  hand='esquerda' if side==-1 else 'direita'
  ob=s.objects[f'RDP01 | HILUX06 | Porta {label} {side}'];pivot=ob.parent;col=ob.users_collection[0]
  assert abs(pivot['abertura_graus'])<1e-9
  mesh_object(ob.name,vs,fs,col,pivot,side,existing=ob)
  ob['boas_v18_center_gap_candidate_m']=.004
  for name,points,channel_radius,closed in [
   (f'HILUX18 | Canal vidro {label} {hand}',[outside(p)+Vector((-.006,0,0)) for p in window],.003,True),
   (f'HILUX18 | Vedacao interna {label} {hand}',[inner(p)+Vector((-.0015,0,0)) for p in outline],.003,True)]:
   seal=s.objects[name];data=bpy.data.curves.new(name+' | encontro V18','CURVE');data.dimensions='3D'
   data.bevel_depth=channel_radius;data.bevel_resolution=3;data.materials.append(black)
   spl=data.splines.new('POLY');spl.points.add(len(points)-1)
   for q,p in zip(spl.points,points):q.co=(*(Vector((side*p.x,p.y,p.z))-pivot.location),1)
   spl.use_cyclic_u=closed;seal.data=data
  if label=='dianteira':
   for word in ['Maçaneta','Bolso maçaneta']:
    handle=s.objects[f'RDP01 | HILUX06 | {word} {label}{side}']
    handle.data.transform(Matrix.Translation(Vector((0,.060,0))))
s['boas_v18_center_seam']=True
bpy.context.view_layer.update()
report['body_unchanged']=False;report['body_change_scope']='Recuo localizado da coluna B e seus encontros, autorizado para permitir o fechamento real das folhas.'
report['body_hash_after']=fingerprint(body)
report['center_joint']={'external_gap_candidate_m':.004,'modified_body_vertices':changed_verts,
 'b_pillar_candidate_recess_lower_m':.078,'b_pillar_candidate_recess_upper_m':.042,
 'reference_id':'hilux-2024-std-dealer-side','status':'candidate'}
report['notes']=[n for n in report['notes'] if not n.startswith('Carroceria fixa preservada')]
report['notes'].append('Coluna B recuada sob as folhas. Portas cobrem a estrutura e se encontram externamente numa junta estreita; V17 permanece preservada.')
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'center_gap_candidate_m':.004,'b_pillar_vertices':changed_verts}))
