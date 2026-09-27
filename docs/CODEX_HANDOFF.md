# Handoff do Codex — MVP no Blender

## Objetivo

Continuar a cena do MVP de Salvador sem exigir coordenação manual repetida.

A cena de trabalho do Blender deve ser fornecida localmente ao Codex. O GitHub é a fonte de verdade para scripts de automação, notas de revisão, proveniência de dados e instruções de validação.

## Contexto atual da cena

A cena-fonte analisada continha aproximadamente:

- 4.617 objetos;
- 4.097 datablocks de mesh;
- 135 materiais;
- 30 coleções;
- 412 curvas;
- 54 câmeras;
- 1 luz explícita;
- milhares de nomes com sufixos automáticos como `.001`, `.002` etc.

A cena já inclui várias revisões históricas ao redor do Elevador Lacerda, Mercado Modelo, Praça Cairu, terreno, vias, acessos e interiores jogáveis.

Não tratar a cena como um blockout novo.

## Ordem de aplicação

Ao começar pela cena original analisada:

1. executar `tools/blender/r27_qa_review.py`;
2. abrir e validar o `_r27.blend` resultante;
3. executar `tools/blender/r28_gameplay_export.py` sobre a cena válida mais recente;
4. abrir e validar o `_r28.blend`;
5. ler o datablock `R28_PERFORMANCE_AUDIT`;
6. executar `tools/blender/r29_optimization.py` **sem** `--apply-exact`;
7. abrir o `_r29.blend` de auditoria e ler:
   - `R29_OPTIMIZATION_REPORT`;
   - `R29_EXACT_DUPLICATE_CANDIDATES`;
   - `R29_LOD_COLLISION_CANDIDATES`;
8. confirmar que nenhum `HERO` ou `GAMEPLAY` está em grupo de deduplicação automática;
9. voltar ao `_r28.blend` validado e executar:

```bash
blender cena_r28.blend --python tools/blender/r29_optimization.py -- --apply-exact
```

10. reabrir e validar o `_r29.blend` aplicado;
11. exportar os relatórios reais da cena com `tools/blender/export_revision_reports.py`;
12. registrar métricas reais antes/depois;
13. só então iniciar a R30 visual.

Se a cena local já estiver em uma revisão validada posterior, pular as etapas anteriores conforme necessário, mas nunca aplicar uma revisão destrutiva sobre um arquivo cuja origem não esteja preservada.

## Aleph e dados geográficos

O projeto **Aleph** é uma ferramenta externa registrada para aquisição e organização de referência geográfica.

Referência pinada atualmente:

- repositório: `Belluxx/Aleph`;
- commit analisado: `d24c61507481a91a0dd6afac4f97626a4e5ea780`;
- licença do software: MIT.

Consultar antes de usar qualquer captura:

- `docs/references/ALEPH.md`;
- `docs/DATA_PROVENANCE.md`;
- `docs/references/SOURCE_REGISTRY.json`.

### Ao encontrar uma pasta de captura Aleph local

Antes de importar qualquer dado no Blender, executar:

```bash
python tools/aleph/inspect_capture.py CAMINHO_DA_CAPTURA \
  --output docs/reports/aleph/AREA_ID/source_summary.json
```

No Windows o comando pode ser executado em uma única linha.

Depois:

1. preservar o `manifest.json` original junto aos dados locais;
2. revisar `source_summary.json`;
3. confirmar o commit do Aleph usado na captura;
4. confirmar bounds e sistema de coordenadas;
5. importar OSM apenas como referência/proxy inicialmente;
6. manter terreno de origem incerta como referência até a licença da fonte efetiva ser confirmada;
7. não importar Google Satellite/Street View obtidos pelo Aleph como assets de produção;
8. registrar a transformação geográfica → coordenadas locais do Blender antes de expandir o mapa.

### Política de uso resumida

- **OSM/Geofabrik:** permitido no pipeline com atribuição/obrigações ODbL registradas;
- **terrain.tif do Aleph:** útil tecnicamente, mas a origem/licença efetiva do DEM deve ser confirmada antes de distribuição;
- **Google Satellite via Aleph:** `PROIBIDO_PRODUCAO`;
- **Google Street View via Aleph:** `PROIBIDO_PRODUCAO`.

A licença MIT do software Aleph não concede direitos sobre os dados obtidos de serviços externos.

## Validação obrigatória após cada revisão

O Codex deve verificar todos os pontos abaixo antes de considerar uma revisão bem-sucedida:

- o `.blend` de origem continua existindo e não foi sobrescrito;
- o novo arquivo de revisão foi criado;
- o Blender consegue reabrir o novo arquivo;
- as coleções e datablocks de texto esperados existem;
- não há exceções Python no console/log do Blender;
- a contagem total de objetos continua plausível;
- nenhuma exclusão em massa ocorreu;
- a geometria dos principais marcos continua presente;
- a rota de gameplay afetada pode ser inspecionada visualmente.

## Corredor jogável atual

A rota atual do MVP é:

**entrada da Cidade Alta → passarela superior → cabines do Elevador Lacerda → saída inferior → Cidade Baixa → Praça Cairu → Mercado Modelo**

As coordenadas usadas pelos guias R27/R28 vêm de checkpoints já registrados na própria cena. Elas são guias de design e não dados topográficos certificados.

## R29 — regras de segurança

A R29 só pode relinkar meshes quando a equivalência for comprovada pelo conteúdo avaliado pelo fingerprint.

Não otimizar automaticamente quando houver dúvida sobre:

- topologia;
- UVs;
- slots e ordem de materiais;
- atributos;
- shape keys;
- custom properties;
- animation data;
- metadados de gameplay;
- classificação R28.

Objetos `HERO` e `GAMEPLAY` ficam protegidos da deduplicação automática.

Não usar nomes parecidos de objetos como prova de equivalência.

## Objetivo da R30

A R30 deve transformar o MVP de maneira visualmente perceptível sem perder o controle técnico conquistado nas revisões anteriores.

Prioridades:

1. leitura de ruas e calçadas;
2. composição da Praça Cairu;
3. entorno imediato do Mercado Modelo;
4. conexão visual e jogável entre a saída inferior do Elevador Lacerda e a Cidade Baixa;
5. mobiliário urbano modular;
6. vegetação controlada;
7. iluminação e atmosfera de preview;
8. corredores claros de tráfego e pedestres;
9. cobertura, atalhos, becos, entradas e pequenas rotas alternativas;
10. preparação visual para expansão futura em direção ao Comércio e Centro Histórico.

A R30 deve consultar `R29_LOD_COLLISION_CANDIDATES` antes de adicionar detalhes pesados em objetos ou áreas de alto custo.

## Idioma da documentação

O nome do jogo permanece **Bay of All Saints**.

Toda a documentação, relatórios, handoffs e notas de desenvolvimento devem ser escritos em **português**. Nomes próprios reais de Salvador permanecem com sua grafia oficial.

Identificadores técnicos históricos como `allsaints_*` podem permanecer por compatibilidade com metadados já gravados no `.blend`.
