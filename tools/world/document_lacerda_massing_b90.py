"""Registra a estrutura aplicada, sem promover projeto/as-built/implantação."""
import json,hashlib,math
from pathlib import Path
root=Path(__file__).resolve().parents[2]
read=lambda p:json.loads((root/p).read_text(encoding='utf8'))
r88=read('docs/reports/blender/lacerda-massing-b88/application.json');r89=read('docs/reports/blender/lacerda-massing-b89/application.json');r90=read('docs/reports/blender/lacerda-massing-b90/application.json');qa=read('docs/reports/blender/lacerda-massing-b90/validation.json');cfg=read('docs/reports/blender/lacerda-massing-b88/architectural-controls.json')
assert qa['reopened'] and r90['reopened'] and qa['objects_checked']==518
with (root/r90['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r90['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==cfg['ssot_sha256']
text=f'''# Lacerda — estrutura exterior B88–B90 — 07/10/2026

A candidata de modelagem ativa é **B90**, salva e reaberta na mesma janela Blender PID {r90['pid']}, MCP 9876, cena `SALVADOR | ESBOCO OFICIAL`. Esta rodada substitui as proporções genéricas da B87 por uma estrutura arquitetônica relativa às pranchas SUCOP 12, 17 e 23. Não constitui certificação da instalação ou da implantação geográfica.

## Alterações reais

- B88: {len(r88['changes'])} componentes e quatro novos elementos estruturais. Piso/galeria da torre nova, ponte livre, envoltória da torre nova, corpo da torre antiga, alas sob o edifício superior, piso e limites inferiores/túnel derivados dos contornos vetoriais documentais. Referências históricas e acabamentos substituídos continuam preservados; não apagar para retomar layout.
- B89: {len(r89['changes'])} componentes. Abertura galeria/ponte identificada pelos mesmos endpoints CAD, independente da ordem dos vértices. Piso inferior e corpos estruturais usam agora a diferença **59,01 m** entre os pisos arquitetônicos. Não reinterpretar isso como parada de cabine, soleira instalada ou solução do offset B80.
- B90: cinco componentes. Cobertura do edifício superior em **+14,00 m** e platibandas em **+15,40 m**, cotas impressas na prancha 23. A cobertura da passarela permanece **+4,00 m**.

| Relação | B87 | Estrutura atual |
|---|---:|---:|
| Ponte livre | aproximadamente 41,2 m, alinhada artificialmente | borda norte {cfg['diagnostic']['bridge_free_north_length_m']:.2f} m; borda sul {cfg['diagnostic']['bridge_free_south_length_m']:.2f} m |
| Ângulo relativo torre nova / ponte | alinhamento genérico | {abs(cfg['diagnostic']['relative_tower_bridge_angle_deg']):.2f}° derivado dos segmentos CAD |
| Apoio antigo junto à encosta | volume genérico de aproximadamente 15,88 × 10,96 m em toda a altura | contorno do núcleo antigo separado das alas do edifício e das circulações |
| Piso inferior | retângulo genérico 8,80 × 10,20 m, sem ligação arquitetônica completa | envoltória inferior e corredor/túnel documentais |
| Saguão/circulações superiores | contorno B86, com apoios/distância ainda genéricos | contorno preservado e reconciliado com ponte/torres; abertura do núcleo antigo separada do chão |

## Origem e transformação

`world/geographic-reference.json` permanece canônico e byte a byte intacto: `{cfg['ssot_sha256']}`.

A transformação documental deriva de três cotas impressas da prancha 17: 5,20 / 1,99 / 2,20 m. Escala nominal resultante: {cfg['pdf_units_per_m']:.6f} unidades PDF por metro. Maior residual dessas cotas: {max(abs(c['residual_m']) for c in cfg['scale_controls']):.4f} m. Este residual avalia a consistência do documento, não precisão de levantamento.

Ponto de origem documental PDF `{cfg['drawing_to_architecture']['origin_pdf']}` associado ao acesso superior local `[5.5, 0]` no frame histórico da cena. Os vértices originais, fontes, hashes e transformação estão em `docs/reports/blender/lacerda-massing-b88/architectural-controls.json`.

**Registro geográfico independente ainda não aceito.** A forma e a relação espacial do conjunto vêm do documento; sua implantação absoluta no terreno continua candidata. Não foram deslocados terreno, Cidade Alta/Baixa, Mercado, Prefeitura, Palácio, vias ou SSOT para esconder discrepâncias. A geometria inferior agora está no datum relativo do projeto: Z {r89['lower_architecture_floor_scene']:.6f}; terreno e contexto mantêm seus valores anteriores. A interface com o terreno/rua precisa de reconciliação independente e não está aprovada para circulação.

## Espaço interno e limites

Os pisos são volumes fechados com recortes dos núcleos das torres. A circulação possui espaço geométrico separado dos corpos dos poços; nenhuma cabine foi redimensionada para encaixar.

Área total de envoltória não equivale às áreas de compartimentos impressas. O salão superior de 117,50 m² não representa todas as circulações. O saguão inferior de 265,56 m² e o túnel de 90,99 m² ainda precisam de subdivisão/controle do layout e do trecho técnico junto à rocha. Não declarar essas áreas internas verificadas pela simples área dos polígonos desta rodada.

Espessuras de chapa/parede e elementos de acabamento que não possuem controle próprio continuam aproximações herdadas/autorais. O layout das janelas, portas internas, equipamentos e divisões não foi certificado. Contorno esquemático da torre não comprova seção útil do poço ou cabine atual.

## Verificação efetiva

- {qa['objects_checked']} componentes conferidos contra assinaturas persistidas; zero faces de área zero. Pisos estruturais controlados têm arestas manifold.
- Bounds XY dos quatro pisos/galeria/ponte conferidos contra os contornos CAD; maior residual {max(r['cad_bound_residual_m'] for r in qa['dimension_checks']):.8f} m, somente numérico.
- Diferença real entre planos de piso: {qa['document_relative_levels']['upper_minus_lower_m']:.8f} m; cobertura superior +{qa['document_relative_levels']['building_roof_above_upper_m']:.6f}; platibanda +{qa['document_relative_levels']['building_parapet_above_upper_m']:.6f}; cobertura da galeria +{qa['document_relative_levels']['gallery_roof_above_upper_m']:.6f}.
- Capturas de planta e exterior são da mesma cena/janela, com isolamento local apenas para comparação. A revisão final abre o **mapa completo**, com terreno visível e sem `local_view`.
- B76–B89, proxy B82, SSOT, terreno e 27 testemunhas históricas preservados. Nenhum export ou promoção para produção.
- Colisores derivados afetados mantêm seus bindings, mas a validação anterior foi explicitamente invalidada. Não representam controller aprovado na nova arquitetura. Não houve sweep/CCD novo nesta rodada de modelagem.

## Estados e sequência

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`

`movement_enabled = false`

`GAMEPLAY_PROXY_B82 = PRESERVED / APPROXIMATE / replacement_required: true`

`ARCHITECTURAL_RELATIVE_STRUCTURE = DOCUMENT_DERIVED_LOCAL_QA`

`ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`

`INTERIOR_LAYOUT = NOT_VALIDATED`

`EXPANDED_MAP = GREYBOX`

Próxima etapa necessária antes de aprovar a estrutura dentro do mapa: reconciliar implantação absoluta e datum de pisos com controles físicos/geográficos independentes, incluindo interfaces Cidade Alta/escarpa e saguão inferior/rua. Depois ajustar divisões, janelas e distribuição dos quatro ascensores. Os gates SEMOB/Otis continuam como dívida conhecida; não foram reabertos nem declarados resolvidos.

Fonte ativa: `{r90['file']}`. SHA-256: `{r90['sha256']}`.
'''
(root/'docs/LACERDA_ARCHITECTURAL_STRUCTURE_B90_2026-10-07.md').write_text(text,encoding='utf8')
prov_path=root/'world/data-provenance.json';prov=read('world/data-provenance.json')
for n,r,deps in [(88,r88,['derived:lacerda-upper-layout-b86','source:lacerda-issue22-sucop-12','source:lacerda-issue22-sucop-17','source:lacerda-issue22-sucop-23']),(89,r89,['derived:lacerda-massing-b88','source:lacerda-issue22-sucop-12','source:lacerda-issue22-sucop-23']),(90,r90,['derived:lacerda-massing-b89','source:lacerda-issue22-sucop-23'])]:
    resource={'resource_id':f'derived:lacerda-massing-b{n}','provider':'Bay of All Saints / modelagem autoral derivada SUCOP','dataset':'Estrutura relativa/cotas documentais do Elevador Lacerda','capture_date':'2026-10-07','bounds':None,'raw_files':[],'derived_files':[r['file'],f'docs/reports/blender/lacerda-massing-b{n}/application.json'],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Modelagem estrutural do conjunto, sem certificar implantação, layout ou instalação atual','dependencies':deps,'kind':'geometry','generation_status':'APPLIED_DOCUMENT_RELATIVE_QA','accuracy':'PROJECT_REFERENCE_DERIVED_PARTIAL','replacement_required':True}
    existing=next((v for v in prov['resources'] if v['resource_id']==resource['resource_id']),None)
    if existing:existing.update(resource)
    else:prov['resources'].append(resource)
ids={r['resource_id'] for r in prov['resources']}
assert all(d in ids for r in prov['resources'] if r['resource_id'].startswith('derived:lacerda-massing-b') for d in r['dependencies'])
prov_path.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary='''## 07/10/2026 — B90 ativa: estrutura arquitetônica relativa SUCOP

B88–B90 corrigem ponte livre, orientação das torres, separação núcleo antigo/alas do edifício, envoltórias dos pisos superior/inferior e túnel, abertura galeria/ponte e cotas exteriores impressas. B90 salva/reaberta na mesma janela MCP 9876; mapa completo visível, sem isolamento local. QA: 518 componentes, zero faces de área zero; cotas relativas 59,01 / +4,00 / +14,00 / +15,40 m. Não equivale a implantação geográfica, layout interno, poço ou controller certificados. Registro absoluto/datum inferior no mapa NEEDS_REVIEW; terreno/SSOT não deformados para encaixar o asset. Bindings físicos preservados mas validações afetadas invalidadas; movement_enabled false, 27 testemunhas e BLOCKED_EXTERNAL_EVIDENCE preservados. B76–B89 e proxy B82 intactos; produção B30 inalterada. Fonte authoring_source/validation_source B90. Relatório: docs/LACERDA_ARCHITECTURAL_STRUCTURE_B90_2026-10-07.md. Próximo passo: reconciliação da implantação/interface com terreno antes de layout/janelas.

'''
for p in ('docs/PROJECT_STATUS.md','docs/CODEX_HANDOFF.md','docs/CODEX_STRUCTURE_HANDOFF.md'):
    path=root/p;previous=path.read_text(encoding='utf8');path.write_text(summary+previous,encoding='utf8')
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=read('world/areas/mvp-centro-lacerda/corridor-slice.json')
profile.setdefault('revision_history',[]).append({'revision':'R30B.90','scope':'estrutura arquitetônica documental; instalação/implantação/controller não aprovados','movement_enabled':False,'evidence':'docs/LACERDA_ARCHITECTURAL_STRUCTURE_B90_2026-10-07.md'})
profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'active_revision':'B90','objects_checked':qa['objects_checked'],'provenance_registered':[88,89,90],'geographic_ssot_preserved':True,'production_ready':False}))
