# Critérios de aceitação R30A.1

A revisão é aceita quando:

- o gate DEM usa `capture_bounds` quando o manifest Aleph está disponível;
- a cobertura do DEM é recalculada sem depender do bbox OSM inflado;
- a seleção vertical padrão não inclui objetos apenas por estarem em coleções de terreno;
- a comparação cena↔referência identifica conflitos de binding por objeto;
- os testes automatizados passam;
- nenhuma geometria do jogo é alterada pela revisão diagnóstica.
