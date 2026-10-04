# Oficina da carroceria e portas Hilux

Fonte atual de autoria: a entrada `vehicle-rondesp-pickup` em `catalog.json`.
Arquivo de trabalho V20: `hilux_chapa_v20.blend`. V19, V18, V17 e revisões anteriores
preservadas; a V11 contém o conjunto montado antes desta separação.

A carroceria **HILUX | CARROCERIA PRINCIPAL**, as quatro portas e suas ferragens ficam visíveis. A carroceria é uma malha para a
chapa fixa: capô, para-lamas, colunas, teto, piso da cabine e caçamba aberta.
A cobertura policial sobre a caçamba não faz parte dessa malha.

Editar a metade **+X**, em Edit Mode. O modificador **ESPELHO X** gera o
lado oposto e mantém o centro preso com clipping. A frente do veículo é −Y.
Grupos de vértices identificam as chapas de origem. O cinza da visualização
facilita a leitura da forma; os materiais de pintura foram preservados.

A V18 ajusta as quatro folhas aos vãos e recua a coluna B para dentro da
carroceria. As portas cobrem a estrutura e se encontram externamente numa
junta candidata de 4 mm, conforme a referência `hilux-2024-std-dealer-side`.
Cada folha inclui chapa externa, caixilho, dobra periférica e estrutura interna
com abertura de serviço. A geometria esquerda foi obtida por reflexão da direita;
cada porta mantém malha e movimento independentes. Nomes dos objetos e pivôs
anteriores foram preservados.

Os conjuntos visíveis ficam em **HILUX | PORTAS EM EDICAO**. Selecione o
**RDP01 | Pivô porta dianteira/traseira ±1** no Outliner e ajuste a propriedade
personalizada **abertura_graus**: 0 fecha, 70 abre. Drivers mantêm o sentido
correto em cada lado; maçanetas, caixilhos e vedações acompanham a folha.
As folhas fixas das dobradiças ficam na subcoleção correspondente. A fonte
é salva com os quatro controles em zero. Não mover o pivô ou a folha por
transform para abrir a porta.

Treze poses, incluindo abertura separada das dianteiras e traseiras, não
apresentaram penetração detectada entre folhas ou na carroceria avaliada.
As folhas não apresentaram auto-interseções nos critérios auditados. As
aberturas internas de serviço permanecem abertas de propósito. Folgas,
espessuras, estampagens e eixos são candidatos de modelagem; a amostragem
não certifica todas as posições intermediárias nem os componentes reservados.
Relatório: `docs/reports/blender/hilux_portas_v18.json`.

A V13 reconstrói o painel traseiro da cabine com vão de vidro arredondado,
os cantos da coluna C e o encontro com o teto. A cabeceira da caçamba tem
chapa própria; cabine e caçamba preservam sua junta física dentro da malha
de autoria. Bordas superiores, paredes internas, piso estampado e caixas
de roda foram refeitos, retirando superfícies duplicadas. Retornos antigos
das colunas e da frente foram substituídos; a espessura constante evita
pontas exageradas nas quinas. O vão do vidro permanece aberto nesta oficina.

O atributo de faces `boas_panel_id` e o mapa correspondente no objeto
registram a identidade das chapas após os encontros soldados. Nas próximas
edições, usar também esse atributo: grupos de vértices compartilhados entre
chapas não identificam sozinhos todas as faces de um componente.

A V14 prolonga o para-lama dianteiro até a soleira e substitui o batente A
solto por uma dobra ligada à chapa. A coluna A ganhou largura no plano Y/Z;
a seção B foi suavizada e o batente C recebeu retorno interno. Farol e grade
têm flanges nos encaixes. Tampa da caçamba, face interna e dobras compartilham
a mesma seção; o limite inferior da lateral traseira sobe suavemente e termina
dobrado, sem as pontas antigas. Os encaixes com portas e vidros reservados
precisam ser conferidos quando esses conjuntos forem recolocados.

A V15 substitui a armação da cabine por um contorno lateral contínuo com os
vãos completos das duas portas da metade editável. Teto, colunas A/B/C, cantos
posteriores e painel do vidro traseiro compartilham as bordas antes da solda.
Retornos dos batentes e do para-brisa ligados à armação; perfil das colunas
regularizado, dobra arredondada localizada no encontro teto/lateral e normais
separadas nas dobras internas. A junta física cabine/caçamba permanece aberta
e os demais conjuntos continuam reservados. Contorno e transições finas da
chapa ainda são candidatos, com encaixes a conferir na remontagem.

A V16 refaz a caçamba com estações comuns para lateral, borda, interior,
piso e caixas de roda. Cabeceira ligada à parede e ao piso, com retorno
superior arredondado, fechos laterais e dobra contínua nos recortes de roda.
Lateral externa regularizada; a junta cabine/caçamba e a tampa permanecem.
A borda superior da chapa frontal compartilha o contorno do capô, com a
faixa abaixo regularizada. Cabine e conjuntos reservados foram preservados.
Contornos finos e encaixes das peças reservadas ainda requerem refinamento.

A V17 corrige as conexões efetivas da chapa: cabeceira externa, soleiras,
assoalho posterior e cowl. Compatibiliza as estações da tampa com suas dobras
e elimina a flange duplicada da grade/farol. Para-lama e frente recebem
retopologia localizada, conservando os pontos de controle, para retirar faces
que cruzavam a própria chapa. Retorno frontal segue os contornos comuns da
frente, capô e para-lama; retornos do para-brisa unidos por mitra no canto.
A caçamba termina com folga candidata de 6 mm da face interna da tampa.

A malha base V17 tem 42.610 vértices e 46.278 faces. As auditorias não encontraram
junções com mais de duas faces, orientação incoerente, faces degeneradas ou
duplicadas, arestas soltas, vértices coincidentes ou pontos intermediários
desconectados nas bordas. Não há penetração não local detectada entre chapas,
com contatos de arestas compartilhadas tratados na tolerância de 1 µm.
Vãos, juntas e centro do Mirror continuam abertos na malha de autoria.
A conferência dos conjuntos reservados e da malha avaliada completa por
modificadores permanece fora desta auditoria. Relatório: `hilux_carroceria_v17.json`
em `docs/reports/blender/`.

Rodas, chassi, vidros, interior, capota policial e equipamentos continuam
separados em **RDP01 | PECAS RESERVADAS**, com visibilidade e render desligados.
Caixilhos antigos ficam reservados como legado, substituídos pelas folhas
integradas V18. Abertura das portas está implementada nesta etapa; rodagem e
direção continuam adiadas.

A revisão é candidata de modelagem. O interior da caçamba foi completado
com piso, paredes, bordas e caixas de roda autorais para permitir esse trabalho
sem a capota. Isso não representa medidas confirmadas de fábrica.

Uma malha de autoria pode preservar juntas e ilhas correspondentes a chapas
distintas. Não há união por boolean nem uso dessa malha detalhada como collider.
Não exportar ou integrar a cena isolada como veículo final. Para runtime,
seguir o contrato de produção e restaurar a montagem aprovada.

### Acabamento V19

Cabeceira externa corrigida mantendo o recuo interno da coluna B abaixo do encontro com o teto. Capô com coroamento contínuo e bordas localmente arredondadas. Parâmetros artísticos candidatos, sem pretensão de medida de fábrica. Relatório em `docs/reports/blender/hilux_superficies_v19.json`.

### Espessura e normais V20

A superfície externa editável é preservada: Solidify com offset −1 mantém a espessura para dentro. Normais de alta qualidade e ponderação de normais por área/ângulo corrigem o reflexo sem alterar a malha base. A inspeção comparativa confirmou que o offset 0 da V19 criava a faixa ondulada no encontro traseiro. Portas e rig permanecem independentes; fonte reaberta e três poses conferidas. Acabamento candidato, com vistas próximas em `artifacts/vehicles/rondesp/v20-*.png`.
