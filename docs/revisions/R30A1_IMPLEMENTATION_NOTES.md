# R30A.1 — notas de implementação

Esta revisão altera somente a confiabilidade dos diagnósticos.

## Não destrutivo

- não edita `terrain.tif`;
- não corta ou reescreve `map.osm`;
- não move objetos Blender;
- não remove OSM IDs automaticamente;
- não aplica escala/offset Z;
- não altera coastline, vias ou footprints.

## Compatibilidade

- `terrain_samples.json` permanece no schema v1; novos campos de seleção são aditivos;
- `dem_osm_coverage.json` passa para v2, mantendo aliases históricos úteis;
- `scene_reference_alignment.json` passa para v2 e preserva a comparação agregada antiga.
