"""Contrato geográfico compartilhado: validar, sem realinhar regiões."""
import json, math
from pathlib import Path


def read_reference(path):
    path=Path(path)
    data=json.loads(path.read_text(encoding='utf8'))
    if data.get('schema')!='boas/geographic-reference-v1':raise ValueError('SSOT geográfico não suportado')
    fit=data['horizontal']['transform']
    if len(fit['translation_blender'])!=2:raise ValueError('Translação XY deve conter duas coordenadas')
    if fit['scale_blender_units_per_meter']<=0:raise ValueError('Escala horizontal inválida')
    for value in [fit['scale_blender_units_per_meter'],fit['rotation_epsg3857_to_blender_deg'],*fit['translation_blender']]:
        if not math.isfinite(value):raise ValueError('Transform geográfico não finito')
    if data['vertical']['absolute_datum_verified'] and not data['vertical']['absolute_datum']:
        raise ValueError('Datum não pode ser verificado sem identificação')
    return data


def require_shared_transform(fit,ssot):
    expected=ssot['horizontal']['transform']
    if len(fit['translation_blender'])!=2:raise ValueError('Origem regional deve conter duas coordenadas')
    for key in ('scale_blender_units_per_meter','rotation_epsg3857_to_blender_deg'):
        if not math.isclose(float(fit[key]),float(expected[key]),rel_tol=0,abs_tol=1e-10):
            raise ValueError('Transform regional diferente do SSOT: '+key)
    if any(abs(float(a)-float(b))>1e-7 for a,b in zip(fit['translation_blender'],expected['translation_blender'])):
        raise ValueError('Origem regional diferente do SSOT')


def project_reference(root,fit):
    path=Path(root)/'world/geographic-reference.json'
    if not path.exists():return None
    data=read_reference(path);require_shared_transform(fit,data)
    return data
