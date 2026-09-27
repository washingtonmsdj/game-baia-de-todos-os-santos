# All Saints — Salvador em Mundo Aberto

> **Nome do jogo:** All Saints  
> **Tagline:** *Todos têm um preço. Ninguém é santo.*

Jogo de ação em mundo aberto ambientado em Salvador, Bahia, Brasil.

O MVP atual está concentrado na região do **Elevador Lacerda / Cidade Alta / Cidade Baixa / Praça Cairu / Mercado Modelo**. O objetivo de longo prazo é expandir o mundo jogável para Salvador inteira, preservando a geografia vertical da cidade, sua identidade cultural, contrastes urbanos, marcos arquitetônicos, bairros, trânsito e vida cotidiana.

## Foco atual do desenvolvimento

O projeto está construindo o primeiro recorte urbano jogável ao redor do Elevador Lacerda.

A cena-fonte do Blender já contém terreno, geometria de referência derivada de OSM, vias, marcos arquitetônicos, sistema do Elevador Lacerda, Mercado Modelo, Praça Cairu, áreas de circulação jogáveis e várias revisões internas.

O trabalho no Blender será continuado por meio de **passes Python versionados e não destrutivos** armazenados neste repositório. Assim, ChatGPT/Codex pode preparar melhorias no GitHub e aplicá-las depois dentro do Blender sem interromper repetidamente o fluxo de construção do mapa.

## Estrutura do repositório

```text
docs/
  PROJECT_VISION.md
  BLENDER_WORKFLOW.md
  CODEX_HANDOFF.md
  revisions/
    R27.md
    R28.md

tools/
  blender/
    r27_qa_review.py
    r28_gameplay_export.py
```

## Política de revisões do Blender

Cada automação do Blender deve:

- ser não destrutiva por padrão;
- preservar o `.blend` anterior;
- salvar em um novo arquivo de revisão;
- poder ser executada novamente com segurança quando possível;
- evitar renomeações em massa ou junções destrutivas sem aprovação explícita;
- registrar o que foi alterado;
- manter geometria de referência/proxy separada da geometria destinada ao jogo;
- fornecer metadados suficientes para o Codex validar o resultado posteriormente.

## Marco atual

**Vertical slice do MVP:** Elevador Lacerda e entorno jogável imediato.

Estado atual do pipeline:

- R27 — marcadores de QA, câmera de revisão e iluminação opcional de preview;
- R28 — guias de rota jogável, zonas de gameplay, classificação de exportação e auditoria de performance;
- R29 — otimização controlada planejada com base na auditoria da R28.

Consulte [`docs/BLENDER_WORKFLOW.md`](docs/BLENDER_WORKFLOW.md) e [`docs/CODEX_HANDOFF.md`](docs/CODEX_HANDOFF.md).
