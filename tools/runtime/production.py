"""Contrato de produção compartilhado pelos exportadores; sem dependência de engine."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / 'world/areas/mvp-centro-lacerda/production.json'


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT) or Path(relative).is_absolute():
        raise ValueError(f'Caminho fora do repositório: {relative}')
    return path


def load_contract():
    data = json.loads(CONTRACT.read_text(encoding='utf-8'))
    if data['schema'] != 'boas/production-v1':
        raise ValueError('Contrato de produção incompatível')
    if data['coordinates']['runtime'] != 'X,Z,-Y' or data['coordinates']['meters_per_unit'] != 1:
        raise ValueError('Conversão de coordenadas não suportada; exige migração explícita')
    for source in (data['world_source'], data['vehicle']['source']):
        resolve(source['file'])
        if len(source['sha256']) != 64 or any(c not in '0123456789abcdef' for c in source['sha256']):
            raise ValueError('Hash de fonte inválido')
        if not source.get('scene'):
            raise ValueError('Cena-fonte não declarada')
    for path in data['staging'].values():
        resolve(path)
    streaming = data['runtime']['streaming']
    if not (0 < streaming['cell_m'] and 0 < streaming['load_radius_m'] < streaming['unload_radius_m']):
        raise ValueError('Raio/histerese de streaming inválidos')
    if not 1 <= streaming['concurrency'] <= 8:
        raise ValueError('Concorrência inválida')
    if data['runtime']['render']['max_fps'] <= 0:
        raise ValueError('Orçamento de frames inválido')
    return data


def require_source(entry, actual_path=None):
    path = resolve(entry['file'])
    if actual_path and Path(actual_path).resolve() != path:
        raise ValueError(f'Abra a fonte registrada: {entry["file"]}')
    if sha256(path) != entry['sha256']:
        raise ValueError(f'Fonte alterada sem promoção no contrato: {entry["file"]}')
    return path
