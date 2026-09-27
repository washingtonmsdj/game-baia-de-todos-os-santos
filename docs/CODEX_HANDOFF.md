# Codex Handoff — Blender MVP

## Goal

Continue the Salvador MVP scene without requiring repeated manual coordination.

The working Blender scene is expected to be provided locally to Codex. GitHub is the source of truth for automation scripts, revision notes, and validation instructions.

## Current scene context

The analyzed source scene contained approximately:

- 4,617 objects;
- 4,097 mesh datablocks;
- 135 materials;
- 30 collections;
- 412 curves;
- 54 cameras;
- 1 explicit light;
- thousands of automatically suffixed object names such as `.001`, `.002`, etc.

The scene already includes multiple historical passes around Elevador Lacerda, Mercado Modelo, Praça Cairu, terrain, roads, accesses, and playable interiors.

Do not treat it as a fresh blockout.

## Apply order

When starting from the original analyzed scene:

1. Run `tools/blender/r27_qa_review.py`.
2. Open/validate the resulting `_r27.blend`.
3. Run `tools/blender/r28_gameplay_export.py` on the newest valid scene.
4. Open/validate `_r28.blend`.
5. Read the Blender Text datablock `R28_PERFORMANCE_AUDIT` before performing optimization.
6. Use the R28 audit to drive R29. Do not guess which repeated objects are safe to instance.

If the local source is already R27 or R28, skip earlier passes as appropriate.

## Required validation after every pass

Codex should check all of the following before declaring a revision successful:

- the source `.blend` still exists and was not overwritten;
- the new revision file exists;
- Blender can reopen the new file;
- generated revision collections exist;
- generated Text datablocks exist;
- there are no Python exceptions in the Blender console/log;
- total object counts remain plausible;
- no mass deletion occurred;
- landmark geometry is still present;
- the affected gameplay route can be visually inspected.

## Current gameplay corridor

The current MVP route is:

**Cidade Alta entrance → upper walkway → Elevador Lacerda cabins → lower exit → Cidade Baixa → Praça Cairu → Mercado Modelo**

The guide coordinates used by R27/R28 come from checkpoints already registered in the source scene. They are design guides, not certified survey data.

## R29 target

R29 should be a controlled performance pass.

Priority order:

1. identify truly identical repeated props/meshes;
2. instance/link only equivalence that is proven safe;
3. preserve object transforms and collection membership;
4. avoid touching HERO or GAMEPLAY objects unless explicitly validated;
5. generate simplified collision candidates instead of replacing render meshes;
6. identify high-cost landmark meshes for manual LOD work;
7. propose road/sidewalk chunk boundaries;
8. produce before/after metrics;
9. save as a new `_r29.blend` revision.

## R29 safety constraints

Do not automatically instance or merge objects when any of the following differ or are uncertain:

- vertex/edge/polygon topology;
- UV data;
- material slots/order;
- color/custom attributes;
- shape keys;
- mesh custom properties that affect the workflow;
- object-specific modifiers that rely on unique mesh data;
- gameplay metadata;
- animation/deformation requirements.

Do not optimize by name alone.

## Visual/world-building work after optimization

Once the MVP scene is technically stable, prioritize visible improvements:

- street and sidewalk readability;
- Praça Cairu composition;
- Mercado Modelo surroundings;
- Cidade Alta/Cidade Baixa transitions;
- landmark silhouette quality;
- vegetation distribution;
- street furniture;
- lighting and atmosphere;
- traffic/pedestrian space;
- gameplay cover, shortcuts, alleys, entrances, and traversal choices;
- expansion-ready boundaries for adjacent districts.

## Documentation language

Repository documentation and development notes should be written in English.

Real Salvador place names should remain in Portuguese where that is the correct proper name.
