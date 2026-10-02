# R30B.04 — entorno imediato do elevador

Arquivo: `blender/salvador_lacerda_r30b04_entorno.blend`. Fonte anterior preservada; não promovido ao runtime.

Escopo passa a incluir calçada, comércio na entrada baixa e proteção da praça superior, aproveitando referências já disponíveis. Evitar microdetalhes internos.

- Guarda-corpo de alvenaria modular sobre a borda existente da praça OSM 1263035782, com intervalo de acesso livre. Perfil de balaústres ainda aproximado (`ADAPT_LOCAL`); não réplica dos vazados da foto.
- Material procedural de pavimento aplicado à praça, sem mudar malha ou cota.
- Pedra portuguesa aplicada a 507 faces já classificadas como passeio no terreno próximo ao acesso baixo e à superfície do caminho OSM 312006925. Sem repintar faces classificadas como pista.
- Depósito Vissor: fachada, molduras, vãos visuais, toldo amarelo e letreiro sobre o bloco OSM 1220650857. Footprint e cotas preservados; alturas e ritmo ainda aproximados. Vãos de loja são representação externa, não interior acessível.
- Demais estabelecimentos, inclusive Cayru, permanecem pendentes de associação confirmada; não atribuir nomes comerciais aos blocos por adivinhação.

Referências enviadas pelo usuário correspondem visualmente aos registros `elevador-lacerda-front-2d9b4031ff6a` (foto baixa, 2025) e `elevador-lacerda-front-97e36e6f289f` (praça, 2015). Originais licenciados já preservados no acervo; não duplicados. Foto de 2015 serve de referência histórica da praça, não prova da configuração atual.

Coleção nova: `ENVIRONMENT_FINAL | entorno Lacerda R30B04`, 31 objetos. Geometria visual separada; colisão das novas proteções não implementada. Cotas/terreno não modificados.

Revisão visual: fachada Vissor conferida na cena; vista da praça na cena completa ainda obstruída por blocos existentes, exigindo revisão estrutural separada. Não interpretar a vista isolada como comprovação do encaixe de toda a cidade. Guias e coleções de referência 01–04, 32–35, 37 e SOURCE_GEOREF ocultadas somente no view layer. Arquivo deixado em vista local para inspecionar praça/elevador.

Script: `automation/blender/refine_lacerda_r30b04_surroundings.py`. Capturas/relatório: `artifacts/lacerda/r30b04_*`. Estado parcial, sem aprovação final de fidelidade.
