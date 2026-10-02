"""Correções observadas na inspeção próxima da estação inferior."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
assert bpy.data.filepath.endswith('salvador_lacerda_r30b07_torre_entrada.blend')
# O bloco OSM tem altura explicitamente provisória e excedia a cobertura da estação.
# Corrigir apenas o trecho acima da verga, mantendo recortes de circulação e XY.
o=bpy.data.objects['OSM | 1263035777'];inv=o.matrix_world.inverted();old=[]
for v in o.data.vertices:
 p=o.matrix_world@v.co
 if p.z>11.85:
  old.append(p.z);p.z=11.85+(p.z-11.85)*.06;v.co=inv@p
o['classification']='ADAPT_LOCAL';o['height_source']='Altura visual ajustada à cobertura da estação inferior e referência fotográfica; não medida'
o['revision_note']='R30B07: removido excesso de altura provisória acima da estação; footprint e recortes preservados'
o['previous_top_z']=max(old)
# Placas laterais não devem ocupar a altura de passagem dos portais.
for o in bpy.data.objects:
 if not o.name.startswith('FACHADA INFERIOR | painel lateral'):continue
 inv=o.matrix_world.inverted();pts=[o.matrix_world@v.co for v in o.data.vertices];a=min(p.z for p in pts);b=max(p.z for p in pts)
 for v,p in zip(o.data.vertices,pts):p.z=10.69+(p.z-a)/(b-a)*.50;v.co=inv@p
 o['revision_note']='R30B07: painel elevado à bandeira para liberar passagem'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
p=ROOT/'artifacts/lacerda/r30b07_report.json';r=json.loads(p.read_text(encoding='utf8'));r['lower_station_proxy_height_corrected']='1263035777';r['lower_station_previous_top_z']=max(old);p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print('Altura provisória da estação corrigida; portais desobstruídos.')
