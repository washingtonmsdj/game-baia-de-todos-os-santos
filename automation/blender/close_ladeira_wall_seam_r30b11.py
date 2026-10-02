"""Fecha a faixa sem pedra entre passeio e contenção, sem alterar pista ou topologia."""
import bpy,json
from pathlib import Path
from mathutils import Matrix

root=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b10_contencao_continua.blend')
terrain=bpy.data.objects['MVP | terreno corrigido | colisão estática']
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z').inverted()
original=next(i for i,m in enumerate(terrain.data.materials) if m and m.name=='MVP | terreno contínuo')
stone=next(i for i,m in enumerate(terrain.data.materials) if m and m.name=='LAC R30B09 | pedra irregular da contenção')
rows=json.loads((root/'artifacts/lacerda/r30b10_ladeira_edge.json').read_text(encoding='utf8'))
edges=[(float(r['y']),float(r['edge_x'])) for r in rows]
def edge(y):
    if y<=edges[0][0]:return edges[0][1]
    if y>=edges[-1][0]:return edges[-1][1]
    for (a,x),(b,z) in zip(edges,edges[1:]):
        if a<=y<=b:return x+(z-x)*(y-a)/(b-a)
    raise RuntimeError('borda fora da faixa')
count=0
for poly in terrain.data.polygons:
    if poly.material_index!=original:continue
    p=rot @ terrain.matrix_world @ poly.center
    if -70<=p.y<=85 and 16<=p.z<=72 and edge(p.y)-3<=p.x<=-4.5:
        poly.material_index=stone
        count+=1
assert count>200
terrain['r30b11_seam_faces']=count
terrain['r30b11_seam_note']='Revestimento de pedra ate o passeio existente; sem alteracao na malha, pista ou colisao.'
bpy.context.scene['lacerda_revision']='R30B.11 | encontro continuo da contenção com o passeio'
dest=root/'blender/salvador_lacerda_r30b11_encontro_contecao_passeio.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'revision':dest.name,'added_stone_faces':count,'road_faces_changed':0,'mesh_vertices_changed':0,'source_edge':'artifacts/lacerda/r30b10_ladeira_edge.json','classification':'ADAPT_LOCAL','reference':'aleph-streetview-vlswmjen; aleph-streetview-1d0zz3_6','note':'Muro da referência encontra passeio estreito; antiga faixa verde era material não revestido, sem abertura geométrica.'}
(root/'artifacts/lacerda/r30b11_wall_seam_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'saved':dest.name,'added_stone_faces':count},ensure_ascii=False))
