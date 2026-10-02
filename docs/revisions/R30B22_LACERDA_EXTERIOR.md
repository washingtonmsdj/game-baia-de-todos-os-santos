# R30B.22 — Revisão do exterior do Elevador

Fonte candidata: `blender/salvador_lacerda_r30b22_exterior_vidros.blend`.
Fonte anterior preservada: R30B.20. Não houve promoção ao runtime.

## Correções aplicadas

- R30B.21 restaurou somente a mesh da face oposta do poço a partir da R30B.19
  e reaplicou os vãos com normais corretas no cortador. O objeto conserva sua
  identidade, transformações e dependências.
- Portais inferiores receberam material mineral de variação discreta, reduzindo
  o contraste excessivo do material anterior; bandeiras receberam vidro fino.
- R30B.22 ajustou o vidro compartilhado do Elevador para transparência por alpha,
  removendo o ruído de transmissão visível na galeria e nas janelas.
- Reboco da torre recebeu microrelevo procedural em coordenadas de objeto.
- Letreiro inferior foi contido no vão central entre pilares (2,50 m na cena).
  Essa largura é adaptação à geometria existente, não medida cadastral.

## Pendências e critérios

Estado **parcial**, sem aprovação de fidelidade final. Comparação visual no
Blender confirmou melhora dos vidros e do acesso; a encosta continua com recorte
e transições artificiais junto ao apoio. Corrigir o terreno respeitando a
implantação do suporte e a continuidade da via. Não deslocar o apoio para
exibi-lo. R30B.14 foi rejeitada por esse motivo; R30B.17–18 são experimentos
rejeitados. R30B.16 é a origem do terreno desta candidata.

Revisar ainda a fachada superior, o coroamento e as proporções das janelas por
comparação direta com referências catalogadas. Materiais procedurais precisarão
de bake para exportação; o vidro por alpha é uma aproximação de vidro fino,
não uma simulação óptica. Geografia, terreno, pistas, colisão e navegação não
foram modificados nas R30B.21–22.

Relatórios específicos: `artifacts/lacerda/r30b21_report.json` e
`artifacts/lacerda/r30b22_report.json`. A R30A.11 segue ativa em `production.json`.
