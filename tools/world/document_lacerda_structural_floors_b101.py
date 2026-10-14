"""Registra a estrutura executada e distingue cota, contorno e estimativa."""
import json,hashlib
from pathlib import Path

root=Path(__file__).resolve().parents[2]; out=root/'docs/reports/blender/lacerda-floors-b101'
r=json.loads((out/'application.json').read_text()); q=json.loads((out/'validation.json').read_text())
cfg=json.loads((out/'controls.json').read_text()); p=json.loads((out/'presentation.json').read_text())
assert r['reopened'] and q['reopened'] and q['sha256']==r['sha256']
assert not p['unsaved_changes'] and not p['local_view'] and p['terrain_visible']
with (root/r['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
with (root/r['parent_file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['parent_sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
doc=root/'docs/LACERDA_STRUCTURAL_DIMENSIONS_B101_2026-10-08.md'
rows='\n'.join(f"| {s['object']} | {s['printed_level_offset_m']:.2f} | {s['top_z']:.6f} | {s['area_m2']:.4f} |" for s in cfg['floors'])
doc.write_text(f'''# Lacerda — estrutura dimensional B101 — 08/10/2026

B100 preservada, B101 aplicada/salva/reaberta na única janela Blender/MCP9876, PID{r['pid']}. Fonte `{r['file']}`, SHA256 `{r['sha256']}`. A janela anterior estava encerrada; reaberta a fonte explícita do catálogo, sem segunda instância. Nenhuma nova busca externa, DEM ou registro das pranchas: reutilizados contornos14/15 e transformação documental derivada da B99.

## Estrutura efetivamente acrescentada

Três superfícies estruturais antes ausentes: piso da subestação/subsolo02 e pisos das duas antigas salas técnicas/subsolo03. Não são cabines, mecanismos ou novas plataformas sobre os poços. Não foram alterados torre, ponte, túnel, corpo superior, lajes anteriores ou terreno para acomodar essas peças.

| Componente | Cota relativa documental (m) | Z arquitetônico (m) | Área do contorno modelado (m²) |
|---|---:|---:|---:|
{rows}

A cota−9,74 vem da15;−19,85 vem da14. As posições dos contornos vêm das faces internas e quinas CAD registradas em `controls.json`, não de pixels de fotografia. A laje02 segue o contorno principal das superfícies da subestação, preservando a reentrância dos lances da escada. Cotas/níveis impressos e coordenadas derivadas de vetores são categorias diferentes no manifesto dimensional.

Espessura0,25m continua candidata, não cálculo estrutural/as-built. Pequenos rebaixos/jambas foram simplificados. As áreas da tabela são das placas modeladas; **não equivalem automaticamente à área útil anunciada de cada ambiente**. A descrição de subestação100,48m² não é usada para reescalar o contorno ou fabricar piso sobre escada/equipamento.

Os pisos03 registram os contornos principais e o nível documental. **Altura/teto das salas, fechamento das paredes entre níveis e conexão física completa dessas salas não estão comprovados nesta revisão**. Não interpretar o empilhamento de lajes como edifício completo, estrutura civil calculada ou circulação aprovada. Não extrudir paredes até a planta15 apenas por ela mostrar a projeção da cobertura.

## Controle dimensional consolidado

`docs/reports/blender/lacerda-floors-b101/dimensions.json` passa a concentrar as verificações desta estrutura, subordinado a `world/geographic-reference.json`, sem outro SSOT. Inclui13 controles de níveis existentes, três pavimentos novos e quatro contornos documentais: torre nova, ponte, galeria e saguão superior. Corpo/cobertura e subsolos anteriores apontam para os controles B100/B99 já executados; não há necessidade de repetir aquisição/registro antes de cada edição.

Cotas de saguão inferior−59,01, cobertura inferior−53,17, térreo0,00, cobertura da galeria+4,00, subsolo01−4,97, pavimentos+4,94/+9,42, cobertura+14,00 e platibanda+15,40 foram conferidas na mesh. A camada legada de acabamento da ponte−0,03 permanece explicitamente candidata. Nenhuma dimensão da cabine/poço é inferida dos contornos exteriores ou de nomes de objetos.

## Verificação do arquivo reaberto

{q['objects_checked']} componentes arquitetônicos conferidos, {q['visible_objects_checked']} visíveis. As malhas ativas verificadas não apresentam faces degeneradas, arestas não manifold, winding inconsistente ou duplicatas internas. {q['preserved_component_signatures']} assinaturas anteriores intactas; três componentes novos, zero mesh anterior alterada e zero geometria deletada.

{len(q['floor_surface_probes'])} sondagens das lajes, {len(q['stair_notch_probes'])} sondagens sem laje tampando o recorte da escada. Erro máximo de aplicação dos novos contornos {max(v['contour_max_residual_m'] for v in q['floor_dimension_checks']):.8f}m. Os encontros anteriores ponte/saguão e túnel foram rechecados; portal superior{q['portal_width_m']:.6f}m, conector inferior{q['connector_area_m2']:.6f}m². Não houve npm/build/testes gerais ou novo CCD do equipamento congelado.

Capturas reais inspecionadas: `artifacts/lacerda-live-diagnostic/b101-estrutura.png`, `b101-pavimentos.png` e `b101-map.png`. A vista de pavimentos é uma inspeção temporária sem paredes, não outra cena. Final: mapa completo na cena `SALVADOR | ESBOCO OFICIAL`, terreno visível, sem alterações pendentes.

## Limites que não mudaram

B76–B100 preservadas. SSOT, terreno, duas torres, GAMEPLAY_PROXY B82 e27 testemunhas históricas intactos. `LACERDA_VERTICAL=BLOCKED_EXTERNAL_EVIDENCE`, testemunhas `UNRESOLVED`, `movement_enabled=false`, `replacement_required=true`. Instalação dos quatro ascensores não certificada. Datum/implantação absoluta e interface inferior de aproximadamente3,857m com o terreno seguem `NEEDS_REVIEW`; não foi deslocado o elevador ou deformada Salvador para esconder isso. Produção B30 inalterada; nenhuma exportação/promoção.

Estrutura dimensional **aprovada somente para os controles listados**. Acabamento/fachadas permanecem fora do escopo. As ligações verticais técnicas, escadas executadas e seções ausentes precisam de controle documental específico antes de serem consideradas definitivas; preservar essas distinções no próximo passe de modelagem.
''',encoding='utf8')
provpath=root/'world/data-provenance.json'; prov=json.loads(provpath.read_text())
resource={'resource_id':'derived:lacerda-structural-floors-b101','provider':'Bay of All Saints / modelagem derivada SUCOP2023',
          'dataset':'Pisos14/15, níveis23 e registro relativo B99; manifesto dimensional da estrutura existente',
          'capture_date':'2026-10-08','bounds':None,'raw_files':[],
          'derived_files':[r['file'],doc.relative_to(root).as_posix(),(out/'controls.json').relative_to(root).as_posix(),(out/'dimensions.json').relative_to(root).as_posix(),(out/'application.json').relative_to(root).as_posix(),(out/'validation.json').relative_to(root).as_posix()],
          'derived_objects':[v['object'] for v in r['added']],'usage_class':'PENDENTE_VERIFICACAO',
          'release_status':'REPLACE_BEFORE_RELEASE','purpose':'Modelagem dos pisos documentais e controle dimensional relativo; não engenharia civil/as-built ou instalação',
          'dependencies':cfg['source_ids']+['derived:lacerda-basement-envelope-b99'],'kind':'geometry',
          'accuracy':cfg['accuracy'],'replacement_required':True}
assert set(resource['dependencies'])<={v['resource_id'] for v in prov['resources']}
old=next((v for v in prov['resources'] if v['resource_id']==resource['resource_id']),None)
if old:old.update(resource)
else:prov['resources'].append(resource)
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary=f'''## 08/10/2026 — B101 ativa: pavimentos e controle dimensional estrutural

B100 preservada; três lajes acrescentadas nas cotas documentais−9,74/−19,85, com recorte de escada da15 livre. B101 aplicada/salva/reaberta na única janela9876/PID{r['pid']}. {q['objects_checked']} componentes conferidos,620 anteriores intactos;22 sondagens de piso/25 de escada,13 níveis existentes e quatro contornos conferidos. Manifesto dimensions.json consolida controles; seções e fechamentos das salas03/instalação/implantação não certificados. Não fabricar paredes usando alturas desconhecidas nem reescalar pela área útil nominal. Mapas/terreno/torres/passarela/B82/27 testemunhas/B76–B100/SSOT intactos, movimento falso, produção B30 inalterada. Relatório docs/LACERDA_STRUCTURAL_DIMENSIONS_B101_2026-10-08.md. Mapa completo aberto e sem alteração pendente; acabamento fora do escopo.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
    path=root/'docs'/name; s=path.read_text(encoding='utf8')
    if not s.startswith(summary):path.write_text(summary+s,encoding='utf8')
print(json.dumps({'revision':'B101','report':doc.relative_to(root).as_posix(),'relative_dimensions':'PASS_FOR_LISTED_CONTROLS','complete_model_certified':False},ensure_ascii=False))
