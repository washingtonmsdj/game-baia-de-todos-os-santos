# Lacerda — encontros do corpo superior B96 — 07/10/2026

B96 finalizada ao vivo, salva e reaberta na mesma janela PID 16912/MCP9876, cena `SALVADOR | ESBOCO OFICIAL`. Nove meshes alteradas; nenhum objeto novo, reparent ou alteração da geografia. B76–B95 preservadas. Fonte ativa: `blender/salvador_lacerda_r30b96_encontro_corpo_cobertura.blend`. SHA-256 `6cc7438c0462f6c5e86108d818e43dcfdcd6f4b3adf0dbf300b01013eafd1d1b`.

## Correções e origem

- A face posterior usava a base legada 75,10 no mapper B88 que tomou 75,20 como origem do corpo elevado. O resultado ficou 0,08333m abaixo das outras faces e dos controles verticais. Parede e seis caixilhos foram reconciliados juntos: delta local X 0.17840283m, Z 0.08333588m, sem mudar tamanho ou relações das janelas. A quina oeste da parede agora pertence ao envelope do edifício, em vez de extrapolar a cobertura pela metade da espessura.
- **Z documental:** prancha23 informa cobertura da passarela +4,00 e cobertura do edifício +14,00. A face inferior da cobertura fica +13,75 pela espessura herdada/candidata 0,25m. As três paredes terminam nessa face inferior; o topo externo da cobertura permanece +14,00.
- **XY:** a quina vem do envelope B86 já usado por cobertura/alas. A reconciliação horizontal é `ADAPT_LOCAL / CANDIDATE_ENVELOPE_CONTINUITY`, para fechar a interface entre peças. Não é novo controle as-built, registro geográfico aceito ou dimensão levantada.
- A inspeção visual detectou faces exteriores coincidentes nos cantos e na faixa do teto, apesar de cada mesh ser manifold. A posterior foi recortada nos limites internos das laterais e na face inferior da cobertura; as duas laterais também terminam sob a cobertura. Juntas de contato entre peças foram preservadas, sem acrescentar volumes para esconder a cintilação. Janela e passagem não foram tampadas. Espessuras continuam candidatas.

## Conferência

- 603 componentes comparados às assinaturas; 391 visíveis sem faces degeneradas, arestas não manifold, winding inconsistente ou faces duplicadas internas no escopo auditado.
- Seis janelas mantêm a mesma translação comum e a mesma topologia; máximo erro numérico 0.00000210m.
- Trinta sondagens sobre a espessura da posterior confirmam cobertura real acima dela. Duas junções laterais conferidas por contato e raio físico. Tangência é `EXPECTED_CONTACT`, não defeito automático.
- 130 sondagens de piso/teto dos encontros, 60 de parede e 15 de portal. Os fechamentos B94/B95 permanecem aprovados em seu escopo local. Isso não aprova o percurso completo, CCD da cabine ou controller.
- Terrain, SSOT e GAMEPLAY_PROXY B82 intactos. Poço, cabine, guias históricas, demais regiões e decoração não alterados. Prova visual real: `artifacts/lacerda-live-diagnostic/b96-rear-roof.png`; mapa completo: `b96-map.png`.
- A janela terminou com terreno visível, `local_view=false`, `unsaved_changes=false`. A sessão inicialmente não salva foi preservada em `artifacts/blender-sessions/salvador_lacerda_r30b95_limites_circulacoes_superiores_sessao_20261007T212923Z.blend`. Os 603 componentes comparados antes da modelagem não apresentavam diferença geométrica contra B95; a recuperação não foi descartada por essa constatação.

## Espaço e preservação

Removido somente o backup automático pré-checkpoint final B92 após comparar geometria/transform/material de 542 componentes com a B92 oficial: zero diferenças. A B92 oficial permanece intacta; não houve alegação de identidade binária de todos os metadados. Evidência: `backup-comparison.json`/`space-recovery.json`.

Checkpoints de B96 em andamento foram substituídos após validar seus sucessores. O último backup temporário, se removido por espaço, tem hash e motivo em `checkpoint-cleanup.json`; ele ainda continha a sobreposição de topo corrigida. B95, B96 final e cópia de recuperação permanecem disponíveis. Não apagar revisões oficiais ou evidências.

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`; `movement_enabled = false`; `27 testemunhas B80 = UNRESOLVED / PRESERVED`; `GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`; `EXPANDED_MAP = GREYBOX`; `production_ready = false`.

Antes/depois e controles: `docs/reports/blender/lacerda-body-b96/{before,mutation-journal,application,joint-finalization,roof-side-finalization,validation,presentation}.json`. Implantação absoluta, acesso inferior ao terreno e guardas/interiores continuam candidatos ou pendentes conforme B93–B95; não foram escondidos com geometria fictícia.

Próximo cluster de modelagem: acesso superior e guardas dos vestíbulos, distinguindo áreas intencionalmente abertas de defeitos, antes de layout fino de janelas ou expansão territorial.
