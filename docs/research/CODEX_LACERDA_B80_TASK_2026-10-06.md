# Codex — tarefa B80: validar Lacerda com evidência independente

## Base obrigatória

Trabalhar a partir do estado atual da **B80**, preservando B76, B77B, B78, B79 e B80.

Ler antes de qualquer alteração:

- `docs/LACERDA_CORRIDOR_B80.md` quando disponível no checkout local atual;
- `docs/research/ELEVADOR_LACERDA_EVIDENCE_2026-10-06.md`;
- `docs/research/ELEVADOR_LACERDA_EVIDENCE_2026-10-06.json`;
- política de proveniência existente do projeto.

Se o checkout remoto desta branch não contiver ainda algum relatório B80 que existe somente no workspace local, **não sobrescrever nem reconstruir esse relatório a partir de memória**. Usar o arquivo local canônico e reconciliar antes de qualquer commit futuro.

## Objetivo

Resolver o próximo bloqueio real da B80 por **evidência independente**, não por ajuste visual:

**saguão superior → soleira → abertura → cabine do Elevador Lacerda**, com foco nas 27 testemunhas atuais de interseção sólida do CCD da cabine.

A tarefa desta rodada é primeiro documental/técnica. Não existe autorização automática para criar B81.

## 1. Recuperar evidência de maior qualidade

Tentar obter, em ordem de prioridade:

1. anexos gráficos do processo IPHAN `01502.000406/2001-93` / tombamento `1.497-T-02`;
2. plantas da reforma de 2002 citadas no parecer do IPHAN;
3. Figuras 122, 123 e 124 da dissertação UFBA em resolução suficiente para leitura;
4. projeto executivo completo da restauração/requalificação 2023, desenvolvido por AP Arquitetos Associados e relacionado à Concorrência SUCOP nº 24/2023;
5. levantamento cadastral/diagnóstico usado na intervenção 2023–2025;
6. eventual documentação pública de fabricante/instalador das cabines novas;
7. fontes adicionais oficiais/acadêmicas que contenham planta, corte ou medidas do poço, soleira, cabine e desembarques.

Registrar cada fonte nova com URL/origem, autoria, data, página/prancha, revisão, escala quando disponível, hash local e classe de evidência.

## 2. Classes de evidência

Usar classes equivalentes a:

- `PRIMARY_MEASURED`
- `OFFICIAL_DRAWING`
- `HISTORICAL_DRAWING`
- `OFFICIAL_TEXT`
- `ACADEMIC_SECONDARY`
- `VISUAL_REFERENCE`
- `SCENE_CANDIDATE`
- `UNKNOWN`

Não promover desenho histórico a estado atual sem evidência de continuidade.

## 3. Números históricos: somente diagnóstico

A pesquisa encontrou referências históricas para:

- passadiço: `6,00 × 28,70 m`;
- torre: `73 m` de altura, `7,50 m` de largura e aproximadamente `3,50 m` de comprimento;
- percurso dos ascensores: `59 m`;
- espaçamento estrutural citado: `3,50 m`.

Esses valores **não autorizam**:

- reescalar a cena;
- mover Hero Assets;
- redimensionar cabine;
- recortar lajes;
- fechar retornos/paredes;
- alterar o SSOT.

Comparar o `59 m` histórico com o deslocamento vertical candidato atual apenas como diagnóstico. Explicar qualquer discrepância antes de propor correção.

## 4. Cruzar as 27 testemunhas sólidas

Para cada testemunha sólida do CCD B80, produzir uma triagem rastreável contendo:

- componente móvel envolvido;
- obstáculo/mesh envolvido;
- posição/intervalo do percurso;
- tipo de contato/interseção;
- fonte geométrica da cena;
- evidência independente relevante;
- classificação: `SCENE_ERROR_CONFIRMED`, `CABIN_CANDIDATE_ERROR`, `HISTORICAL_CONFIGURATION`, `CURRENT_CONFIGURATION_SUPPORTED`, `NEEDS_REVIEW` ou `UNKNOWN`;
- correção autorizada, se houver;
- justificativa e fonte.

**Não tratar 27 testemunhas como 27 defeitos arquitetônicos independentes.** Agrupar quando forem manifestações do mesmo conflito estrutural.

## 5. Regra para alteração da cena

Somente modificar geometria se existir evidência independente suficiente para demonstrar que a geometria atual está errada.

Se nenhuma correção estiver comprovada:

- não alterar B80;
- não criar B81 artificialmente;
- entregar somente relatório documental/técnico atualizado;
- manter `movement_enabled: false`.

Se uma ou mais correções forem comprovadas:

- preservar B80 intacta;
- aplicar somente as correções comprovadas;
- registrar antes/depois e fonte de cada alteração;
- criar a próxima revisão apenas após alteração geométrica real;
- repetir CCD integral da cabine;
- repetir sweep volumétrico da cápsula;
- repetir ground-following/apoio;
- manter o gate bloqueado se restar qualquer interseção sólida não explicada.

## 6. Ground-following e apoio

A B80 já removeu os oito trechos superiores com penetração da cápsula. Não desfazer isso.

Os 18 apoios superiores ainda pendentes devem continuar separados de aprovação física. Blender/timeline não substitui gravidade, step, slide e solver real de engine.

Não criar piso invisível ou preencher vão apenas para eliminar um alerta.

## 7. B78

A B78 pode ser usada apenas como comparação histórica da própria evolução da cena.

Não migrar automaticamente as sete alterações de malha da B78. Verificar se alguma delas passa a ser sustentada pela nova evidência; caso contrário, manter `NEEDS_REVIEW`.

## 8. Aleph

Continuar usando Aleph extensivamente como ferramenta de aquisição/referência de desenvolvimento, dentro da política de proveniência já estabelecida.

Pode usar OSM, DEM, satélite, Street View e metadados para investigação e correlação espacial, mas referências temporárias não devem ser silenciosamente promovidas a asset final.

## 9. Escopo bloqueado nesta rodada

Não:

- detalhar Lapa;
- detalhar Dique;
- detalhar Fonte Nova;
- iniciar fachadas cosméticas fora da vertical slice;
- corrigir em massa os alertas 118/234 herdados;
- exportar B80/B81 para produção;
- marcar a viagem como funcional apenas porque a timeline reproduz.

## 10. Saída esperada

Entregar:

1. relatório das fontes novas localizadas;
2. cópia/registro dos desenhos ou referências que possam ser legalmente/versionavelmente preservados;
3. matriz atualizada dos desconhecidos B80;
4. triagem das 27 testemunhas do CCD com justificativa por evidência;
5. lista de correções realmente autorizadas;
6. lista do que continua desconhecido;
7. decisão explícita: `NO_SCENE_CHANGE` ou `GEOMETRY_CHANGE_JUSTIFIED`;
8. se houver mudança geométrica, nova revisão preservando B80 e todos os gates repetidos;
9. se não houver, nenhum novo número de revisão apenas por pesquisa.

Critério de qualidade: **nenhuma geometria deve ser alterada para fazer o teste passar; o teste só passa quando a geometria sustentada pelas fontes realmente passa.**
