# Checklist R30A.1

- [ ] `manifest.json` detectado como fonte dos bounds da captura.
- [ ] Gate DEM recalculado contra `capture_bounds`.
- [ ] Bbox OSM completo preservado apenas para auditoria.
- [ ] `terrain_samples.json` reexportado em modo `strict`.
- [ ] Lista de objetos de terreno revisada antes do fit vertical.
- [ ] Fit vertical reexecutado sem passarela/fachada/torre contaminando a amostra.
- [ ] `scene_reference_alignment.json` regenerado em v2.
- [ ] Bindings conflitantes identificados por objeto.
- [ ] Mercado Modelo `59392558` revisado manualmente.
- [ ] Nenhuma geometria movida com base nos números antigos.
- [ ] Testes/compileall/registro de referências verdes.
