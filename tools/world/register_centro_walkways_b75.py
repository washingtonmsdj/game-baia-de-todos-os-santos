"""Registrar evidências B75 sem promover autoria/produção nem perder pendências."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
REPORTS=ROOT/'docs/reports/blender/centro-expansion'


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def write(path,data):
    temporary=path.with_suffix(path.suffix+'.writing')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    temporary.replace(path)


def main():
    scene=read(REPORTS/'scene_b75.json');validation=read(REPORTS/'validation_b75.json')
    source=scene['source_after'];derivation=read(REPORTS/'walkways_b75_derivation.json')
    assert source==validation['source'] and validation['source_reopened'] and validation['saved_partitions_exact']
    with (ROOT/source['file']).open('rb') as stream:
        assert hashlib.file_digest(stream,'sha256').hexdigest()==source['sha256']
    catalog_path=ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json';catalog=read(catalog_path)
    assert catalog['validation_source']['sha256']==source['sha256']
    for entry in catalog['revisions']:
        if entry['file']==source['file']:
            entry.update({'source_reopened':True,'local_geometry_checks_passed':True,'validation_evidence':'docs/reports/blender/centro-expansion/validation_b75.json'})
    catalog['validation_source'].update({'source_reopened':True,'local_geometry_checks_passed':True,'validation_evidence':'docs/reports/blender/centro-expansion/validation_b75.json'})
    write(catalog_path,catalog)
    scene.update({'source_reopened':True,'validation_evidence':'docs/reports/blender/centro-expansion/validation_b75.json','visual_review_status':'images_checked_world_partial'})
    write(REPORTS/'scene_b75.json',scene)
    visual=read(REPORTS/'visual_review_b75.json')
    visual.update({'images_inspected':visual['images'],'status':'partial_world','findings':['Passeios estreitos com largura explícita encaixados no terreno','Ruas finais ainda ausentes na expansão','Intervalo entre borda de terreno e água do Dique exige perfil de margem/altimetria; não aprovado'],'shore_review':'docs/reports/blender/centro-expansion/dique_shore_height_b75.json'})
    write(REPORTS/'visual_review_b75.json',visual)
    ledger_path=ROOT/'world/areas/centro-lapa-tororo-fontenova/road-corrections.json';ledger=read(ledger_path)
    ids={i['issue_id'] for i in ledger['issues']}
    shore={'issue_id':'B75-dique-shore-height','status':'pending','osm_relation_id':15601931,'classification':'SOURCE_LIMITATION','reason':'Borda do terreno e água candidata sem perfil coerente/fechamento da margem; delta Z máximo 23,9923 unidades, altimetria absoluta não verificada.','evidence':'docs/reports/blender/centro-expansion/dique_shore_height_b75.json'}
    if shore['issue_id'] not in ids:ledger['issues'].append(shore)
    ledger['validation_source']=source;ledger['latest_modeling_cycle']='R30B.75'
    write(ledger_path,ledger)
    section=f'''## 05/10/2026 — B75: passeios por larguras OSM; margem do Dique pendente

Fonte de validação: `{source['file']}`, SHA-256 `{source['sha256']}`. Aplicada pelo MCP 9876 na única janela, salva, reaberta e conferida. B74 preservada; autoria B41 e produção B30 mantidas.

29 passeios candidatos, com 4.437,29 unidades de eixo e larguras explícitas OSM (não levantamento). Conversão horizontal explicita o fit EPSG:3857 candidato e a escala Mercator local. Superfície subdividida, passeios removidos da base e encaixados em objetos próprios com OSM IDs; sem planos elevados sobrepostos. Todos os controles originais do terreno mantidos; erro Z máximo dos novos pontos relativo às faces anteriores: 0,00000487 unidade. 22 divisões de arestas corrigem nós colineares desconectados nos encontros. Malha combinada sem frestas internas, triângulos degenerados ou arestas com mais de duas faces; partições reabertas idênticas aos dados derivados, sem vértices órfãos.

Seis trechos excluídos: três conflitos com footprints, duas travessias dependentes de via e uma ligação de escada. Ledger preserva os 106 alertas B74 e adiciona esses seis casos e a margem do Dique. Costa, cais, núcleo, água e marcos anteriores preservados. Replays RONDESP e câmera mantidos; a subdivisão conserva a superfície anterior, mas não houve novo teste físico e ruas finais continuam ausentes.

Revisão visual B74 completada após liberar espaço; duas imagens B75 conferidas. O lago revela um intervalo entre terreno aberto e água plana candidata: delta Z varia de -0,1232 a 23,9923 unidades. Altimetria/resolução nativa desconhecidas; não são alturas reais medidas. Resolver perfil hidrológico/margem antes de aprovar o Dique, sem elevar água globalmente ou criar um muro para ocultar a diferença. Os passeios seguem relevo candidato e não têm caminhabilidade aprovada.

Evidências: `docs/reports/blender/centro-expansion/{{walkways_b75_derivation,scene_b75,validation_b75,visual_review_b75,dique_shore_height_b75}}.json`; scripts reproduzíveis em `tools/world/derive_centro_walkways_b75.py` e `automation/blender/model_centro_walkways_b75.py`. Próximo: coerência vertical/margem do Dique, limites/larguras e perfis de vias, travessias/acessos. Serviços públicos GeoSalvador/SIG Salvador e CONDER foram consultados apenas para localizar fontes; nenhuma camada foi adquirida ou aprovada. Sem npm/build/suíte de testes, exportação runtime ou aprovação integral.

'''
    for relative in ('docs/PROJECT_STATUS.md','docs/CODEX_HANDOFF.md'):
        path=ROOT/relative;content=path.read_text(encoding='utf8')
        if '## 05/10/2026 — B75:' not in content:
            if content.startswith('# Estado Atual do Projeto'):
                first,rest=content.split('\n',1);content=first+'\n\n'+section+rest.lstrip('\n')
            else:content=section+content
            path.write_text(content,encoding='utf8')
    area=ROOT/'world/areas/centro-lapa-tororo-fontenova/README.md'
    content=area.read_text(encoding='utf8')
    if 'B75' not in content:
        content+='\nB75 acrescenta 29 passeios por largura OSM explícita, subdividindo a superfície candidata sem mudar os controles originais. Seis trechos excluídos e a incoerência entre margem/água do Dique permanecem pendentes em `road-corrections.json`. Ruas para veículos e caminhabilidade ainda não aprovadas. Evidências em `docs/reports/blender/centro-expansion/validation_b75.json`.\n'
        area.write_text(content,encoding='utf8')
    print(json.dumps({'revision':source['revision'],'reopened':True,'walkways':scene['walkway_count'],'issues':len(ledger['issues']),'production_ready':False},ensure_ascii=False))


if __name__=='__main__':main()
