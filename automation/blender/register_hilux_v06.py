"""Registra a fonte V06 conferida, sem promover fidelidade para approved."""
import hashlib,json
from pathlib import Path
repo=Path(__file__).resolve().parents[2]
report_path=repo/'docs/reports/blender/rondesp_marrom_v06.json'
report=json.loads(report_path.read_text(encoding='utf-8'))
source=repo/report['file']
assert source.name=='marrom_v06.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==report['sha256']
report['reopen_verification']={'verified':True,'method':'get_blender_status após conclusão do comando MCP 5934e42f41574b518bab64ce2f7f5c19','file_observed':report['file'],'scene_observed':report['scene'],'pid':11116,'is_dirty':False}
report['visual_review']={'views':['v06-base-lateral.png','v06-base-frente.png','v06-base-frontal.png','v06-frente.png','v06-traseira.png','v06-materiais.png'],'latest_material_view':'artifacts/vehicles/rondesp/v06-materiais.png','status':'candidate','limitations':'Comparação visual qualitativa; fidelidade perfeita e equivalência ao ônibus não demonstradas. Brasão e camuflagem simplificados.'}
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
catalog_path=repo/'world/vehicles/catalog.json'
catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
vehicle=next(v for v in catalog['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')
base={k:report[k] for k in ['file','scene','sha256']}
vehicle['authoring_base']=base
variant=vehicle['variants'][0];variant.update(base,status='candidate')
variant['scope']='Hilux Rondesp 3.1110 V06: carroceria, cabine, frente e ópticas reconstruídas pelas referências já catalogadas. Fidelidade ainda em revisão; brasão detalhado e mapa exato da camuflagem pendentes. Sem integração runtime.'
vehicle['revision_policy']='V06 é a fonte explícita de autoria. V01–V05 são históricas e não aprovadas; não escolher por sufixo/mtime. Novo passe deve partir do catálogo e conferir o arquivo aberto.'
catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='''## 03/10/2026 — Hilux Rondesp: autoria candidata V06

Fonte explícita: `blender/assets/vehicles/rondesp-pickup/marrom_v06.blend`, cena
`VIATURA | Rondesp Hilux marrom v06`. Hash no catálogo e em
`docs/reports/blender/rondesp_marrom_v06.json`. V01–V05 preservadas; V04/V05
não atendiam à fidelidade solicitada. Não retomar essas bases pelo histórico.

V06 reconstrói a carroceria pelas referências existentes: caimento do capô,
ombros dos para-lamas, estreitamento da cabine no teto, vãos curvos das janelas,
chapas das portas, batentes/soleiras, grade STD, câmaras ópticas e lentes,
capota e lanternas. Inscrições da 3.1110 conformadas à superfície. Entre-eixos
mantido em 3,085 m; especificações nominais em `world/vehicles/hilux-dimensions.json`.
As seções da carroceria continuam interpretações de imagens com perspectiva,
não medidas de escaneamento; acessórios policiais não têm dimensões verificadas.

Revisão visual: frente, lateral, traseira e forma neutra em
`artifacts/vehicles/rondesp/v06-*.png`. Trabalho via MCP na única instância visível.
Scripts: `rebuild_hilux_reference_v06.py`, `finish_hilux_reference_v06.py`,
`present_hilux_v06.py`, em `automation/blender/`. Executam passes de modelagem;
não repetir um passe de acabamento na mesma revisão sem conferir seu escopo.

Status **candidate**, não approved e não declarado equivalente ao ônibus.
Pendentes: aprovação de fidelidade, brasão PMBA detalhado, camuflagem exata,
animação das portas e integração runtime. Sem pesquisa adicional, npm/build ou
testes gerais neste ciclo, conforme escopo solicitado; sem commit/push.

'''
for rel in ['docs/PROJECT_STATUS.md','docs/CODEX_HANDOFF.md']:
    path=repo/rel;text=path.read_text(encoding='utf-8')
    if '## 03/10/2026 — Hilux Rondesp: autoria candidata V06' not in text:
        i=text.index('\n')+1;text=text[:i]+'\n'+note+text[i:]
        path.write_text(text,encoding='utf-8')
readme=repo/'world/vehicles/README.md'
text=readme.read_text(encoding='utf-8')
if '## Hilux Rondesp V06' not in text:
    text+='\n## Hilux Rondesp V06\n\nAutoria ativa no catálogo: `rondesp-pickup/marrom_v06.blend`, sob `blender/assets/vehicles/`. V01–V05 preservadas como histórico não aprovado. Carroceria em revisão de fidelidade; não integrada ao runtime. Relatório: `docs/reports/blender/rondesp_marrom_v06.json`.\n'
    readme.write_text(text,encoding='utf-8')
print(json.dumps({'source':report['file'],'sha256':report['sha256'],'status':'candidate'}))
