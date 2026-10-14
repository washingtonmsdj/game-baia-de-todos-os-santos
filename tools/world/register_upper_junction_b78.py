"""Registra a revisão real e sua proveniência; não promove produção/runtime."""
import argparse, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def main():
    p = argparse.ArgumentParser(); p.add_argument('--verified', action='store_true'); args = p.parse_args()
    r = json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))
    entry = {**r['source_after'], 'parent_file': r['source_before']['file'],
             'status': 'corridor_slice_candidate', 'production_ready': False,
             'source_reopened': args.verified,
             'evidence': 'docs/reports/blender/lacerda-corridor/scene_b78.json',
             'notes': 'Retornos existentes conciliados com a largura da passarela; sem alteração geográfica. Dimensões reais/engine continuam pendentes.'}
    with (ROOT/entry['file']).open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == entry['sha256']
    if args.verified:
        v = json.loads((ROOT/'docs/reports/blender/lacerda-corridor/validation_b78.json').read_text(encoding='utf8'))
        assert v['passed'] and v['source_reopened'] and v['reopen_evidence']['sha256'] == entry['sha256']
        entry['validation_evidence'] = 'docs/reports/blender/lacerda-corridor/validation_b78.json'
    path = ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json'
    catalog = json.loads(path.read_text(encoding='utf8'))
    assert catalog['validation_source']['revision'] in ('R30B.77B', 'R30B.78')
    catalog['revisions'] = [x for x in catalog['revisions'] if x['file'] != entry['file']]+[entry]
    catalog['validation_source'] = entry
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    path = ROOT/'world/data-provenance.json'; registry = json.loads(path.read_text(encoding='utf8'))
    legacy = next(x for x in registry['resources'] if x['resource_id'] == 'derived:lacerda-corridor-b77')
    resource = {'resource_id': 'derived:lacerda-junction-b78', 'provider': 'Bay of All Saints — autoria local',
                'dataset': 'Correção determinística de encaixe da B77B', 'kind': 'derived_geometry',
                'usage_class': legacy['usage_class'], 'capture_date': None, 'raw_files': [],
                'dependencies': ['derived:lacerda-corridor-b77'], 'source_scene': r['source_before'],
                'coordinate_reference': 'world/geographic-reference.json',
                'measurement_frame': r['measurement_frame'],
                'bounds': None,
                'purpose': 'Corrigir aberturas laterais indevidas entre saguão e passarela; paredes e colisores separados',
                'derived_objects': [x['object'] for x in r['changed_meshes']]+r['added_objects'],
                'reference_media_ids': r['reference_media_ids'],
                'reference_use': 'Contexto de desenvolvimento; fotografias não determinam dimensões nem viram textura',
                'evidence': 'docs/reports/blender/lacerda-corridor/scene_b78.json'}
    registry['resources'] = [x for x in registry['resources'] if x['resource_id'] != resource['resource_id']]+[resource]
    path.write_text(json.dumps(registry, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'revision': entry['revision'], 'verified': args.verified, 'production_promoted': False}))

if __name__ == '__main__': main()
