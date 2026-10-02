"""Empacota a cena exportada em setores, sem modificar geometria ou arquivos Blender.

Publica runtime.json por último. Um pacote anterior continua utilizável se houver erro.
Usa somente stdlib; não executa npm, build web ou Blender em background.
"""
import copy
import hashlib
import json
import math
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.runtime.production import ROOT, CONTRACT, load_contract, require_source, resolve, sha256


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def atomic(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def read_glb(path):
    data = path.read_bytes()
    magic, version, size = struct.unpack_from('<III', data)
    if magic != 0x46546C67 or version != 2 or size != len(data):
        raise ValueError(f'GLB inválido: {path}')
    length, kind = struct.unpack_from('<II', data, 12)
    if kind != 0x4E4F534A:
        raise ValueError('JSON GLB ausente')
    doc = json.loads(data[20:20 + length])
    offset = 20 + length
    binary_length, binary_kind = struct.unpack_from('<II', data, offset)
    if binary_kind != 0x004E4942:
        raise ValueError('BIN GLB ausente')
    if doc.get('skins') or doc.get('animations'):
        raise ValueError('Setorização estática não pode descartar rig/animação')
    if any('uri' in image for image in doc.get('images', [])):
        raise ValueError('Texturas externas precisam ser incorporadas antes do pacote')
    return doc, data[offset + 8:offset + 8 + binary_length]


def multiply(a, b):
    return [[sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]


IDENTITY = [[float(r == c) for c in range(4)] for r in range(4)]


def node_matrix(node):
    if 'matrix' in node:
        return [[node['matrix'][c * 4 + r] for c in range(4)] for r in range(4)]
    x, y, z, w = node.get('rotation', [0, 0, 0, 1])
    scale = node.get('scale', [1, 1, 1])
    rotation = [[1-2*y*y-2*z*z, 2*x*y-2*z*w, 2*x*z+2*y*w],
                [2*x*y+2*z*w, 1-2*x*x-2*z*z, 2*y*z-2*x*w],
                [2*x*z-2*y*w, 2*y*z+2*x*w, 1-2*x*x-2*y*y]]
    translation = node.get('translation', [0, 0, 0])
    return [[rotation[r][c] * scale[c] for c in range(3)] + [translation[r]] for r in range(3)] + [[0, 0, 0, 1]]


def scene_bounds(doc):
    result, parents = {}, {}
    def visit(index, parent):
        node = doc['nodes'][index]
        if node.get('extensions'):
            raise ValueError('Extensão de nó requer suporte explícito no empacotador')
        matrix = multiply(parent, node_matrix(node))
        if 'mesh' in node:
            points = []
            for primitive in doc['meshes'][node['mesh']]['primitives']:
                acc = doc['accessors'][primitive['attributes']['POSITION']]
                for x in (acc['min'][0], acc['max'][0]):
                    for y in (acc['min'][1], acc['max'][1]):
                        for z in (acc['min'][2], acc['max'][2]):
                            points.append([sum(matrix[r][k] * [x,y,z,1][k] for k in range(4)) for r in range(3)])
            result[index] = [[min(p[d] for p in points) for d in range(3)], [max(p[d] for p in points) for d in range(3)]]
        for child in node.get('children', []):
            parents[child] = index
            visit(child, matrix)
    for index in doc['scenes'][doc.get('scene', 0)]['nodes']:
        visit(index, IDENTITY)
    return result, parents


def union(bounds):
    return [[min(b[0][d] for b in bounds) for d in range(3)], [max(b[1][d] for b in bounds) for d in range(3)]]


def subset(doc, binary, selected, parents):
    """Preserva transforms/hierarquia; copia só buffers referidos pelo subset."""
    selected = set(selected)
    kept = set(selected)
    for index in selected:
        while index in parents:
            index = parents[index]
            kept.add(index)
    node_ids = sorted(kept)
    node_map = {old:new for new,old in enumerate(node_ids)}
    mesh_ids = sorted({doc['nodes'][i]['mesh'] for i in selected})
    mesh_map = {old:new for new,old in enumerate(mesh_ids)}
    out = {key:copy.deepcopy(doc[key]) for key in ('asset','extensionsUsed','extensionsRequired','materials','textures','images','samplers') if key in doc}
    out['nodes'] = []
    for index in node_ids:
        node = copy.deepcopy(doc['nodes'][index])
        if 'mesh' in node:
            if index in selected:
                node['mesh'] = mesh_map[node['mesh']]
            else:
                del node['mesh']
        node.pop('camera', None)
        if 'children' in node:
            node['children'] = [node_map[i] for i in node['children'] if i in kept]
        out['nodes'].append(node)
    out['scenes'] = [{'nodes':[node_map[i] for i in node_ids if parents.get(i) not in kept]}]
    out['scene'] = 0
    out['meshes'] = [copy.deepcopy(doc['meshes'][i]) for i in mesh_ids]
    accessors = set()
    for mesh in out['meshes']:
        for primitive in mesh['primitives']:
            if primitive.get('extensions'):
                raise ValueError('Primitiva comprimida não suportada para repartição')
            accessors.update(primitive['attributes'].values())
            if 'indices' in primitive:
                accessors.add(primitive['indices'])
            for target in primitive.get('targets', []):
                accessors.update(target.values())
    accessor_ids = sorted(accessors)
    accessor_map = {old:new for new,old in enumerate(accessor_ids)}
    out['accessors'] = [copy.deepcopy(doc['accessors'][i]) for i in accessor_ids]
    for mesh in out['meshes']:
        for primitive in mesh['primitives']:
            primitive['attributes'] = {k:accessor_map[v] for k,v in primitive['attributes'].items()}
            if 'indices' in primitive:
                primitive['indices'] = accessor_map[primitive['indices']]
            primitive['targets'] = [{k:accessor_map[v] for k,v in target.items()} for target in primitive.get('targets', [])]
            if not primitive['targets']:
                del primitive['targets']
    views = set()
    for acc in out['accessors']:
        if 'sparse' in acc:
            raise ValueError('Accessor sparse requer suporte explícito')
        if 'bufferView' in acc:
            views.add(acc['bufferView'])
    views.update(image['bufferView'] for image in out.get('images', []) if 'bufferView' in image)
    view_map = {old:new for new,old in enumerate(sorted(views))}
    packed = bytearray()
    out['bufferViews'] = []
    for index in sorted(views):
        view = copy.deepcopy(doc['bufferViews'][index])
        if view.get('buffer', 0) != 0:
            raise ValueError('Mais de um buffer GLB')
        packed.extend(b'\0' * (-len(packed) % 4))
        start = view.get('byteOffset', 0)
        view['byteOffset'] = len(packed)
        packed.extend(binary[start:start + view['byteLength']])
        out['bufferViews'].append(view)
    for acc in out['accessors']:
        if 'bufferView' in acc:
            acc['bufferView'] = view_map[acc['bufferView']]
    for image in out.get('images', []):
        if 'bufferView' in image:
            image['bufferView'] = view_map[image['bufferView']]
    out['buffers'] = [{'byteLength':len(packed)}]
    raw = encode(out)
    raw += b' ' * (-len(raw) % 4)
    packed.extend(b'\0' * (-len(packed) % 4))
    return struct.pack('<III',0x46546C67,2,28+len(raw)+len(packed)) + struct.pack('<II',len(raw),0x4E4F534A) + raw + struct.pack('<II',len(packed),0x004E4942) + packed


def main():
    contract = load_contract()
    require_source(contract['world_source'])
    require_source(contract['vehicle']['source'])
    inputs = contract['staging']
    city_path = resolve(inputs['city'])
    provenance = json.loads(city_path.with_suffix('.json').read_text(encoding='utf-8'))
    if provenance['source_file'] != contract['world_source']['file'] or provenance['source_sha256'] != contract['world_source']['sha256']:
        raise ValueError('Exportação de cidade pertence a outra revisão')
    if provenance['export_sha256'] != sha256(city_path):
        raise ValueError('GLB alterado depois da exportação')
    surfaces = json.loads(resolve(inputs['surfaces']).read_text(encoding='utf-8'))
    if surfaces.get('source_sha256') != contract['world_source']['sha256']:
        raise ValueError('Reexporte superfícies da fonte ativa antes de empacotar')
    hashes = {key:sha256(resolve(value)) for key,value in inputs.items()}
    release = hashlib.sha256(encode({'contract':contract,'inputs':hashes,'packager':sha256(__file__)})).hexdigest()[:20]
    public = resolve(contract['runtime']['public_root'])
    directory = public / 'world/releases' / release
    def emit(asset_id, filename, payload, **extra):
        atomic(directory / filename, payload)
        return {'id':asset_id,'url':f'/world/releases/{release}/{filename}', 'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload),**extra}
    doc, binary = read_glb(city_path)
    bounds, parents = scene_bounds(doc)
    groups = {}
    cell = contract['runtime']['streaming']['cell_m']
    for index, (low, high) in bounds.items():
        if max(high[0]-low[0],high[2]-low[2]) > cell:
            key = 'city-core'
        else:
            key = f'city-cell-{math.floor((low[0]+high[0])/2/cell)}-{math.floor((low[2]+high[2])/2/cell)}'
        groups.setdefault(key, []).append(index)
    assigned = [i for group in groups.values() for i in group]
    if len(set(assigned)) != len(bounds) or len(assigned) != len(bounds):
        raise ValueError('Perda ou duplicação de nós na setorização')
    sectors = []
    for name, indices in sorted(groups.items()):
        sectors.append(emit(name,name+'.glb',subset(doc,binary,indices,parents), bounds=union([bounds[i] for i in indices]), always_loaded=name=='city-core', source_nodes=indices))
    # Veículos são assets completos: nunca passar rig/animação pelo particionador estático.
    vehicle = emit(contract['vehicle']['id'],'vehicle.glb',resolve(inputs['vehicle']).read_bytes(),source=contract['vehicle']['source'],dimensions=contract['vehicle']['dimensions'])
    assets = {'vehicle':vehicle}
    if 'urban_slice' in inputs:
        urban_slice = json.loads(resolve(inputs['urban_slice']).read_text(encoding='utf-8'))
        if urban_slice.get('source', {}).get('sha256') != contract['world_source']['sha256']:
            raise ValueError('Superfícies da slice pertencem a outra revisão')
        assets['urban_slice'] = emit('urban-slice', 'urban_slice.json', encode(urban_slice))
    # Legado exportado em X,Z,Y; a release tem somente o contrato glTF canônico.
    if surfaces['coordinates'] == 'x=Blender.X,y=Blender.Z,z=Blender.Y; meters':
        for mesh in surfaces['meshes']:
            mesh['positions'][2::3] = [-z for z in mesh['positions'][2::3]]
            for i in range(0,len(mesh['indices']),3):
                mesh['indices'][i+1],mesh['indices'][i+2] = mesh['indices'][i+2],mesh['indices'][i+1]
    elif surfaces['coordinates'] != 'X,Z,-Y':
        raise ValueError('Coordenadas de suporte desconhecidas')
    surfaces['coordinates'] = 'X,Z,-Y'
    assets['surfaces'] = emit('gameplay-surfaces','surfaces.json',encode(surfaces))
    for key in ('foundation','roads'):
        assets[key] = emit(key,key+'.json',resolve(inputs[key]).read_bytes())
    manifest = {'schema':'boas/runtime-world-v1','area_id':contract['area_id'],'release':release,
        'production_sha256':sha256(CONTRACT),'source':contract['world_source'],'coordinates':contract['coordinates'],
        'settings':contract['runtime'],'assets':assets,'sectors':sectors,
        'bounds':union(list(bounds.values())),
        'focus_bounds':union([bounds[i] for ids in groups.values() for i in ids if max(bounds[i][1][0]-bounds[i][0][0],bounds[i][1][2]-bounds[i][0][2]) <= cell]),
        'inventory':{'source_mesh_nodes':len(bounds),'packaged_mesh_nodes':len(assigned),'sector_count':len(sectors)},
        'limitations':contract['limitations']}
    atomic(directory/'manifest.json',encode(manifest))
    atomic(public/'world/runtime.json',encode(manifest))
    report = {'release':release,'source':contract['world_source'],'inventory':manifest['inventory'],
        'bytes':sum(s['bytes'] for s in sectors),'publication':'complete','source_geometry_modified':False}
    atomic(ROOT/'docs/reports/runtime/package_world.json',encode(report))
    print(json.dumps(report,ensure_ascii=False))


if __name__ == '__main__':
    main()
