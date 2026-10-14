# Lacerda — corpo superior e cobertura B100 — 08/10/2026

B99 inspecionada na única janela Blender/MCP9876, sem alterações pendentes:616 componentes conhecidos intactos. Utilizados os vetores/cotas18/19/20/23 e o registro relativo já extraído naB99; não houve nova aquisição, novo SSOT ou nova pesquisa da instalação. B100 salva e reaberta nessa janela, arquivo `blender/salvador_lacerda_r30b100_corpo_superior_cobertura.blend`, SHA256 `481d884fc3dc413ee9413c1a1b5259d05245da6a2fb7c273e39106ad69750678`.

## Modelagem aplicada

- Corpo superior retangular reconstruído como envoltória oca contínua de oito arestas, incluindo o prolongamento técnico voltado à torre. Pequenos rebaixos dos pilares/jambas simplificados, explicitamente candidatos; não extrudir o retângulo do administrativo como edifício inteiro.
- Cobertura existente substituída pelo contorno completo20/321, sem criar uma segunda laje. Platibanda contínua entre os contornos20/321 e20/326; topo relativo+15,40m. A primeira aplicação revelou erro de conversão entre espaço arquitetônico e espaço local do objeto reutilizado: corrigido no gerador e na mesh, preservando o checkpoint preliminar e sem deslocar mapa/objeto.
- Lajes administrativas nos níveis documentais+4,94m(Z75,063008728) e+9,42m(Z79,543008728), diferença4,48m. Teto da galeria continua em+4,00m; não confundir teto com piso do andar. Ala técnica/caixa dos elevadores/escada permanecem sem lajes inferidas. Limite administrativo derivado da parede18/563; não é detalhamento de interiores.
- 158 componentes de esquadrias migrados rigidamente para as fachadas correspondentes, preservando dimensões/topologia. Segunda fileira acompanha a diferença entre os níveis dos pavimentos(+0,896667m em relação ao espaçamento legado); peitoril, layout e dimensões das janelas continuam candidatos herdados, sem alegar comprovação as-built. Dezoito aberturas reconciliadas com os vidros existentes.
- Dezesseis tampões coincidentes removidos **antes** da soldagem dos oito trechos, produzindo um corpo único sem divisórias internas acidentais. Nenhum preenchimento para fazer controller passar.
- Quatro componentes novos,159 meshes alteradas(158 partes rígidas e a cobertura),19 peças antigas preservadas fora da apresentação ativa. 457 assinaturas anteriores intactas. Referências substituídas continuam com geometria/material/transform preservados; B99 e snapshots anteriores intactos.

## Verificação na cena reaberta

QA de 620 componentes de arquitetura, 321 visíveis. Malhas do escopo sem faces degeneradas, arestas não manifold, winding inconsistente ou duplicatas internas. Erro máximo de aplicação rígida0.00000764m; alteração máxima de comprimento de aresta0.00000310m, compatível com precisão numérica e sem reescala.

160 sondagens do corpo, 40 contatos sob a cobertura,18 aberturas com vidro presente e peitoril acima do piso, 4 sondagens dos pavimentos. Pontes/galerias/túnel anteriores rechecados pela QA comum. Essas verificações não aprovam instalação, CCD da cabine, navegação ou controller.

Capturas reais da única cena: `artifacts/lacerda-live-diagnostic/b100-corpo.png`, `b100-cobertura.png`, `b100-conjunto.png`, `b100-map.png`. Final no mapa completo, terreno visível, sem edição pendente. Não houve npm/build/testes gerais; somente QA delimitada de geometria/persistência.

## Precisão e preservação

Contornos são documentais relativos; implantação absoluta no SSOT continua pendente. Parede0,30m e lajes0,25m são seções candidatas. Migração das esquadrias conserva formas herdadas e não equivale a layout documental aprovado. Campo de precisão/proveniência/replacement_required acompanha os componentes; nenhuma promoção para produção.

B76–B99, SSOT, terreno, duas torres, passarela, túnel, subsolosB99 e GAMEPLAY_PROXY B82 preservados. `LACERDA_VERTICAL=BLOCKED_EXTERNAL_EVIDENCE`,27 testemunhasB80 `UNRESOLVED`, `movement_enabled=false`, `replacement_required=true`. Instalação vertical permanece congelada. Lapa/Dique/Fonte Nova e demais áreas não modificadas. Não representar o exterior candidato como elevador todo certificado ou controller final.
