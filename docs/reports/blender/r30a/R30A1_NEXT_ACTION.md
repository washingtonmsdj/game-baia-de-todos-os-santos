# Próxima ação após R30A

O commit `a19b4fd` deve ser tratado como diagnóstico válido, mas seus dois principais números de bloqueio precisam ser recalculados antes de qualquer alteração geométrica:

- cobertura DEM `0,1584%`: calculada contra bbox OSM completo inflado por ways que ultrapassam a captura;
- RMS vertical `12,5436`: calculado com seleção contaminada por objetos que não são superfície de terreno.

Executar `docs/CODEX_R30A1_HANDOFF.md`.

Mercado Modelo `59392558` deve ser revisado como conflito de binding por objeto antes de ser interpretado como erro de posição.

Nenhuma geometria deve ser movida apenas com base nos valores da R30A original.
