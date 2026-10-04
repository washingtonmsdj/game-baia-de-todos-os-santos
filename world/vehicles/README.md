# Veículos e variantes

## Fonte atual da viatura Rondesp

O catálogo aponta explicitamente para `blender/assets/vehicles/rondesp-pickup/marrom_v24_farois.blend`.
A V24 inclui montagem completa, materiais, faróis reforçados e demonstração de quatro portas,
giroflex azul/vermelho e freio. `intensidade_farois` ajusta os faróis no root;
`demonstracao_ativa=0` devolve portas e freio aos controles manuais. Revisões anteriores preservadas.
Fonte candidata, sem integração runtime: os controles de gameplay e o pós-processamento precisam
ser implementados na engine. As seções datadas abaixo registram o histórico da autoria.

## 02/10/2026 — Hilux Rondesp: fonte V04

Fonte explícita: `blender/assets/vehicles/rondesp-pickup/marrom_v04.blend`, cena `VIATURA | Rondesp Hilux marrom v04`. V01–V03 preservadas como históricas; não retomar por maior sufixo ou mtime.

Carroceria reconstruída com seções curvas; revisão da frente, encaixes dos faróis, máscara STD, capô, portas, teto, caçamba, capota e rodas. Medidas nominais Toyota em `world/vehicles/hilux-dimensions.json`: comprimento 5,325 m, largura base 1,855 m, altura stock 1,815 m, entre-eixos 3,085 m e pneus 265/65 R17. Esses valores são especificações do veículo base; não levantamento dos acessórios policiais. Vistas SRX enviadas servem ao contorno, sem aplicar rodas/alargadores da SRX à viatura.

Status `candidate`: aprovação visual final, brasão e mapa exato da camuflagem pendentes; não exportado/integrado no runtime. Relatório `docs/reports/blender/rondesp_marrom_v04.json`; comparação visual em quatro vistas, sem npm/build/testes gerais nesta etapa, conforme pedido do usuário.

`catalog.json` registra uma fonte por cor e seu SHA-256. Não selecionar arquivos
pelo número de revisão ou pela data. O amarelo usa a v06 existente com anúncio.
O verde e o azul ficam em `blender/assets/vehicles/torino-31065/`,
nos arquivos `verde_v01.blend` e `azul_v01.blend`.

As três cores mantêm carroceria Torino, dimensões, vidros, anúncio, rodas e três portas.
Somente pintura externa/marca Integra e cor dos letreiros foram alteradas.
Corrimãos, degraus e faixas verde/amarela/azul conservam suas cores.
A imagem mostra Comil Svelto: usada somente para orientar o verde, sem criar
esse modelo ou acrescentar Euro 6/ar-condicionado. Cor aproximada de modelagem.
Proveniência em `media-manifest.json`; imagem em `world-reference`, fora do Git.

Novos veículos ficam em `blender/assets/vehicles/<asset_id>/`; fontes antigas
permanecem no caminho atual. Componentes móveis continuam separados.
`production.json` define o veículo integrado no jogo. Este passe não exporta
GLB, altera a cidade ou promove variantes para runtime.

Para reproduzir: abrir a base do catálogo e executar via MCP na janela única
`automation/blender/create_green_bus_variant.py` ou
`automation/blender/create_blue_bus_variant.py`, que recusam sobrescrita.
Ambos usam `bus_color_variant.py`, para manter o mesmo processo de pintura.
O azul foi orientado pela imagem `meubuzu-integra3.jpg` fornecida pelo usuário.
Não se altera o número da frota 31065 ou os textos para criar outra cor.
# Viatura Rondesp

Fonte candidata própria: `blender/assets/vehicles/rondesp-pickup/marrom_v03.blend`.
ID `vehicle-rondesp-pickup`, variante `rondesp-pickup-marrom`.
As duas fotografias enviadas indicam Hilux CD 2.8 2024/2025, prefixo 3.1110.
Cabine dupla, capota fechada com acessos, quebra-mato, rodas de aço pretas,
sinalizador, estribos, camuflagem e inscrições foram modelados separadamente.
Frente `-Y`, metros, origem ao nível do chão; quatro pivôs de rodas e portas.
`APRESENTACAO` é somente estúdio, não geometria de exportação.
Dimensões e camuflagem são candidatas; brasão detalhado e movimento das portas
ainda pendentes. Fotografias são referências internas com licença pendente,
creditadas no manifesto; não foram incorporadas como textura. Sem integração
ao runtime, colisão de gameplay ou aprovação final nesta etapa.
V01 e V02 são históricas e não são fonte ativa. O catálogo aponta explicitamente
V03; a escolha não depende de sufixo, data do arquivo ou conversa.


## Hilux Rondesp V06

Autoria ativa no catálogo: `rondesp-pickup/marrom_v06.blend`, sob `blender/assets/vehicles/`. V01–V05 preservadas como histórico não aprovado. Carroceria em revisão de fidelidade; não integrada ao runtime. Relatório: `docs/reports/blender/rondesp_marrom_v06.json`.
