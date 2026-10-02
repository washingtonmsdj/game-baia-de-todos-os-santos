"""Reabre a revisão salva na mesma janela para conferir persistência."""
import bpy
assert bpy.data.filepath.endswith('salvador_lacerda_r30b09_contecao_ladeira.blend')
assert not bpy.data.is_dirty
bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
