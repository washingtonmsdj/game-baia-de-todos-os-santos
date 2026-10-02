"""Exportação somente leitura das superfícies R30A.11, sem salvar o .blend."""
import bpy
import json
import sys
from pathlib import Path

root = Path(bpy.data.filepath).parent.parent
sys.path.insert(0, str(root))
from tools.runtime.production import load_contract, require_source, resolve
contract = load_contract()
require_source(contract['world_source'], bpy.data.filepath)
if bpy.context.scene.name != contract['world_source']['scene']:
    raise RuntimeError('Cena ativa não corresponde à composição registrada')
groups = {
    'terrain': [contract['export']['terrain_proxy']],
    'road': [contract['export']['road_object']],
}
manifest = json.loads(resolve(contract['export']['surface_manifest']).read_text(encoding='utf-8'))
for role in ('walkable', 'crossing', 'curb'):
    groups[role] = manifest['runtime_sources'][role]['objects']
if contract['export'].get('urban_slice_collection'):
    for obj in bpy.data.collections[contract['export']['urban_slice_collection']].objects:
        groups.setdefault(obj['boas_role'], []).append(obj.name)
depsgraph = bpy.context.evaluated_depsgraph_get()
meshes = []
for role, names in groups.items():
    for name in names:
        obj = bpy.context.scene.objects.get(name)
        if obj is None:
            raise RuntimeError(f'Superfície ausente: {name}')
        if role != 'terrain' and (obj.hide_render or not obj.visible_get()):
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            road_materials = set(contract['export']['road_materials'])
            road_slots = {i for i,m in enumerate(mesh.materials) if m and m.name in road_materials}
            is_source_road = role == 'road' and name == contract['export']['road_object']
            if is_source_road and len(road_slots) != len(road_materials):
                raise RuntimeError('Materiais de pista ausentes; revisar binding no contrato')
            triangles = [t for t in mesh.loop_triangles if not is_source_road or t.material_index in road_slots]
            used = sorted({v for t in triangles for v in t.vertices})
            remap = {v:i for i,v in enumerate(used)}
            positions = []
            for vertex_id in used:
                p = obj.matrix_world @ mesh.vertices[vertex_id].co
                positions.extend([round(p.x, 5), round(p.z, 5), round(p.y, 5)])
            indices = []
            for triangle in triangles:
                a, b, c = triangle.vertices
                indices.extend([remap[a], remap[c], remap[b]])
            meshes.append({'name': name, 'role': role, 'positions': positions, 'indices': indices})
        finally:
            evaluated.to_mesh_clear()
output = resolve(contract['staging']['surfaces'])
payload = {'source': 'blender/' + Path(bpy.data.filepath).name,
           'source_sha256': contract['world_source']['sha256'],
           'coordinates': 'x=Blender.X,y=Blender.Z,z=Blender.Y; meters',
           'terrain_status': 'accepted_candidate_R30A5', 'meshes': meshes}
output.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(json.dumps({'meshes': len(meshes), 'bytes': output.stat().st_size}))
