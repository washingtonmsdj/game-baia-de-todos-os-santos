# Handoff do Codex — MVP no Blender

## Objetivo

Continuar a cena do MVP de Salvador sem exigir coordenação manual repetida.

A cena de trabalho do Blender deve ser fornecida localmente ao Codex. O GitHub será a fonte de verdade para scripts de automação, notas de revisão e instruções de validação.

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
5. ler o datablock de texto `R28_PERFORMANCE_AUDIT` dentro do Blender antes de otimizar;
6. usar a auditoria da R28 para orientar a R29; não adivinhar quais objetos repetidos podem virar instâncias.

Se a cena local já estiver na R27 ou R28, pular as revisões anteriores conforme necessário.

## Validação obrigatória após cada revisão

O Codex deve verificar todos os pontos abaixo antes de considerar uma revisão bem-sucedida:

- o `.blend` de origem continua existindo e não foi sobrescrito;
- o novo arquivo de revisão foi criado;
- o Blender consegue reabrir o novo arquivo;
- as coleções geradas pela revisão existem;
- os datablocks de texto gerados existem;
- não há exceções Python no console/log do Blender;
- a contagem total de objetos continua plausível;
- nenhuma exclusão em massa ocorreu;
- a geometria dos principais marcos continua presente;
- a rota de gameplay afetada pode ser inspecionada visualmente.

## Corredor jogável atual

A rota atual do MVP é:

**entrada da Cidade Alta → passarela superior → cabines do Elevador Lacerda → saída inferior → Cidade Baixa → Praça Cairu → Mercado Modelo**

As coordenadas usadas pelos guias R27/R28 vêm de checkpoints já registrados na própria cena. Elas são guias de design e não dados topográficos certificados.

## Objetivo da R29

A R29 deve ser um passe controlado de performance.

Ordem de prioridade:

1. identificar props/meshes realmente idênticos e repetidos;
2. criar instâncias/vínculos somente quando a equivalência estiver comprovada;
3. preservar transforms e vínculo com coleções;
4. evitar alterar objetos `HERO` ou `GAMEPLAY` sem validação explícita;
5. gerar candidatos simplificados de colisão em vez de substituir meshes de render;
6. identificar meshes de alto custo dos marcos principais para trabalho manual de LOD;
7. propor limites de chunks para ruas e calçadas;
8. produzir métricas antes/depois;
9. salvar uma nova revisão `_r29.blend`.

## Restrições de segurança da R29

Não criar instâncias nem unir objetos automaticamente quando qualquer um dos itens abaixo for diferente ou incerto:

- topologia de vértices/arestas/polígonos;
- dados UV;
- slots e ordem de materiais;
- cores/atributos customizados;
- shape keys;
- propriedades customizadas do mesh que afetem o fluxo;
- modifiers específicos do objeto dependentes de dados únicos;
- metadados de gameplay;
- requisitos de animação/deformação.

Não otimizar apenas com base no nome do objeto.

## Trabalho visual/construção de mundo após a otimização

Quando o MVP estiver tecnicamente estável, priorizar melhorias perceptíveis:

- leitura de ruas e calçadas;
- composição da Praça Cairu;
- entorno do Mercado Modelo;
- transições entre Cidade Alta e Cidade Baixa;
- qualidade das silhuetas dos marcos arquitetônicos;
- distribuição de vegetação;
- mobiliário urbano;
- iluminação e atmosfera;
- espaço para tráfego e pedestres;
- cobertura, atalhos, becos, entradas e escolhas de travessia para gameplay;
- limites preparados para expansão aos distritos adjacentes.

## Idioma da documentação

O nome do jogo permanece **Bay of All Saints**.

Toda a documentação, relatórios, handoffs e notas de desenvolvimento devem ser escritos em **português**. Nomes próprios reais de Salvador permanecem com sua grafia oficial.
