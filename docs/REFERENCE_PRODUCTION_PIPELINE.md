# Pipeline de Referências de Produção

## Objetivo

Este documento define como o projeto **Bay of All Saints** registra, coleta, valida e consome referências do mundo real para reproduzir Salvador com alta fidelidade sem misturar material temporário, dados geográficos e assets finais.

O princípio central é simples: **nenhum prédio, rua, praça, encosta, cais ou marco importante deve depender de memória, improviso ou imagem solta sem origem conhecida**.

## Camadas do sistema

### 1. Geografia

Responsável por posição, escala e continuidade territorial:

- bounds WGS84;
- OSM/Geofabrik;
- terreno e elevação;
- coastline, cais e borda d'água;
- sistema de coordenadas;
- transformação mundo real → Blender/engine;
- chunks territoriais.

Esta camada responde: **onde fica e qual é a forma-base?**

### 2. Catálogo de locais

Cada elemento relevante recebe um `location_id` estável, independente do nome do objeto no Blender.

Exemplos:

- `elevador-lacerda`;
- `mercado-modelo`;
- `palacio-rio-branco`;
- `praca-cairu`;
- `praca-tome-de-sousa`.

O catálogo registra categoria, prioridade, fidelidade desejada, OSM ID quando conhecido, posição, estado de modelagem e requisitos de referência.

Esta camada responde: **o que é e em que estado está?**

### 3. Mídia de referência

Fotos, ortofotos aprovadas, levantamentos próprios, plantas e outras referências visuais ficam fora do Git quando forem pesadas. O Git armazena apenas metadados, hashes, licença, origem, data e caminho lógico.

Nenhuma imagem deve entrar no pipeline apenas como `foto1.jpg` sem contexto.

Cada item precisa informar pelo menos:

- `media_id`;
- `source_type`;
- `capture_date` quando conhecida;
- origem/licença/status de uso;
- orientação ou vista;
- local associado;
- hash quando o arquivo existir localmente;
- se é somente referência temporária ou pode permanecer no acervo de produção.

Esta camada responde: **com base em quê estamos modelando?**

### 4. Asset de produção

O Blender/engine mantém sua própria representação do local.

Estados padronizados:

- `not_started` — ainda não modelado;
- `proxy` — volume/footprint de referência;
- `blockout` — forma jogável inicial;
- `modeling` — modelagem em andamento;
- `review` — aguardando comparação com referência;
- `approved` — aprovado para o nível de fidelidade atual;
- `needs_rework` — divergência conhecida;
- `deprecated` — asset substituído.

Esta camada responde: **o que realmente existe no jogo?**

## Níveis de fidelidade

### A — Hero

Usado para marcos reconhecíveis e locais de gameplay importante.

Requer, quando aplicável:

- implantação e escala verificadas;
- altura/volume verificáveis;
- frente;
- oblíqua esquerda;
- oblíqua direita;
- laterais expostas;
- cobertura/telhado quando visível;
- acessos;
- detalhes arquitetônicos dominantes;
- relação com terreno/calçada/rua;
- revisão visual antes de aprovação.

### B — Contextual

Prédios importantes para a leitura urbana, mas não hero assets.

Requer:

- footprint/posição;
- altura plausível ou verificada;
- fachada principal;
- pelo menos uma vista oblíqua quando disponível;
- materiais e ritmo arquitetônico coerentes.

### C — Fundo urbano

Edificações de preenchimento distante ou baixo impacto.

Requer:

- footprint;
- altura aproximada;
- tipologia;
- material dominante;
- coerência com o quarteirão.

Mesmo nível C não deve deslocar rua ou coastline para "caber" no modelo.

## Regra para ruas, calçadas e oceano

A fidelidade da malha urbana tem prioridade sobre decoração.

Antes de detalhar uma área, validar:

1. eixo e largura aproximada das vias;
2. cruzamentos;
3. calçadas e travessias;
4. ladeiras/escadarias;
5. muros e contenções relevantes;
6. coastline/cais/borda marítima;
7. relação terreno ↔ rua ↔ água;
8. continuidade com chunks vizinhos.

A água pode usar shader artístico, porém o **contorno costeiro e a implantação do cais devem permanecer geograficamente coerentes**.

## Referência visual tipo "streetview interno"

O projeto pode manter um acervo navegável por pontos/rotas, semelhante conceitualmente a um streetview interno, sem acoplar a produção a um fornecedor específico.

Cada ponto de captura deve ser associado a:

- coordenada quando disponível;
- heading/orientação;
- lado da rua ou alvo;
- `location_id` relacionado;
- proveniência/licença;
- data;
- distância/qualidade quando conhecida.

O Codex pode usar esse acervo para orientar modelagem e revisão, mas não deve copiar material marcado como proibido para produção nem promover mídia temporária para asset final.

## Estrutura lógica recomendada

Fora do Git:

```text
world-reference/
  mvp-centro-lacerda/
    media/
      elevador-lacerda/
      mercado-modelo/
      palacio-rio-branco/
      streets/
    aleph/
      ...
```

No Git:

```text
world/
  areas/
    mvp-centro-lacerda/
      area.json
      locations.json
      media-manifest.json

schemas/
  area-reference.schema.json
  location-reference.schema.json
  media-manifest.schema.json
```

## Regras de promoção para produção

Um local não pode ser marcado `approved` se:

- a posição geográfica ainda estiver incerta em nível incompatível com sua classe;
- não houver referência visual mínima exigida pelo nível de fidelidade;
- a origem/licença da referência estiver indefinida;
- houver divergência conhecida em escala, orientação, acesso ou silhueta principal;
- o asset estiver baseado somente em proxy OSM quando for nível A.

## Papel do Codex

Para cada área, o Codex deve:

1. validar `area.json`, `locations.json` e `media-manifest.json`;
2. identificar os locais com maior `priority` ainda não `approved`;
3. localizar as referências permitidas associadas;
4. trabalhar somente no nível de fidelidade solicitado;
5. preservar IDs e proveniência;
6. registrar no relatório da revisão quais `location_id` foram alterados;
7. gerar capturas de comparação antes/depois para Hero assets;
8. não inventar dimensões exatas quando as fontes não suportarem essa precisão.

## Regra anti-gambiarra

Não usar:

- nome de arquivo como única identificação de referência;
- caminhos absolutos de uma máquina dentro de metadados versionados;
- imagens sem origem/licença conhecida;
- offsets manuais não registrados para "alinhar visualmente" áreas;
- duplicação silenciosa de prédios em overlaps;
- geometria de Google Satellite/Street View como asset final;
- renomeação de objetos Blender como substituto de um `location_id` estável.

Toda exceção deve ser explícita, documentada e temporária.
