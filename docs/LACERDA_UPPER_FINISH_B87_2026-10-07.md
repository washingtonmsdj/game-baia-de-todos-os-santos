# B87 — modelagem do fechamento e piso superior

## Resultado aplicado

**B87 salva e reaberta na única janela Blender**, PID 16912, porta MCP 9876, cena SALVADOR | ESBOCO OFICIAL. Fonte de autoria/validação registrada: `blender/salvador_lacerda_r30b87_pisos_e_fechamentos_superiores.blend`. SHA-256: `b3435e0dd500bd6a95f28d3511008ad262bb4f9ce6ce483cf4115524346d8a8c`.

B86 preservada, SHA-256 `5add1823f0d2cebb9c2c3bd33f59b6aead145a7929787dc88137be3ef173fb48`. B76–B85, SSOT, proxy B82 e gates históricos também preservados. Não houve exportação/promoção de produção.

## Modelagem

1. **Piso do saguão reconciliado com acabamento da ponte**: topo 70.044998 → 70.123009, diferença 78.011 mm. Topo dos dois colisores explicitamente vinculados recebeu a mesma correção. A cota relativa 0,00 da prancha 17 é a evidência independente de continuidade; o valor de acabamento foi obtido da malha existente da ponte, não da cápsula. A origem/datum global permanece candidata. Nenhum Z global ou terreno foi alterado.
2. **Duas paredes laterais do saguão reconstruídas com faixa de vidro**. Foram substituídas as três aberturas genéricas largas em cada lateral por envidraçamento contínuo com 222 painéis, montantes e travessas. Materiais de vidro, esquadria e reboco foram reutilizados da passarela/retornos existentes. Não existe parede opaca atrás da faixa de vidro. O contorno principal continua o derivado da B86/prancha 17.
3. **Dois colisores simples de parede envidraçada**, vinculados às respectivas fontes, impedem atravessar o vidro. A geometria detalhada inteira não foi duplicada como collider. Os bindings são únicos e explícitos.
4. **Piso auxiliar NAV legado preservado como referência substituída**, fora da representação física/visual ativa. Seu collider já estava desabilitado na B80 e substituído pelo piso real da ponte; isso está comprovado no contrato e em `reconcile_upper_ground_b80.py`. Não foi removido um obstáculo real para liberar o teste. A função obsoleta ainda constava na apresentação da B86, atravessando o salão ampliado.
5. Seis peitoris vinculados às antigas três aberturas foram preservados como referência substituída. O fechamento novo inclui seus próprios encontros inferiores, evitando empilhar duas soluções visuais.

Nenhuma torre, cabine, poço, guia de fila, soleira do elevador ou desembarque inferior foi alterado nesta revisão. Não há teleporte, recorte de poço ou passagem invisível.

## Referências e precisão

- SUCOP 17, projeto 2023: contorno superior, esquadrias das circulações e níveis relativos. `source:lacerda-issue22-sucop-17`.
- Fotografias externas fornecidas pelo usuário e catalogadas, em especial `source:lacerda-exterior-photo-139fa6c8d4d1`: padrão qualitativo de faixa envidraçada contínua junto ao saguão.
- Retornos B84 e materiais/travessas da passarela: compatibilidade visual do fechamento.

**A largura dos módulos de vidro e suas seções são aproximações autorais**, reaproveitando o padrão existente de 0,68 m e travessas, não medidas derivadas da perspectiva da foto. Altura do vidro segue a passarela existente, de aproximadamente 71,225 a 73,875 no referencial local. A planta não certifica essas dimensões executadas. O recurso mantém `APPROXIMATE`, `partial`, `replacement_required: true` e `REPLACE_BEFORE_RELEASE`.

## Conferência objetiva

- 15 componentes conferidos após reabertura: signatures persistidas e ausência de faces degeneradas.
- Paredes reconstruídas fechadas/manifold.
- Piso visual e dois derivados físicos na mesma altura final.
- Binding de cada novo collider único e preservando fonte.
- Hash da B86 e SSOT preservados.
- Aplicação confirmou preservação do terreno, dos 70 componentes do proxy B82 e dos objetos fora do escopo.
- Encontro ponte/saguão: Y -1.0: LOCAL_CLEAR, Y +0.0: LOCAL_CLEAR, Y +1.0: LOCAL_CLEAR.

O QA local cobre 4 m, com cápsula R 0,30 / H 1,80 / skin 0,015 / step máximo candidato 0,25. Usa apoio da esfera inferior em faces/arestas finitas e CCD Lipschitz entre amostras; classifica contato/convergência insuficiente sem forçar aprovação. **Não representa controller completo, gravidade/slide no percurso inteiro, poço ou ligação até o Mercado.** `full_route_approved: false`, `engine_verified: false`.

Arquivos: `docs/reports/blender/lacerda-finish-b87/application.json`, `validation.json`, `artifacts/lacerda-live-diagnostic/b87-upper-finish.png`. Scripts: `model_upper_finish_b87.py` e `validate_upper_finish_b87.py` em `automation/blender/`.

## Gates preservados

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`; 27 testemunhas B80 `UNRESOLVED`; movimento histórico falso. Proxy B82 permanece separado e aproximado. Implantação/orientação das torres, comprimento livre completo da ponte e distribuição física dos quatro equipamentos continuam pendentes. O progresso desta revisão não deve ser apresentado como reprodução integral/certificada do Elevador Lacerda.

Lapa, Campo da Pólvora, Dique e Fonte Nova não foram alterados. Não houve npm, build, testes amplos, commit/push ou exportação de produção.
