"""Consolida evidência já examinada; não modifica Blender nem aprova caminho."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/reports/research/lower-lobby-connector'

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))

def digest(path):
    with (ROOT / path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    live = read('docs/reports/research/lower-lobby-connector/live_object_audit.json')
    guide = next(row for row in live['objects'] if row['object'] == 'INFERIOR | guia de fila.001')
    history = read('docs/reports/research/lower-lobby-connector/historical_r30a_object.json')
    trace = read('docs/reports/research/lower-lobby-connector/controller_trace.json')
    manifest = read('world/areas/mvp-centro-lacerda/media-manifest.json')['media']
    reviews = []
    observations = {
        'elevador-lacerda-front-2d9b4031ff6a': 'Exterior 2025: ENTRADA/BILHETES e pavimento visíveis; interior escuro/oculto. Não comprova guia nem passagem interna.',
        'elevador-lacerda-detail-6e9796b71968': 'Street View julho/2024: marquise/andaimes; entrada recortada. Não comprova guia nem ausência; obras são transitórias.'
    }
    for row in manifest:
        if row['media_id'] in observations:
            file = 'world-reference/' + row['storage']['logical_path']
            reviews.append({'media_id': row['media_id'], 'file': file,
                            'sha256': digest(file), 'source': row['provenance'],
                            'capture': row['capture'], 'observation': observations[row['media_id']],
                            'physical_correspondence_accepted': False})
    sheet = next(row for row in read('docs/reports/research/lacerda-issue22/source_summary.json')['resources']
                 if any(x['path'].endswith('/sucop-architectural-12.pdf') for x in row['raw_files']))
    reviews.append({'resource_id': sheet['resource_id'], 'source_url': sheet['source_url'],
                    'file': sheet['raw_files'][0]['path'], 'sha256': digest(sheet['raw_files'][0]['path']),
                    'observation': 'Planta inferior 2023 mostra saguão/túnel/torre e aberturas; registro XY aceito inexistente. Não associa inequivocamente esta guia à cena.',
                    'physical_correspondence_accepted': False})
    preserved = []
    for row in read('docs/reports/blender/cairu-market-b81/protected_baseline.json')['protected']:
        actual = digest(row['file'])
        preserved.append({'file': row['file'], 'expected': row['sha256'], 'actual': actual, 'preserved': actual == row['sha256']})
    for file, expected in [
        ('blender/salvador_lacerda_r30b81_cairu_colisao_e_rota_parcial.blend', '45583e49dde0a4a03d6b8d4a654135bb11644e786acb681dab7da3d68984e4af'),
        ('world/geographic-reference.json', '1d9da0962d456cb38ed3df0da797208e499a8465f82e9836c14bb337df2385e7')]:
        actual = digest(file)
        preserved.append({'file': file, 'expected': expected, 'actual': actual, 'preserved': actual == expected})
    assert all(x['preserved'] for x in preserved), 'Baseline alterada'
    contract = read('world/areas/mvp-centro-lacerda/cairu-market-pedestrian.json')
    result = {
        'decision': 'NO_SCENE_CHANGE', 'new_revision': None, 'object_classification': 'UNRESOLVED',
        'LACERDA_VERTICAL': 'BLOCKED_EXTERNAL_EVIDENCE', 'LOWER_LOBBY_TO_OSM': 'UNRESOLVED_BLOCKED',
        'OSM_CROSSING': 'TOPOLOGY_CONFIRMED_NOT_ADVANCED', 'MARKET_ENTRANCE_CONNECTOR': 'UNRESOLVED_NOT_ADVANCED',
        'TRAFFIC_PERMISSION': None, 'movement_enabled': False, 'partial_osm_route_enabled': False,
        'facts_scene_only': guide, 'historical_evidence': history,
        'history_limitations': ['Mesma caixa e bounds já registrados na auditoria R30A.',
                                'Summaries R27/R30A são agregados; falta de match não prova ausência.',
                                'Busca literal em automation/blender e git log -S não recuperou script/commit de criação. Não é prova de inexistência.',
                                'Sem evidência identificando mobiliário real permanente, temporário ou obsoleto.'],
        'reference_reviews': reviews, 'first_blocked_move': trace['stop'],
        'controller_source': 'docs/reports/research/lower-lobby-connector/controller_trace.json',
        'controller_limits': ['Replay numérico, não certificação de engine.',
                              'Normal de slide horizontal nula na face horizontal mais próxima; não há avanço lateral executado.',
                              'Testemunha CCD é penetração amostrada adaptativamente, não instante exato do primeiro contato.',
                              'Rota existente 736745764→3178050253 é baseline candidata; nó inicial não comprova saída física do saguão.'],
        'required_external_evidence': 'Vista atual do interior inferior mostrando guia e saída em conjunto, ou levantamento/planta registrada com controles permanentes. Confirmar passagem e piso até o início OSM.',
        'preservation': preserved, 'pedestrian_contract_sha256': digest('world/areas/mvp-centro-lacerda/cairu-market-pedestrian.json'),
        'contract_not_changed': True, 'no_new_connector': True, 'no_crossing_or_market_test': True,
        'protected_witnesses': 27, 'curb_patch_preserved': True, 'paint_render_only_preserved': True
    }
    (OUT / 'decision.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'decision': result['decision'], 'object_classification': result['object_classification'],
                      'protected_files': len(preserved), 'first_blocked_move': trace['stop']['point']}))

if __name__ == '__main__':
    main()
