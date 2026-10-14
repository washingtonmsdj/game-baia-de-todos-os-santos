# Lacerda — estrutura e malhas B91/B92 — 07/10/2026

A **B92** é a candidata de modelagem ativa, salva e reaberta na mesma janela Blender PID 16912, MCP 9876, cena `SALVADOR | ESBOCO OFICIAL`. B76–B91 preservadas. SSOT, terreno, proxy B82 e gates históricos mantidos. Nenhum export de produção ou alteração na expansão.

## Correção da causa raiz

A seleção da B88 ignorou componentes da coleção `08 ELEVADOR E TERRENO / dimensoes calibradas`. O nome da passarela dizia 28,71 m, mas sua malha ainda media cerca de **55,54 m**. Esses nomes históricos não são cotas confiáveis.

**B91:** laje da ponte reconstruída pelo mesmo contorno CAD do piso paginado; contato com intradorso e acabamento. Casca da torre contínua, apoio alargado da galeria e limpeza de malha. Removidas 226 faces internas opostas; soldadas as bordas degeneradas de três paredes, sem preencher abertura arquitetônica. Cobertura redundante preservada como referência. Relatório completo: `docs/LACERDA_MESH_STRUCTURE_B91_2026-10-07.md`.

**B92:** cobertura da passarela usa exatamente o mesmo contorno CAD da ponte, topo **+4,00 m**, conforme prancha 23. Os 18 montantes e duas vigas laterais do esboço antigo foram identificados como representação substituída: a nova ponte já tem caixilhos/estrutura longitudinal. Seus meshes/transforms permanecem intactos, com `SUPERSEDED_REFERENCE`, fora da apresentação ativa. A plataforma superior da implantação antiga também foi preservada como referência substituída; ela estava flutuando ao lado da galeria atual. Não foram movidos para encaixar nem apagados.

O binding `B82 / upper_walkway` cita a laje histórica, mas o proxy continua independente. Seus metadados foram comparados com a B90: **0 diferenças**. Não foi promovido nem ajustado para a arquitetura candidata.

## Validação real

- 542 componentes comparados com assinaturas após reabertura; 387 visíveis auditados com zero faces degeneradas, arestas não manifold, winding inconsistente ou faces duplicadas internas.
- Cobertura e laje da ponte possuem o mesmo contorno XY. Topo da cobertura acima do piso: 4.00000000 m.
- Quatro encontros estruturais explicitamente conferidos, gap numérico máximo 0.00000000 m: intradorso/laje, laje/piso, núcleo/capeamento e consolo/galeria.
- Vinte componentes da ponte e a plataforma superior substituída conferidos geometricamente intactos e preservados como referência. B91 permanece preservada como revisão própria, com QA de 520 componentes. O checkpoint anterior de apresentação B92 foi preservado em `blender/salvador_lacerda_r30b92_ponte_estrutural_consolidada.blend1`, hash `bad73e6c5e114862c4da284f943b91bf7339fb29aca82100f520e9d0db342112`.
- QA local de malha/contatos. **Não é auditoria integral de todas as auto-interseções do edifício**, aprovação de controller, CCD, layout interno ou fidelidade milimétrica.

## Aproximações e pendências explícitas

Apresentação final conferida em `docs/reports/blender/lacerda-bridge-b92/presentation-map.json`: B92 na mesma cena/janela, mapa completo, `local_view: false`, terreno visível e `unsaved_changes: false`. Capturas reais: `artifacts/lacerda-live-diagnostic/b92-exterior.png` (isolamento local de inspeção) e `b92-map.png` (mapa completo). Não são testes em engine nem outra cena.

Contornos documentais derivados das pranchas 17/23 não constituem registro geográfico absoluto aceito. O consolo possui forma alargada comprovada nas referências, mas sua altura/perfil sem cota e espessuras de montagem continuam candidatos declarados, `replacement_required: true`. Não apresentá-los como medidas as-built.

O inventário adicional encontrou 85 componentes legados/controles visíveis. Só os 20 componentes da ponte e a plataforma superior com substituição inequívoca foram retirados da camada ativa nesta etapa; a cobertura foi corrigida. Outros componentes — em especial fachada inferior, marquises e peças no antigo datum inferior — continuam como pendência de reconciliação do conjunto com o mapa. Não ocultar essas discrepâncias ajustando terreno ou declarando o gate resolvido.

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`

`movement_enabled = false`

`27 testemunhas B80 = UNRESOLVED / PRESERVED`

`GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`

`ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`

`INTERIOR_LAYOUT = NOT_VALIDATED`

`EXPANDED_MAP = GREYBOX`

`production_ready = false`

Próxima causa estrutural identificada: conciliar, com controles independentes, a fachada inferior/implantação do conjunto com os pisos relativos do projeto e terreno SSOT. Não investigar novamente cabine/poço por causa desta limpeza de malha. Não começar janelas novas ou decoração antes dessa reconciliação.

Fonte ativa: `blender/salvador_lacerda_r30b92_ponte_estrutural_consolidada.blend`. SHA-256: `8ea3ce94c86aca60e15dc2dab42e2100436ecc6e2bf05347732f137306e41514`.
Fonte canônica: `blender-revisions.json#/authoring_source`, também `validation_source`. Produção B30 e proxy B82 permanecem separados.
