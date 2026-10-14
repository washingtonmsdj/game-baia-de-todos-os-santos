# B81 — bloqueio saguão inferior → início OSM

Resultado: **NO_SCENE_CHANGE**. Nenhuma B82, exclusão, ocultação, mudança de colisão, nova trajetória ou exportação. B81 examinada ao vivo pelo MCP 9876 na mesma janela/PID 10684, sem salvar ou modificar a cena.

## Estado preservado

| Gate | Resultado |
|---|---|
| `LACERDA_VERTICAL` | `BLOCKED_EXTERNAL_EVIDENCE` |
| `LOWER_LOBBY_TO_OSM` | `UNRESOLVED_BLOCKED` |
| `OSM_CROSSING` | `TOPOLOGY_CONFIRMED_NOT_ADVANCED` |
| `MARKET_ENTRANCE_CONNECTOR` | `UNRESOLVED_NOT_ADVANCED` |
| `TRAFFIC_PERMISSION` | `null`, bloqueia gameplay |

B76–B81 e SSOT conferidos por hash; os arquivos canônicos protegidos da B80 permanecem intactos, incluindo as 27 testemunhas. `movement_enabled: false`. Guia OSM parcial desabilitada, patch de meios-fios B81 preservado, pintura verde `RENDER_ONLY`. Contrato externo não alterado. Expansão continua greybox. Não reaberta a investigação vertical.

## O que a guia representa

**Comprovado na cena:** `INFERIOR | guia de fila.001` é uma caixa sólida de oito vértices/seis faces, sem parent/modificadores, escala unitária, dimensões locais 4,00 × 0,08 × 1,10 m. Centro `[-52,226425; 59,352962; 7,840999]`, rotação Z −0,753606 rad. Coleção `11 ELEVADOR LACERDA | interior jogavel`, material `LAC R30B | inox escovado`, papel `game_role: static_collision`. A outra guia tem as mesmas dimensões e orientação. Material/nome não comprovam existência física no local.

**Candidato:** divisor/guia física de fila representado por um volume simplificado. A propriedade original declara: `Acabamentos por fotos; dimensões de aproximação, sem levantamento`. Dimensões acima são medidas da malha, não medidas do edifício real.

**Desconhecido:** posição/dimensões reais, permanência, atual existência, origem fotográfica específica, autor/script/operação de criação. Não há prova para classificá-la como temporária, não física ou proxy obsoleto. Classificação solicitada: **UNRESOLVED**; colisão mantida.

Na auditoria histórica R30A, a guia já tem os mesmos bounds, centro e escala. Não foi introduzida pelo patch B81. A busca literal nos scripts Blender e no histórico Git não recuperou seu criador. Os summaries R27/R30A são agregados e não permitem datar a criação nem provar ausência em R27.

## Referências examinadas

| Referência catalogada | O que permite concluir | Limite |
|---|---|---|
| Commons/Sintegrity, 21/07/2025, `elevador-lacerda-front-2d9b4031ff6a` | Aberturas ENTRADA/BILHETES e pavimento externo | Interior escuro/oculto; guia e conector interno não comprovados |
| Aleph/Street View, imagem julho/2024, `elevador-lacerda-detail-6e9796b71968` | Marquise/intradorso e andaimes | Entrada recortada; obra temporária não comprova configuração atual |
| SUCOP/A+P, prancha oficial 12, 2023 | Organização de saguão inferior, túnel, torre e aberturas | Sem registro XY aceito contra a cena; não identifica inequivocamente esta guia |

URLs, hashes, arquivos brutos e pareceres individuais estão em `docs/reports/research/lower-lobby-connector/decision.json`. Mantidas as classificações centrais de proveniência; nenhuma referência temporária virou asset final. Não foi inferida ausência da guia porque ela não aparece nas vistas externas.

O way 312006925 permanece evidência topológica entre 736745764 e 3178050253. Não comprova, sozinho, onde a pessoa sai do saguão ou como contorna seus obstáculos. Portanto não há conector físico novo autorizado. Nenhum traçado por menor distância ou interpolação foi aplicado.

## Controller e primeiro bloqueio

Reexecutada somente a parte inicial da rota candidata existente, limitada a 736745764 → 3178050253. Não executada a cadeia posterior, travessia ou entrada Mercado. Geometria física exportada da B81, cápsula raio 0,30 m, altura 1,80 m, step máximo 0,25 m, skin 0,015 m, gravidade 9,81 m/s², integração 1/60 s. Nenhum parâmetro reduzido.

- 50 movimentos aceitos; primeiro movimento bloqueado: **51**, `BODY_COLLISION_STEP_BLOCKED`.
- Última posição aceita: `[-50,547911; 57,702025; 7,421000]`.
- Proposta bloqueada: `[-50,617562; 57,772917; 7,421000]`.
- Testemunha CCD: `INFERIOR | guia de fila.001`, triângulo exportado 8706, parâmetro 0,75 do movimento, posição `[-50,600149; 57,755194; 7,421000]`, penetração **0,020493961 m**. É testemunha de interseção, não instante exato do primeiro contato.
- Step: elevação de 0,25 m livre; avanço elevado bloqueado pela mesma guia com penetração 0,020493961 m. Drop não executado após a falha. Apoio candidato de retorno disponível.
- Slide: seleção da face mais próxima retorna normal horizontal nula, pois seleciona uma face horizontal da caixa. Nenhum movimento lateral é executado. Isso caracteriza uma limitação do solver atual; não comprova que seja impossível contornar a guia real.
- Apoio anterior/proposto: `INFERIOR | piso do saguão`, Z 7,405999660; separação da cápsula 0,015 m, velocidade vertical estabilizada pelo apoio.

O replay registra gravidade, apoio, fases de step e testemunhas volumétricas/CCD. Não é certificação de engine; não autoriza navegação. O ensaio diagnostica o candidato existente, não um percurso real comprovado. A instrumentação preserva o comportamento do solver e expõe a falha de seleção da normal, em vez de aprovar um slide fictício.

## O que falta para resolver

É necessária uma vista atual do interior inferior que mostre **guia, abertura de saída e piso em conjunto**, ou levantamento/planta registrada por controles permanentes. Deve permitir distinguir obstáculo permanente de mobiliário temporário e identificar a conexão física até o primeiro nó OSM. Sem essa associação, não há base para retirar colisão nem implantar um contorno como se fosse real.

Após comprovar o conector, corrigir a seleção da normal de slide e validar o volume ao longo do percurso físico, apoios de borda, step e CCD na engine/adapter. Somente então avançar à cadeia OSM posterior. Tráfego e entrada Mercado continuam gates independentes.

## Evidências e reprodução

- `automation/blender/inspect_lower_queue_b81.py`: auditoria read-only da janela B81.
- `docs/reports/research/lower-lobby-connector/live_object_audit.json`: malhas, transform, material, propriedades e PID.
- `historical_r30a_object.json`: registro histórico; `historical_summaries.json`: fontes agregadas, sem inferência de ausência.
- `controller_trace.json`: primeira falha, fases, apoios e limites.
- `decision.json`: comparação, fontes, classificação e hashes de preservação.

```powershell
python tools/world/replay_cairu_controller.py --geometry artifacts/lacerda-controller/external_route_physics_b81.json --initial-connector --output-name ../../research/lower-lobby-connector/controller_trace.json
python tools/world/audit_lower_connector_evidence.py
```

Sem npm, build, suíte geral, mutação de cena ou promoção para produção. O próximo trabalho continua sendo comprovar **saguão → início OSM**, não detalhar o mapa ou contornar o elevador vertical.
