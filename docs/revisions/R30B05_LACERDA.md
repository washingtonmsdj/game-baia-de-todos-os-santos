# R30B.05 — sequência comercial da entrada baixa

Arquivo: `blender/salvador_lacerda_r30b05_comercio.blend`. R30B.04 preservada, sem promoção ao runtime.

- Bloco OSM 1263035779: fachada branca/rosada, painéis vazados e representação externa dos portais. A fonte OSM registra `shop=bakery`; associação à Cayru da foto permanece **candidata**, sem letreiro nominal.
- Bloco OSM 1220650665: fachada azul, cornijas e janelas arqueadas inspiradas no sobrado contíguo da mesma foto. Associação arquitetônica candidata; nenhuma identidade comercial atribuída.
- Toldo do Depósito Vissor inclinado para a rua, corrigindo a seção horizontal provisória.
- Footprints, alturas e cotas dos três blocos preservados. Os vãos comerciais são representação exterior, sem interior acessível ou nova colisão. Proporções adaptadas aos blocos existentes (`ADAPT_LOCAL`).

Referência reutilizada: `elevador-lacerda-front-2d9b4031ff6a`, registrada no manifesto. Nenhuma mídia pesada duplicada.

Inspeção visual da sequência comercial na cena completa, captura `artifacts/lacerda/r30b05_comercio_final.png`. Estado parcial: blocos restantes e relação espacial da praça alta ainda pendentes. Inspeção da praça identificou proxy superior OSM 1263035781 já oculto; não foi apagado nem deslocado outro edifício com base apenas na obstrução da câmera.

Scripts: `automation/blender/refine_lacerda_r30b05_commerce.py`, seguido de `automation/blender/refine_lacerda_r30b05_neighbor.py`.
