# R30A.2 — diagnóstico vertical por domínio

## Objetivo

Resolver o bloqueio vertical restante da R30A.1 sem alterar geometria.

A R30A.1 confirmou:

- cobertura horizontal do DEM: 100% da janela da captura;
- fit XY estável, ainda candidato;
- seleção de terreno limpa para um único objeto de superfície;
- fit vertical ainda insuficiente;
- DEM com valores muito negativos dentro do recorte que inclui a Baía.

A documentação do Mapzen/Tilezen Terrain Tiles informa que ETOPO1 é usado para batimetria oceânica em todos os zooms. Portanto valores negativos na área da Baía podem ser dados válidos de fundo oceânico e não nodata.

## Hipótese a testar

O objeto `MVP | terreno corrigido | colisão estática` abrange ou toca regiões que não devem participar da calibração do relevo terrestre. Misturar batimetria com superfície de solo pode contaminar o fit vertical mesmo após a seleção correta do objeto.

A R30A.2 deve separar os domínios sem apagar dados:

1. todos os valores DEM válidos;
2. DEM abaixo de 0 m — domínio abaixo do nível médio do mar/batimetria;
3. DEM >= 0 m — candidato de superfície terrestre para QA vertical.

O limiar 0 m é semântico (nível médio do mar), não um offset ajustado para melhorar resultado.

## Ferramenta

`tools/terrain/analyze_vertical_domains.py`

Ela:

- reutiliza a mesma transformação XY candidata;
- amostra o mesmo `terrain.tif` original;
- mantém todos os valores negativos no relatório;
- calcula fit robusto completo;
- calcula fit robusto apenas no domínio não negativo;
- gera grade EPSG:3857 de resíduos do domínio terrestre;
- cria fila de células com maior erro para inspeção no Blender;
- não altera DEM, `.blend`, escala, offset ou objetos.

## Grade espacial

Padrão: células de 50 m.

Para cada célula terrestre:

- quantidade de amostras;
- min/max/mediana DEM;
- mediana Z Blender;
- mediana do resíduo;
- mediana absoluta;
- percentil 90 absoluto;
- máximo absoluto.

O threshold padrão de 5 m serve somente para fila de revisão. Ele não define que a geometria está errada e não autoriza correção automática.

## Decisão após execução

Se o fit terrestre melhorar significativamente em relação à R30A.1, usar a grade para localizar discrepâncias reais por região.

Se continuar insuficiente, investigar primeiro:

- erro espacial do fit XY;
- resolução efetiva SRTM/ETOPO1 versus malha local;
- correções históricas introduzidas no terreno do MVP;
- escarpa muito abrupta para a resolução do DEM;
- vertices do terreno que representam plataformas/colisão e não superfície física.

Não ajustar escala Z global enquanto o fit terrestre permanecer insuficiente.

## Critério de conclusão

R30A.2 é diagnóstico concluído quando houver:

- contagem de amostras abaixo/acima do nível do mar;
- fit completo e fit terrestre comparáveis;
- mapa de células residuais;
- principais regiões de discrepância identificadas;
- decisão documentada sobre se o próximo passo é correção local de terreno ou investigação adicional.
