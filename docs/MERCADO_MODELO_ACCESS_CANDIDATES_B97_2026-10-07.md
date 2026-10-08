# Mercado Modelo — aberturas arquitetônicas candidatas (B97)

## Inspeção real e verificável

Na única janela Blender aberta (PID 16912, cena SALVADOR | ESBOCO OFICIAL,
fonte B97), foram encontradas duas aberturas arquitetônicas **visíveis**,
com ombreiras e verga. A cena não tinha alterações não salvas.
As medidas abaixo são **da geometria autoral**, não medidas certificadas
do edifício real nem uma rota de gameplay aprovada.

| Abertura candidata | Centro XY Blender | Vão geométrico projetado | Altura até base da verga |
| --- | --- | ---: | ---: |
| Fachada Praça Cairu | (-126,491974; 154,290283) | 2,75891 m | 4,50 m |
| Fachada posterior | (-96,603867; 184,757965) | 2,131885 m | 4,00 m |

Os dois centros tiveram sondagens verticais positivas contra a malha
TÉRREO | laje e o terreno MVP | terreno corrigido | colisão estática,
com Z aproximadamente 7,25566 m. Os cinco controles por abertura
(-3, -1, 0, +1 e +3 m no normal local) mostraram o piso de mercado
em um lado e o terreno no outro, com cotas próximas onde houve contato.
Isso **não** demonstra o caminho completo, a ausência de obstáculos,
a largura livre após colisores, a existência das portas na edificação
real nem conexão ao último nó de rota do B82.

As peças têm status de fidelidade:
"esboço tipológico; footprint e escala exterior derivados do OSM;
interior sem planta cadastral publicada". Portanto, nenhuma das
aberturas é aprovada como entrada pública real. O objeto
MERCADO MODELO | entrada principal continua oculto na coleção LEGACY,
e **não** foi reativado nem usado como vínculo de navegação.

## Autoridade e execução

A autoridade de locais continua sendo
world/areas/mvp-centro-lacerda/locations.json.
O item mercado-modelo ainda possui blender_binding=null e OSM
way 59392558 com verified=false. Não adicionar segunda tabela
de entradas nem preencher coordenadas geográficas estimadas.

A auditoria somente-leitura automation/blender/audit_market_access.py
descobre as aberturas pelas três partes reais na coleção do Mercado,
compara geometria e níveis nos mesmos XY e submete o resultado a
tools/world/market_access.py. A classificação é sempre candidata,
nunca aprovação de rota; a futura liberação requer evidência arquitetônica
independente, binding geográfico verificado, varredura completa de colisão,
e teste de percurso ponta a ponta com personagem.

A auditoria deve executar apenas com a fonte autoral explícita já
registrada e seu SHA-256 correspondente; caso contrário falha fechada.
O código fica no GitHub para uso após a consolidação da B97 no Git LFS.
Nenhuma alteração do arquivo .blend é necessária para esta auditoria.

## Pendências de jogabilidade

- FULL_TOME_MARKET_ROUTE = NOT_APPROVED.
- MARKET_ENTRANCE_CONNECTOR = NOT_IMPLEMENTED_NOT_TESTABLE.
- LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE.
- ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW.
- Produção continua B30; não promover B97 e não habilitar movement_enabled.
- A tentativa de varredura abrangente de obstáculos do Mercado excedeu
  o tempo de execução; **não** registrar passagem livre como comprovada.

Próximo trabalho: comparar a posição das ombreiras com fontes de
acesso físico verificadas, resolver o binding do Mercado e conferir
uma faixa caminhável contínua desde Cairu por malhas e colisores reais.
