# Blender Workflow

## Purpose

This repository stores reproducible Blender automation passes for the Salvador open-world project.

The `.blend` working file remains the source scene, while Python scripts in `tools/blender/` describe controlled changes that can be applied later by Codex or by a developer running Blender locally.

## Why this workflow exists

The current scene is already large and historically layered. It contains thousands of objects, imported reference geometry, gameplay structures, landmark models, terrain, roads, cameras, and prior revision work.

For that reason, automated work must be conservative. A script should make a specific improvement, record it, save a new revision, and avoid destructive global cleanup unless that cleanup is explicitly scoped and validated.

## Revision rules

Every revision script should follow these rules:

1. **Never overwrite the source file by default.**
2. Save to a new suffix such as `_r28.blend`, `_r29.blend`, etc.
3. Prefer adding metadata, collections, guides, instances, or validated derived geometry over destructive edits.
4. Avoid mass renaming because Blender object names may be referenced by constraints, drivers, scripts, exporters, or manual workflows.
5. Avoid broad `Join`, `Decimate`, triangulation, transform application, or material consolidation without a dedicated validation pass.
6. Mark generated objects with a revision prefix and/or custom properties.
7. Make generated content removable/rebuildable when practical.
8. Keep OSM/DEM/reference geometry distinguishable from authored/game-ready geometry.
9. Store an internal Blender Text datablock or scene metadata describing the pass.
10. Emit a useful console summary.

## Suggested repository layout

```text
tools/blender/
  r27_qa_review.py
  r28_gameplay_export.py
  r29_optimization.py

docs/revisions/
  R27.md
  R28.md
  R29.md
```

## How Codex should apply a Blender revision

Codex should use the newest validated `.blend` source available locally and run Blender from the command line, for example:

```bash
blender current_scene.blend --python tools/blender/r28_gameplay_export.py
```

If Blender is installed under a non-standard path, Codex should locate the executable rather than modifying the script.

After execution, Codex should verify:

- Blender exited successfully;
- the expected new `_rXX.blend` file exists;
- the generated collections/text datablocks exist;
- object counts did not unexpectedly collapse;
- no source `.blend` was overwritten;
- the script console output does not contain Python exceptions;
- the resulting file can be reopened.

For revisions involving visual or spatial changes, Codex should additionally open the scene and inspect the affected area before considering the pass complete.

## Binary file policy

`.blend` files are intentionally ignored by default.

Reasons:

- the scene can become very large;
- ordinary Git is inefficient for repeated large binary revisions;
- Blender binaries cannot be usefully code-reviewed as text;
- reproducible scripts are more valuable for agent-to-agent handoff.

If the project later decides to version `.blend` files, configure Git LFS intentionally and update `.gitignore`/documentation at that time.

## Naming policy

Repository documentation and script comments should be in English.

Blender object/collection names may retain Portuguese names where they correspond to real Salvador locations, existing scene conventions, or in-world labels. Avoid renaming existing scene objects solely for language consistency.

## Safety levels

### Safe / default

- create guide collections;
- add non-rendering helpers;
- add custom properties;
- create audit reports;
- add export-link collections without unlinking originals;
- create review cameras;
- create optional preview lighting;
- save a new revision.

### Requires validation

- replace repeated meshes with linked instances;
- create collision meshes;
- create LODs;
- consolidate roads by spatial chunk;
- consolidate materials;
- apply transforms;
- move objects between canonical collections.

### Explicit approval / dedicated migration

- mass deletion;
- mass renaming;
- destructive mesh joining;
- deleting source reference geometry;
- coordinate-system changes;
- rescaling the entire world;
- rewriting landmark architecture.

## Current sequence

- **R27:** QA anchors, review camera, optional preview lighting.
- **R28:** gameplay route guides, gameplay zones, export classification, performance audit.
- **R29:** controlled optimization based on the real R28 audit.
- **R30+:** visual/world-building passes, collision/export hardening, and larger playable-area expansion.
