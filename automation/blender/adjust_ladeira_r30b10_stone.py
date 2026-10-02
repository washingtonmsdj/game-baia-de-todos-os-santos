"""Ajusta escala e contraste da pedra de contenção após inspeção visual."""
import bpy
assert bpy.data.filepath.endswith('salvador_lacerda_r30b10_contencao_continua.blend')
material=bpy.data.materials['LAC R30B09 | pedra irregular da contenção']
voronoi=next(n for n in material.node_tree.nodes if n.type=='TEX_VORONOI')
voronoi.inputs['Scale'].default_value=2.3
ramp=next(n for n in material.node_tree.nodes if n.type=='VALTORGB')
ramp.color_ramp.elements[0].position=.007
ramp.color_ramp.elements[0].color=(.17,.16,.14,1)
ramp.color_ramp.elements[1].position=.048
ramp.color_ramp.elements[1].color=(.36,.35,.31,1)
bump=next(n for n in material.node_tree.nodes if n.type=='BUMP')
bump.inputs['Strength'].default_value=.18
bump.inputs['Distance'].default_value=.025
bpy.ops.wm.save_mainfile()
print('Material da pedra suavizado e salvo')
