# R30A.8 — Oceano e água de gameplay

## Direção

A R30A.8 estabelece a água como sistema de jogo, não apenas como elemento visual.

A revisão separa três responsabilidades:

- autoria no Blender: costa, nível do mar, volume, profundidade, espuma e lookdev;
- contrato engine-agnostic: metadados estáveis para exportação;
- runtime no motor: ondas, consultas de superfície, natação, mergulho, buoyancy, correntes e renderização subaquática.

## Princípios

- nível físico do mar determinístico em `0,35 m`;
- volume de gameplay até `-16 m` no recorte atual;
- superfície visual nunca é usada diretamente como colisão dinâmica;
- espuma costeira deriva da malha real de água;
- deformação visual pode evoluir sem quebrar gameplay;
- binding de engine permanece `unbound` nesta revisão.

## Artefatos

- `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a8_ocean.blend`;
- `docs/reports/blender/r30a8/R30A8_REPORT.md`;
- `docs/reports/blender/r30a8/ocean_scene.json`;
- `docs/reports/blender/r30a8/water_runtime_contract.json`.
