# Lacerda — limites e encontros superiores B95 — 07/10/2026

B95 aplicada e reaberta na mesma janela Blender PID 16912, MCP9876, cena `SALVADOR | ESBOCO OFICIAL`. B76–B94 preservadas; authoring_source/validation_source agora apontam explicitamente para B95. Produção e gameplay anteriores não promovidos.

## Causa comum e correções

O piso superior foi reconstruído pelo contorno documental na B88, mas partes da envoltória conservaram limites do layout anterior. A B94 adicionou os dois retornos corretos sem separar os seis componentes antigos sobrepostos.

- **Circulação norte:** a parede envidraçada avançava até X local 5,50. A planta17 separa a circulação da área `SAÍDA 20,10m²` na quina X 0.97828305, Y 7.93840742. A parede foi recortada nesse limite, sem esticar caixilhos, deslocar o piso ou fechar o acesso aberto.
- **Circulação sul:** o mesmo erro terminava em X 5,50; a quina documental da área `ENTRADA 15,17m²` está em X 0.87984681, Y -8.04954529. Recorte no limite correspondente. As áreas de entrada/saída não foram tratadas como buracos a preencher.
- **Verga ponte/saguão:** o elemento antigo ocupava Z73,50–75,00, ultrapassando a cobertura atual. Reconstruído pelos endpoints CAD do portal e pelas faces da cobertura: Z 73.87300873–74.12300873. Espessura 0,18m continua candidata/herdada. A passagem permanece livre abaixo da cobertura.
- **Retornos antigos:** seis componentes (duas paredes, dois lambris e dois rodapés) preservados sem alterar geometria, transform ou materiais, agora `SUPERSEDED_REFERENCE` fora da apresentação ativa. Sua substituição pelos retornos B94 é explícita. Nenhum objeto apagado, reparentado ou duplicado.

Três meshes alteradas, seis referências separadas e nenhum objeto novo. Controles relativos derivados da fonte catalogada SUCOP17 e do mesmo registro B88; não foi criado segundo SSOT. Não houve ajuste de datum, poço, cabine, terreno, ruas ou expansão.

## QA e limites da conclusão

- 603 componentes comparados às assinaturas B88–B95; 391 visíveis sem faces degeneradas, arestas não manifold, winding inconsistente ou faces duplicadas no escopo auditado.
- Limites das duas paredes conferidos contra as quinas documentais: maior residual numérico 0.00000012m. Mede consistência de aplicação, não precisão de levantamento.
- 100 sondagens de piso/teto, 60 de parede e 15 verificações do portal repetidas na B95, incluindo a nova verga. 12 contatos verticais sem gap acima da tolerância numérica.
- Auditoria anterior dos limites laterais da ponte e da galeria: 400 raios horizontais, 0 pontos sem hit. Essas envoltórias não foram alteradas nesta rodada. Essa amostragem não comprova toda a arquitetura nem toda a navegação.
- 6306 objetos protegidos durante a aplicação; 394 assinaturas geométricas do inventário local preservadas após reabrir, incluindo os seis componentes agora arquivados cuja visibilidade mudou deliberadamente.
- Terrain, SSOT e GAMEPLAY_PROXY B82 geometricamente intactos. Bindings históricos afetados preservados e invalidados explicitamente; não foram regenerados ou aprovados como controller.
- Arquivo salvo e reaberto, hash conferido. Vistas reais em `artifacts/lacerda-live-diagnostic/b95-*.png`; janela final com mapa completo, terreno visível e nenhuma alteração pendente.

Guardas dos acessos, subdivisões interiores e interface do piso inferior com o terreno não foram aprovadas nesta revisão. Não confundir abertura arquitetônica correta com percurso completo seguro para personagem. As dimensões de instalação continuam congeladas e a implantação absoluta mantém a pendência B93.

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`; `movement_enabled = false`; `27 testemunhas B80 = UNRESOLVED / PRESERVED`; `GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`; `EXPANDED_MAP = GREYBOX`; `production_ready = false`.

Fonte ativa: `blender/salvador_lacerda_r30b95_limites_circulacoes_superiores.blend`. SHA-256 `ea284af5adc6bc38c4c774962ef97af03d04a36c1f1a1f87f08d399b3cdfd662`.

Antes/depois, controles e hashes: `docs/reports/blender/lacerda-enclosure-b95/{before,mutation-journal,application,validation,presentation}.json`. Próxima modelagem: conferir os encontros exteriores do corpo antigo/alas e os limites dos acessos, sem usar acabamento para esconder divergência nem reabrir investigação dos ascensores.
