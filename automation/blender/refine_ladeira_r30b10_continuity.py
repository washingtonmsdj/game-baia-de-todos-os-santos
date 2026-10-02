"""Corrige manchas da contenção usando faixa contínua guiada pela borda da pista."""
import bpy, json
from pathlib import Path
from mathutils import Matrix

root=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith(('salvador_lacerda_r30b09_contecao_ladeira.blend','salvador_lacerda_r30b10_contencao_continua.blend'))
terrain=bpy.data.objects['MVP | terreno corrigido | colisão estática']
rotation=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z').inverted()
original=next(i for i,m in enumerate(terrain.data.materials) if m and m.name=='MVP | terreno contínuo')
stone=next(i for i,m in enumerate(terrain.data.materials) if m and m.name=='LAC R30B09 | pedra irregular da contenção')
for poly in terrain.data.polygons:
    if poly.material_index==stone:poly.material_index=original
rows=json.loads((root/'artifacts/lacerda/r30b10_ladeira_edge.json').read_text(encoding='utf8'))
edges=[(float(r['y']),float(r['edge_x'])) for r in rows]
def road_edge(y):
    if y<=edges[0][0]:return edges[0][1]
    if y>=edges[-1][0]:return edges[-1][1]
    for (y0,x0),(y1,x1) in zip(edges,edges[1:]):
        if y0<=y<=y1:return x0+(x1-x0)*(y-y0)/(y1-y0)
    raise RuntimeError('fora da borda')
changed=0
for poly in terrain.data.polygons:
    if poly.material_index!=original:continue
    p=rotation @ terrain.matrix_world @ poly.center
    if not (-40<=p.y<=50 and 19<=p.z<=72):continue
    if not (road_edge(p.y)+.25<=p.x<=-4.5):continue
    poly.material_index=stone;changed+=1
assert changed>555
material=terrain.data.materials[stone]
ramp=next(n for n in material.node_tree.nodes if n.type=='VALTORGB')
ramp.color_ramp.elements[0].position=.007
ramp.color_ramp.elements[0].color=(.17,.16,.14,1)
ramp.color_ramp.elements[1].position=.048
ramp.color_ramp.elements[1].color=(.36,.35,.31,1)
next(n for n in material.node_tree.nodes if n.type=='TEX_VORONOI').inputs['Scale'].default_value=2.3
bump=next(n for n in material.node_tree.nodes if n.type=='BUMP')
bump.inputs['Strength'].default_value=.18
bump.inputs['Distance'].default_value=.025
terrain['r30b10_retaining_faces']=changed
terrain['r30b10_note']='Faixa continua delimitada pela borda externa do passeio da Ladeira, sem mudar topologia ou materiais viarios.'
bpy.context.scene['lacerda_revision']='R30B.10 | continuidade da contenção Ladeira da Montanha'
dest=root/'blender/salvador_lacerda_r30b10_contencao_continua.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'revision':dest.name,'faces_stone':changed,'road_faces_changed':0,'terrain_vertices_changed':0,'classification':'ADAPT_LOCAL','status':'partial; faixa visual continua, topologia da contenção por revisar','source_edge':'artifacts/lacerda/r30b10_ladeira_edge.json'}
(root/'artifacts/lacerda/r30b10_continuity_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'saved':dest.name,'faces':changed},ensure_ascii=False))
