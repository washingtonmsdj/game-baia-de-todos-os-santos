# R30A.6 — Collision Chunks

## Direção

A colisão otimizada criada na R30A.5 ainda era um único mesh de `131.097` polígonos. A R30A.6 divide esse collider em células espaciais para permitir streaming, culling e integração futura com física de engine.

A geometria-fonte permanece intacta. Os chunks são derivados e reconstruíveis.

## Critério de seleção

Foram avaliadas grades de `64 m`, `128 m` e `256 m`.

O candidato precisa satisfazer:

- no máximo `80` chunks;
- no máximo `15.000` polígonos em qualquer chunk;
- P95 de até `10.000` polígonos.

A grade de `128 m` foi a primeira a cumprir todos os critérios.
## Operação

A revisão deve ser executada ao vivo em uma única janela visível do Blender.

Rota principal:

`Desktop Commander -> OrdaX/Blender Live -> Blender visível`

Fallback na mesma janela:

`BlendMCP 1.4.4 -> 127.0.0.1:9877`

Não abrir uma segunda instância do Blender para aplicar geometria. Processos headless são permitidos somente para validações read-only/CI, nunca para alterações de cena quando o usuário estiver acompanhando o trabalho ao vivo.

## Saída

Coleção: `34 GAMEPLAY | COLLISION CHUNKS R30A6`.

Cada chunk registra tamanho da célula, índices X/Y, origem e papel de runtime por custom properties.
