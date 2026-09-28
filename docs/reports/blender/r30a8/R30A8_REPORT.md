# R30A.8 — Oceano visual + contrato de gameplay

## Objetivo

Transformar a água da Baía de Todos-os-Santos em um sistema preparado para jogo, separando autoria visual, volume de gameplay e implementação runtime.

A água não é mais tratada apenas como um plano azul. A revisão preserva um nível físico determinístico em `Z = 0,35 m`, mantém um volume nadável/mergulhável até `Z = -16 m` e cria uma camada visual independente.

## Arquitetura

- `BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro`: referência de superfície e limite costeiro.
- `BAÍA | volume de água no limite do recorte`: volume de nado, mergulho e futura flutuação.
- `36 VISUAL | OCEANO R30A8`: camada estritamente visual.
- `R30A8 | Água oceânica`: material PBR com Fresnel implícito, IOR de água, macro/micro ondas em normal e animação procedural.
- `R30A8 | FOAM | linha costeira`: espuma fina derivada da própria borda da malha de água.
- `R30A8 | FOAM | halo costeiro`: faixa secundária suave para transição costeira.

## Regra de runtime

A deformação visual não deve ser usada diretamente como malha de colisão. Natação, mergulho, barcos, buoyancy, consulta de altura de onda, correntes, câmera submersa, cáusticas e pós-processamento devem ser resolvidos no motor de jogo.

O Blender é a autoridade de autoria para nível do mar, costa, volume, profundidade, guias de espuma e parâmetros artísticos. O contrato correspondente está em `water_runtime_contract.json`.

## Validação visual

A primeira espuma baseada em `REF_WATERFRONT` foi rejeitada porque o fit geográfico candidato produziu linhas deslocadas. A implementação final deriva a espuma da borda real da malha de água, portanto coincide com o recorte costeiro efetivamente usado pela cena.

Foi realizada renderização de revisão em Eevee a partir da câmera `ORLA | vista aérea Mercado, praça e Baía`.

## Próximos passos

1. Criar referência de ondas de larga escala com Ocean Modifier apenas para lookdev/bake.
2. Autorizar zonas de corrente e profundidade por gameplay.
3. Quando o motor for escolhido, implementar uma vertical slice de água runtime com player entrando, nadando, mergulhando e emergindo.
4. Medir GPU/CPU e definir níveis de qualidade de água por distância e plataforma.
