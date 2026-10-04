"""Caixilho dianteiro contido na folha e dobra periférica com estrutura interna recuada."""
import ast,bpy,bmesh,collections,hashlib,json,math,struct
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import delaunay_2d_cdt
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_portas_v18.blend'
assert s.get('boas_v18_center_seam') and not s.get('boas_v18_door_returns_finished')
before=json.loads((r/'artifacts/vehicles/rondesp/v18-doors-before.json').read_text(encoding='utf8'))
rp=r/'docs/reports/blender/hilux_portas_v18.json';report=json.loads(rp.read_text(encoding='utf8'))
body=s.objects['HILUX | CARROCERIA PRINCIPAL'];root=s.objects['RDP01_ROOT | viatura']
paint=bpy.data.materials['RDP01 | Pintura marrom Rondesp'];black=bpy.data.materials['RDP01 | Polímero preto']
gray=(.53,.55,.58,1);changed=[];added=[]
for file,names in [
 ('rebuild_hilux_reference_v06.py',{'interp','sidewidth'}),
 ('rebuild_hilux_cab_v15.py',{'smooth','roof_width','roof_edge_z','cab_side','radius','rear_y','cab_x','rounded'}),
 ('finish_hilux_cab_v15.py',{'regular_x'}),
 ('model_hilux_doors_v18.py',{'fingerprint','field','area','inside','inset','dense','border','move_to','mesh_object','skin','strip'})]:
 for fn in ast.parse((r/'automation/blender'/file).read_text(encoding='utf8')).body:
  if isinstance(fn,ast.FunctionDef) and fn.name in names:
   exec(compile(ast.Module(body=[fn],type_ignores=[]),file,'exec'),globals())
original_border=border
for fn in ast.parse((r/'automation/blender/join_hilux_door_seams_v18.py').read_text(encoding='utf8')).body:
 if isinstance(fn,ast.FunctionDef) and fn.name in {'seam','border','window_adjust'}:
  exec(compile(ast.Module(body=[fn],type_ignores=[]),'encontro-portas-v18','exec'),globals())
src=(r/'automation/blender/model_hilux_doors_v18.py').read_text(encoding='utf8')
fn=next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name=='door_shape')
code=ast.get_source_segment(src,fn)
code=code.replace("[(-.869,1.324),(-.741,1.451),(-.386,1.694),(-.237,1.713),(.071,1.714),(.069,1.324)]",
 "[(-.836,1.328),(-.680,1.445),(-.314,1.690),(-.217,1.713),(.071,1.714),(.069,1.328)]")
code=code.replace('    window = rounded(win_points,rad=.014,n=8)',
 '    win_points=window_adjust(label,win_points)\n    window = rounded(win_points,rad=.014,n=8)')
code=code.replace("hy = -.065 if label=='dianteira' else .866","hy = -.005 if label=='dianteira' else .866")
code=code.replace('    skin(vs,fs,outline,[window,service],inner,True)',
 '    internal_outline=inset(outline,.010)\n    skin(vs,fs,internal_outline,[window,service],inner,True)')
code=code.replace('    for loop in [outline,window]:\n        strip(vs,fs,[[outside(p).lerp(inner(p),j/4) for j in range(5)] for p in loop+[loop[0]]])',
 '    for loop,internal in [(outline,internal_outline),(window,window)]:\n        strip(vs,fs,[[outside(p),outside(p)+Vector((-.0015,0,0)),outside(p).lerp(inner(q),.50),inner(q)] for p,q in zip(loop+[loop[0]],internal+[internal[0]])])')
code=code.replace('return vs,fs,outline,window,outside,inner,hy','return vs,fs,outline,window,outside,inner,hy,internal_outline')
exec(compile(code,'dobras-candidatas-v18','exec'),globals())
assert fingerprint(body)==report['body_hash_after']
for label in ['dianteira','traseira']:
 vs,fs,outline,window,outside,inner,hy,internal_outline=door_shape(label)
 for side in [-1,1]:
  hand='esquerda' if side==-1 else 'direita'
  ob=s.objects[f'RDP01 | HILUX06 | Porta {label} {side}'];pivot=ob.parent;col=ob.users_collection[0]
  assert abs(pivot['abertura_graus'])<1e-9
  mesh_object(ob.name,vs,fs,col,pivot,side,existing=ob)
  for name,points in [
   (f'HILUX18 | Canal vidro {label} {hand}',[outside(p)+Vector((-.006,0,0)) for p in window]),
   (f'HILUX18 | Vedacao interna {label} {hand}',[inner(p)+Vector((-.0015,0,0)) for p in internal_outline])]:
   seal=s.objects[name];data=bpy.data.curves.new(name+' | dobras V18','CURVE');data.dimensions='3D'
   data.bevel_depth=.003;data.bevel_resolution=3;data.materials.append(black)
   spl=data.splines.new('POLY');spl.points.add(len(points)-1)
   for q,p in zip(spl.points,points):q.co=(*(Vector((side*p.x,p.y,p.z))-pivot.location),1)
   spl.use_cyclic_u=True;seal.data=data
  ob['boas_v18_internal_edge_inset_candidate_m']=.010
s['boas_v18_door_returns_finished']=True
bpy.context.view_layer.update()
report['door_return_finish']={'internal_edge_inset_candidate_m':.010,'hem_candidate_m':.0015,
 'front_window_contained_in_door':True,'status':'candidate; conferir abertura'}
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
