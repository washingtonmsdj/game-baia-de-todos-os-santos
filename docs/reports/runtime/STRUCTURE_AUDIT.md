# Auditoria de estrutura do MVP — 2026-09-29

## Problemas confirmados

- Documentação declarava R30A.12 enquanto o usuário selecionou R30A.11 no runtime.
- Arquivo, escala, coordenadas e medidas de veículo repetidos em módulos distintos.
- Exportação inicial excluía terreno/vias compartilhados com coleções GAMEPLAY.
- Runtime aplicava reflexão adicional ao GLB; cidade ficava espelhada.
- Pistas antigas ocultas eram usadas como fonte de apoio em vez do asfalto integrado.
- Chão de estúdio entrou no GLB do veículo e contaminou a normalização de escala.
- Existiam substitutos procedurais e caminhos de fallback para a cidade/ônibus.
- Carga monolítica, sem ciclo explícito de liberação de setores da GPU.
- Git LFS não abrangia claramente `.blend` de bibliotecas em subdiretórios.
- Ausência de LOD e custo elevado do tráfego detalhado.

## Correção deste ciclo

Contrato de produção versionado por área, hashes de fontes, perfil explícito de
execução, exportadores orientados pelo contrato, empacotamento estático por setores
preservando geometria/ancestrais e carregamento com verificação de integridade,
concorrência limitada e descarregamento. Fonte Blender preservada sem corte,
renomeação em massa, movimentação de prédios ou promoção automática da R30A.12.

O relatório gerado `package_world.json` registra a release efetivamente publicada.
O documento `docs/MVP_PRODUCTION_PIPELINE.md` registra o fluxo e as limitações.
Não há certificação de desempenho, nem conclusão de LOD/streaming de terreno.


## Evidência de integração no navegador

- Inventário: 2.766 nós de malha de entrada, 2.766 atribuídos uma única vez.
- Visão geral: 25/25 setores carregados, zero erros de setor.
- Modo a pé: 16/25 setores residentes após descarregar nove setores distantes.
- JavaScript: nenhum `pageerror` durante carga e transição observadas.
- Geometria fonte não foi movida nem modificada.
- Perfil provisório com 12 veículos, sem alegação de performance final.
- Contadores observados antes do ajuste de enquadramento: 7.470 chamadas na visão
  geral e 2.874 a pé; incluem o trabalho do renderizador e não certificam FPS.
  São evidência de que batching/LOD ainda são necessários.
- A vista geral usa o enquadramento de revisão já registrado em
  `automation/blender/r30a11_focus_core.py`, com câmera orbital. É apresentação,
  não transform da cidade nem georreferenciamento.
