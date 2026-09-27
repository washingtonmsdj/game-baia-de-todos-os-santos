# All Saints — Open-World Salvador

> **Working title:** All Saints  
> **Tagline:** *Everyone has a price. No one is a saint.*

An open-world action game set in Salvador, Bahia, Brazil.

The current MVP focuses on the **Elevador Lacerda / Cidade Alta / Cidade Baixa / Praça Cairu / Mercado Modelo** area. The long-term goal is to expand the playable world across Salvador while preserving the city's vertical geography, cultural identity, urban contrasts, landmarks, neighborhoods, traffic, and everyday life.

## Current development focus

The project is currently building the first playable urban slice around Elevador Lacerda.

The Blender source scene already contains terrain, OSM-derived reference geometry, roads, architectural landmarks, the Elevador Lacerda system, Mercado Modelo, Praça Cairu, playable circulation areas, and several internal revision passes.

Current Blender work is being continued through **versioned, non-destructive Python passes** stored in this repository. This allows ChatGPT/Codex to prepare changes in GitHub and apply them later inside Blender without repeatedly interrupting the level-design workflow.

## Repository structure

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

## Blender revision policy

Each Blender automation pass must:

- be non-destructive by default;
- preserve the previous `.blend` file;
- save to a new revision file;
- be safe to run more than once when practical;
- avoid mass renaming or destructive joins unless explicitly approved;
- record what it changed;
- keep reference/proxy geometry separate from game-ready geometry;
- provide enough metadata for a later Codex pass to validate the result.

## Current milestone

**MVP vertical slice:** Elevador Lacerda and its immediate playable surroundings.

Current pipeline state:

- R27 — QA anchors, review camera, optional preview lighting.
- R28 — gameplay route guides, gameplay zones, export classification, performance audit.
- R29 — planned controlled optimization pass using the R28 audit.

See [`docs/BLENDER_WORKFLOW.md`](docs/BLENDER_WORKFLOW.md) and [`docs/CODEX_HANDOFF.md`](docs/CODEX_HANDOFF.md).
