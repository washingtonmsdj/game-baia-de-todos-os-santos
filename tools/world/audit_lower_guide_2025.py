"""Consolida revisão visual humana de 2025; nunca altera Blender ou habilita rota."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/reports/research/lower-guide-2025'
RAW = Path('world-reference/mvp-centro-lacerda/research-lower-guide-20261006')


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf8'))


def sha(path):
    h = hashlib.sha256()
    with (ROOT / path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = read('world/areas/mvp-centro-lacerda/media-manifest.json')['media']
    photos = [
        ('125127', 'Painel envidraçado decorativo LACERDA/Salvador entre colunas de mármore; piso quase ausente.',
         'Contexto interior; não mostra guia/saída/conector.'),
        ('125222', 'Placa sobre mármore informa entrega da restauração em fevereiro de 2025.',
         'Contexto pós-restauração; não comprova configuração da guia.'),
        ('125324', 'Galeria envidraçada superior; vista da Cidade Baixa/escarpa e indicação SAÍDA.',
         'Distinguir saída superior da inferior; não usar como conector Cairu.'),
        ('125657', 'Rocha exposta da escarpa, revestimento inferior de mármore e iluminação suspensa.',
         'Contexto construtivo; nenhuma associação inequívoca com a guia.'),
        ('125707', 'Saguão inferior com ilha de bilheteria envidraçada, mural à direita e fachada/SAÍDA; pessoa sai à esquerda da ilha; piso externo claro e veículos visíveis.',
         'Há passagem junto à bilheteria até abertura externa. Não identifica a guia .001 nem registra o conector no SSOT/OSM.')]
    evidence = []
    for suffix, observation, conclusion in photos:
        media = next(m for m in manifest if '20250721' + suffix in m['storage']['logical_path'])
        path = Path('world-reference') / media['storage']['logical_path']
        digest = sha(path)
        if digest != media['storage']['sha256']:
            raise ValueError(f'Hash da foto divergente: {path}')
        evidence.append({'source': media['provenance']['source_url'], 'date': media['capture']['date'],
                         'frame/image': path.name, 'raw_file': path.as_posix(), 'sha256': digest,
                         'author': 'Sintegrity', 'license': media['provenance']['license'],
                         'media_id': media['media_id'], 'observed_feature': observation,
                         'confidence': {'visible_feature': 'HIGH', 'exact_scene_binding': 'UNRESOLVED'},
                         'scene_correspondence': None, 'allowed_conclusion': conclusion,
                         'not_proven': ['Dimensão métrica', 'Identidade/posição da guia .001', 'Permanência/fixação da guia', 'Conexão física registrada até OSM'],
                         'inspection': 'Imagem integral examinada, não apenas título/descrição',
                         'release_status': 'DEV_REFERENCE_ONLY'})
    videos = {
        'b896lscqBws': {'publication_date': '2025-07-15', 'duration_seconds': 139,
                       'title': 'Salvador Bahia Como é o Elevador Lacerda por Dentro'},
        '0VC78CYx0X0': {'publication_date': '2025-03-14', 'duration_seconds': 714,
                       'title': 'Elevador Lacerda por dentro Depois da Reforma A Nova Vista Incrível de Salvador Bahia'}}
    frames = [
        ('b896lscqBws', '010', 10, 'Corredor abobadado; portas ao fundo, gradis centrais; barreira metálica separada e cones laranja.', 'Gradis e objetos de controle de fila são fisicamente visíveis; não confundir barreira/cones com o gradil.'),
        ('b896lscqBws', '020', 20, 'Dois gradis longos paralelos escuros, montantes verticais e corrimão castanho; pessoa circula pela lateral esquerda.', 'Guia física genérica e circulação lateral observadas; correspondência .001 não comprovada.'),
        ('b896lscqBws', '038', 38, 'Corredor com gradil central e pessoa circulando à direita; barreira separada ao fundo.', 'Passagem lateral ao gradil visível nesta vista; não registra percurso até a saída inferior.'),
        ('b896lscqBws', '060', 60, 'Vista a partir de abertura, voltada ao corredor abobadado com gradis/pessoas.', 'Contexto dos gradis; nenhuma conclusão dimensional da cabine/poço.'),
        ('b896lscqBws', '083', 83, 'Galeria envidraçada e saída com espaço externo superior/guarda-corpo.', 'Saída superior; não constitui prova do conector inferior.'),
        ('0VC78CYx0X0', '071', 71, 'Fachada inferior LACERDA, bilheteria ao fundo, pedestres e pavimento externo; pintura verde diante da fachada.', 'Localização contextual inferior; nenhum avanço ou autorização de travessia.'),
        ('0VC78CYx0X0', '142', 142, 'Saguão inferior, volume central revestido e abertura arqueada lateral; piso parcialmente visível.', 'Relação geral saguão/corredor; não registra a guia no SSOT.'),
        ('0VC78CYx0X0', '214', 214, 'Fila de pessoas junto ao mármore; corpos ocultam grande parte do piso/gradis.', 'Oclusão impede análise conclusiva do conector.')]
    for video, suffix, seconds, observation, conclusion in frames:
        path = RAW / f'{video}-{suffix}.png'
        evidence.append({'source': f'https://www.youtube.com/watch?v={video}&t={seconds}s',
                         'date': None, 'publication_date': videos[video]['publication_date'],
                         'frame/image': path.name, 'observed_player_time_seconds': seconds,
                         'timestamp_precision': 'Posição indicada pelo player; não timecode de frame extraído',
                         'raw_file': path.as_posix(), 'sha256': sha(path),
                         'author': 'Farol Viagem (@FarolViagem)', 'license': None,
                         'license_status': 'NOT_VERIFIED', 'release_status': 'DEV_REFERENCE_ONLY',
                         'observed_feature': observation,
                         'confidence': {'visible_feature': 'HIGH' if suffix != '214' else 'LOW', 'exact_scene_binding': 'UNRESOLVED'},
                         'scene_correspondence': None, 'allowed_conclusion': conclusion,
                         'not_proven': ['Data da filmagem', 'Dimensões métricas', 'Identidade/posição/fixação da guia .001', 'Conector inferior registrado até OSM'],
                         'inspection': 'Quadro real reproduzido no navegador e screenshot nativo; nenhum vídeo bruto baixado'})
    excluded = []
    for suffix, reason in [('106', 'Buffering/quadro anterior; horário não utilizável'),
                           ('106-ready', 'Mural visível, mas instante exato não certificado; só contexto'),
                           ('126', 'Buffering/quadro anterior; horário não utilizável'),
                           ('121-ready', 'Placa visível, divergência slider/tempo do player; não usar para registro temporal/espacial')]:
        path = RAW / f'0VC78CYx0X0-{suffix}.png'
        excluded.append({'raw_file': path.as_posix(), 'sha256': sha(path), 'source': 'https://www.youtube.com/watch?v=0VC78CYx0X0',
                         'author': 'Farol Viagem (@FarolViagem)', 'publication_date': '2025-03-14',
                         'date': None, 'license': None, 'release_status': 'DEV_REFERENCE_ONLY', 'reason': reason,
                         'used_for_decision': False})
    write('docs/reports/research/lower-guide-2025/visual_evidence.json', {
        'schema': 'boas/lower-guide-visual-evidence-v1', 'review_date': '2026-10-06',
        'method': 'Revisão humana integral de cinco fotografias e quadros selecionados de dois vídeos; não são vídeos integralmente assistidos.',
        'coordinate_registration_accepted': False, 'metric_measurements_from_images': False,
        'videos': videos, 'evidence': evidence, 'excluded_captures': excluded})
    baseline = read('docs/reports/research/lower-lobby-connector/decision.json')
    preservation = [{'file': row['file'], 'expected': row['actual'], 'actual': sha(row['file'])} for row in baseline['preservation']]
    for row in preservation:
        row['preserved'] = row['expected'] == row['actual']
    contract_hash = sha('world/areas/mvp-centro-lacerda/cairu-market-pedestrian.json')
    if not all(row['preserved'] for row in preservation) or contract_hash != baseline['pedestrian_contract_sha256']:
        raise ValueError('Baseline protegido/contrato alterado')
    replay = read('docs/reports/research/lower-guide-2025/controller_slide_final.json')
    slides = [row for row in replay['steps'] if row['mode'] == 'slide_collision_normal']
    write('docs/reports/research/lower-guide-2025/decision.json', {
        'decision': 'NO_SCENE_CHANGE', 'new_revision': None, 'guide_classification': 'STILL_UNRESOLVED',
        'generic_physical_guides_observed': True, 'generic_passages_observed': True,
        'exact_guide_scene_binding': None, 'permanence_or_removability': None,
        'allowed_scene_changes': [], 'new_route_authorized': False,
        'reason': 'Gradis e circulação lateral visíveis, mas nenhuma correspondência inequívoca com .001/SSOT nem sequência física registrada até o nó OSM.',
        'LACERDA_VERTICAL': 'BLOCKED_EXTERNAL_EVIDENCE', 'LOWER_LOBBY_TO_OSM': 'UNRESOLVED_BLOCKED',
        'OSM_CROSSING': 'TOPOLOGY_CONFIRMED_NOT_ADVANCED', 'MARKET_ENTRANCE_CONNECTOR': 'UNRESOLVED_NOT_ADVANCED',
        'TRAFFIC_PERMISSION': None, 'movement_enabled': False, 'partial_osm_route_enabled': False,
        'protected_witnesses': '27 UNRESOLVED B80; sem CCD vertical repetido',
        'curb_patch_preserved': True, 'paint_render_only_preserved': True,
        'solver_comparison': {'before_first_block': 51, 'after_accepted_moves': len(replay['steps']),
                              'after_slides': len(slides), 'after_stop': replay['stop'],
                              'arrival_approved': False, 'engine_verified': False},
        'solver_limits': ['Apoio consultado no centro, sem prova completa de borda',
                          'Alvos de waypoint podem ficar distantes após slides; parada não certifica queda/step real nem impossibilidade do trajeto',
                          'Replay candidato não é controller de engine nem comprovação de conector físico'],
        'preservation': preservation, 'pedestrian_contract_sha256': contract_hash})
    print(json.dumps({'photos': 5, 'video_frames': len(frames), 'protected_files': len(preservation),
                      'decision': 'NO_SCENE_CHANGE', 'guide': 'STILL_UNRESOLVED'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
