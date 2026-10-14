# B81 — evidência visual de 2025 e correção do slide

Resultado: **NO_SCENE_CHANGE**, nenhuma B82. Classificação da `INFERIOR | guia de fila.001`: **STILL_UNRESOLVED**. Gradis físicos e circulação lateral aparecem em imagens atuais, mas não foi comprovado qual gradil corresponde à caixa candidata da B81 nem seu registro no SSOT. Não houve alteração, ocultação, deslocamento ou retirada de colisão. Nenhuma nova rota foi criada.

## Evidência examinada

As cinco fotografias Commons foram examinadas integralmente. Autor Sintegrity, captura 21/07/2025, licença CC BY-SA 4.0, hashes conferidos contra o catálogo. Quatro já estavam catalogadas; somente `125707` foi acrescentada, sem duplicar os binários existentes. Todas permanecem referência de desenvolvimento.

| Foto — sufixo após `20250721` | Observação e limite |
|---|---|
| `125127` | Painel LACERDA/Salvador entre colunas; não mostra o percurso. |
| `125222` | Placa da entrega da restauração em fevereiro/2025; não comprova posição da guia. |
| `125324` | Galeria e saída superiores, com vista da Cidade Baixa. Não confundir com saída inferior. |
| `125657` | Rocha exposta, mármore e iluminação; sem guia/saída/piso conjuntamente. |
| `125707` | Saguão inferior, ilha envidraçada da bilheteria, fachada/SAÍDA, pessoa saindo à esquerda da ilha e pavimento externo visível. Confirma passagem junto à bilheteria, mas não identifica a guia `.001` nem liga essa passagem ao nó OSM. |

A [foto 125707](https://commons.wikimedia.org/wiki/File:Elevador_Lacerda_-_Salvador_-_20250721125707.jpg) é a mais útil para relacionar interior e abertura externa. A ausência de um gradil em parte do enquadramento não comprova sua inexistência no local. Não foram extraídas larguras métricas da perspectiva.

Foram examinados **quadros reais selecionados de dois vídeos**, não apenas títulos/descrições e não a íntegra de ambos:

| Vídeo Farol Viagem | Publicação indicada pelo player | Quadros úteis examinados |
|---|---|---|
| [Como é o Elevador Lacerda por Dentro](https://www.youtube.com/watch?v=b896lscqBws) | 15/07/2025 | 0:10, 0:20, 0:38, 1:00, 1:23 |
| [Por dentro Depois da Reforma](https://www.youtube.com/watch?v=0VC78CYx0X0) | 14/03/2025 | 1:11, 2:22, 3:34 |

Em 0:20 e 0:38 do primeiro vídeo há gradis longos, montantes e corrimão castanho, com pessoas passando pelas laterais. Uma barreira metálica separada e cones também aparecem; não foram tratados como o mesmo elemento. A vista em 1:23 é superior e não serve como saída para Cairu. No segundo vídeo, fachada inferior e abertura lateral são visíveis, mas pessoas/estrutura ocultam partes relevantes. Nenhum quadro resolve a correspondência específica com as duas caixas da B81.

Publicação não equivale a data de filmagem. A data de captura dos vídeos permanece `null`; licença de redistribuição não verificada. Screenshots nativos foram preservados como **DEV_REFERENCE_ONLY**, sem baixar os vídeos brutos. Capturas com buffering, quadro atrasado ou divergência de tempo do player estão registradas separadamente e **excluídas da decisão**. Os horários úteis são posições indicadas pelo player, não timecodes exatos de frames extraídos.

## O que está e não está comprovado

- **Comprovado visualmente:** gradis físicos no corredor filmado; pessoas circulando ao lado deles; passagem junto à bilheteria inferior até uma abertura externa.
- **Não comprovado:** identidade da `.001`, posição/orientação exatas, relação registrada com a segunda guia, fixação/permanência, removibilidade, largura métrica e sequência contínua até o início do way 312006925.
- **Não autorizado:** `GUIDE_CONFIRMED_NOT_PRESENT`, `GUIDE_PRESENT_BUT_SCENE_POSITION_WRONG` ou remoção de colisão. Também não se aplica `PASSAGE_AROUND_GUIDE_CONFIRMED` à guia específica da cena sem correspondência inequívoca.

O fato de gradis genéricos aparecerem não promove automaticamente a caixa `.001` para `GUIDE_CONFIRMED_CURRENT_PHYSICAL`. O próximo dado necessário é o registro dos gradis, abertura e piso contra controles permanentes da cena/plantas, com continuidade até o nó OSM. O material existente permite avançar essa comparação, mas não autoriza uma rota por proximidade.

## Solver corrigido, sem aprovação de rota

`tools/world/character_slide.py` seleciona uma face lateral realmente associada ao contato CCD e oposta ao movimento. Empates em arestas não escolhem mais automaticamente a face horizontal. Testemunhas profundamente penetrantes são refinadas para selecionar a normal perto da borda de contato; isso não substitui nem relaxa o CCD. A projeção ainda precisa passar pelo CCD original e não recupera uma cápsula inicialmente penetrante.

O replay recalcula apoio no XY projetado do slide, pois apoio do alvo original não é apoio do movimento lateral. Mantidos raio **0,30**, altura **1,80**, step **0,25**, skin **0,015**, gravidade **9,81** e intervalo **1/60 s**. Nenhuma geometria foi alterada.

| Resultado numérico | Baseline anterior | Após correção |
|---|---|---|
| Movimentos aceitos | 50 | 145 |
| Slides aceitos | 0 | 95 |
| Primeira parada | 51: colisão/step, normal horizontal nula | 146: `GRAVITY_SUPPORT_NOT_CERTIFIED` |
| Chegada/rota aprovada | Não | Não |

No movimento 51, o avanço e step continuam bloqueados pela guia; a face lateral selecionada tem normal XY `[0,729186; −0,684315]`, triângulo exportado 8713. O slide passa no CCD e mantém apoio no piso do saguão, gap 0,015. Uma verificação independente de 101 amostras desse primeiro slide contra a malha exportada da guia encontrou distância mínima 0,353892, acima do limiar contratual 0,285.

A parada 146 tem apoio anterior no piso do saguão em Z 7,405999660 e apoio candidato seguinte no terreno em Z 7,255668640, gap 0,162606. Isso **não comprova um degrau real nem autoriza preencher o vão**: após slides, os alvos da rota candidata ficam distantes da posição efetiva. O replay usa apoio central e não é prova completa de borda/engine. Mantém o bloqueio em vez de certificar uma queda ou conexão desconhecida.

Onze testes regressivos passaram: empate horizontal/lateral, parede distante, piso isolado, orientação invertida, tangência, degeneração, movimento de afastamento, penetração inicial, testemunha profunda, projeção com clearance e canto com segunda parede que continua bloqueando. Catálogo validado: zero erros, dois avisos anteriores (bounds WGS84 e referência insuficiente do cais). Sem suíte geral, npm ou build.

## Estado preservado

| Gate | Estado |
|---|---|
| `LACERDA_VERTICAL` | `BLOCKED_EXTERNAL_EVIDENCE` |
| `LOWER_LOBBY_TO_OSM` | `UNRESOLVED_BLOCKED` |
| `OSM_CROSSING` | `TOPOLOGY_CONFIRMED_NOT_ADVANCED` |
| `MARKET_ENTRANCE_CONNECTOR` | `UNRESOLVED_NOT_ADVANCED` |
| `TRAFFIC_PERMISSION` | `null` |
| Movimento / NAV parcial | `false` / `false` |
| Expansão | `GREYBOX`, não alterada |

24 arquivos protegidos conferidos por hash, incluindo B76–B81, SSOT e evidências canônicas B80. Contrato externo inalterado. 27 testemunhas continuam `UNRESOLVED`; não repetido CCD vertical. Patch de meios-fios e pintura `RENDER_ONLY` preservados. Nenhuma exportação/promoção para produção.

## Registro e reprodução

`docs/reports/research/lower-guide-2025/visual_evidence.json` registra por foto/frame fonte, data, autor, licença, hash, observação, confiança, correspondência, conclusão permitida e limites. `decision.json` contém classificação e preservação; `solver_validation.json`, os testes e a verificação local. `controller_slide_final.json` é o replay final. Os replays intermediários são apenas diagnóstico, não baseline vigente. Proveniência central em `world/data-provenance.json`, política existente reutilizada.

```powershell
python -m unittest discover -s tests -p test_character_slide.py -v
python tools/world/replay_cairu_controller.py --geometry artifacts/lacerda-controller/external_route_physics_b81.json --initial-connector --output-name ../../research/lower-guide-2025/controller_slide_final.json
python tools/world/audit_lower_guide_2025.py
python tools/references/validate_registry.py --root .
```

O relatório anterior continua baseline histórico intacto. A correção técnica do slide permite diagnosticar melhor o candidato; não comprova a rota real nem autoriza avançar travessia/Mercado.
