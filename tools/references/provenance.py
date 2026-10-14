"""Política central e índice de proveniência, reaproveitando os catálogos existentes."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load_policy(root=ROOT):return json.loads((root/'world/provenance-policy.json').read_text(encoding='utf8'))
def release_class(record,policy):
    value=record.get('release_status')
    if value is None:value=policy['legacy_usage_mapping'].get(record.get('usage_class'))
    return value if value in policy['classes'] else None
def catalog(root=ROOT):
    registry=json.loads((root/'world/data-provenance.json').read_text(encoding='utf8'))
    result={}
    def add(record):
        key=record['resource_id']
        if key in result:raise ValueError('ID de proveniência duplicado: '+key)
        result[key]=record
    for r in registry['resources']:add(r)
    for path in (root/'world').glob('**/media-manifest.json'):
        for item in json.loads(path.read_text(encoding='utf8')).get('media',[]):
            add({'resource_id':'media:'+item['media_id'],'usage_class':item['usage_class'],'provider':item.get('provenance',{}).get('source_name'),'dataset':item.get('source_type'),'raw_files':[{'path':'world-reference/'+item['storage']['logical_path'],'sha256':item['storage'].get('sha256')}],'capture':item.get('capture'),'catalog_reference':path.relative_to(root).as_posix(),'dependencies':[],'kind':'raw_reference'})
    return result
def safe_path(root,value):
    path=Path(value)
    if path.is_absolute() or '..' in path.parts:raise ValueError('Caminho de pacote inválido: '+value)
    resolved=(root/path).resolve()
    if not resolved.is_relative_to(root.resolve()):raise ValueError('Caminho fora do projeto: '+value)
    return resolved
