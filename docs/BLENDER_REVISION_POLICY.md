# Revisões da cidade

Decisão de 02/10/2026. O catálogo distingue histórico, recuperação, trabalho e produção; a quantidade de arquivos não decide a fonte.

| Papel | Revisão | Estado |
| --- | --- | --- |
| Trabalho/modelagem | B38 `salvador_lacerda_r30b38_binding_conceicao.blend` | Candidata: preserva B37, corrige binding de camada e refina colisor local; circuito completo pendente |
| Produção registrada | B30 `salvador_lacerda_r30b30_conexao_real_recorte.blend` | Conferência estrutural localizada; jogabilidade/cidade não aprovadas integralmente |
| Base histórica | B23 `salvador_lacerda_r30b23_fachada_praca.blend` | Antecessora; não reiniciar o trabalho dela |
| Experimentos R30C | `salvador_lacerda_mvp_r30c*.blend` | Rejeitados como base |

A cadeia B23 → B24 → B25 → B26 → B27 → B28 → B29 → B30 → B31 → B32 → B33 → B34 → B35 → B36 → B37 → B38
é documentada em `source_before` nos relatórios de `docs/reports/blender/`.
B24–B30 corrigiram encontro de vias, colisão e borda de terreno. B31 acrescentou
arquitetura sem modificar terreno/ruas. B32 recuperou três corpos e 38 componentes
autorais B23, incluindo toldo, que o passe B31 tinha substituído visualmente por
fachadas piores. B33 preserva essa recuperação e acrescenta três parcelas ao sul
do acesso, sem alterar planta, chão, pistas ou colisor. Não copiar tudo de volta para B23:
isso criaria outro ramo e excluiria correções sucessoras.

## Autoridade por responsabilidade

- `production.json#/world_source`: fonte exclusiva para exportação de produção.
- `blender-revisions.json#/authoring_source`: única candidata para continuar a
  modelagem. Ramo explícito, nunca escolhido por sufixo/mtime/janela aberta.
- `blender-revisions.json#/revisions`: histórico, origem, hashes e evidência.
- `artifacts/blender-sessions/current-session.json`: janela/porta adotadas e
  recuperação local; não é autoridade da cidade nem revisão de produção.
- O pacote do navegador conserva sua própria origem/hash. Abrir outro `.blend`
  não atualiza o jogo; não assumir que o navegador representa a candidata B38.

A B23 aberta na 9876 tinha alterações não salvas. Foi preservada uma cópia de
recuperação em `artifacts/blender-sessions/`, sem sobrescrever a fonte e sem criar
revisão numerada. A comparação do terreno/proxy e dos três edifícios/38 componentes
selecionados não encontrou diferença entre recuperação e B23 salva. Isso não
compara a cena inteira. Diferenças legítimas restantes devem ser incorporadas por objetos/IDs.
Nenhuma revisão foi apagada ou movida nesta organização.

## Entrada única

Adotar somente a janela indicada pelo usuário, sem abrir outra:

```powershell
python tools/blendmcp/run_script.py automation/blender/inspect_authoring_session.py --port 9876 --read-only --adopt-session
```

Abrir o ponteiro de trabalho na mesma janela, preservando sessão suja:

```powershell
python tools/blendmcp/run_script.py automation/blender/open_registered_source.py --port 9876 --source-operation
```

Por padrão, `run_script.py` confere PID/porta adotados, caminho e hash da
candidata antes de editar. B23 ou outra instância são recusadas. `--read-only`
é somente para inspeção sem modificar/salvar a fonte; não usar para contornar
o bloqueio de modelagem. Para abrir/exportar produção usar `--source production`.
O wrapper canônico de exportação permanece `export_active_world.py`.

## Nova revisão

1. Continuar a candidata declarada; preservar anterior.
2. Salvar somente mudança real e registrar origem, mudanças e pendências.
3. Reabrir/conferir e registrar explicitamente o novo ponteiro:

```powershell
python tools/blendmcp/catalog_revisions.py --authoring-file blender/NOVA_REVISAO.blend --parent-file blender/REVISAO_ANTERIOR.blend --evidence docs/reports/blender/RELATORIO.json
```

4. Conferir a candidata reaberta. `open_registered_source.py --source-operation --reopen`
   registra a carga concluída em `artifacts/blender-sessions/last-open.json`.
   Uma chamada com timeout não autoriza repetir a alteração: primeiro inspecionar.
5. Promover caminho/hash em `production.json` só após a revisão exigida.
6. Atualizar status/handoff no mesmo ciclo; exportar quando a etapa pedir.

## Preservação por componente

Antes de substituir uma fachada, conferir o objeto e seus componentes existentes
pelo ID explícito. Um gerador novo não é motivo para esconder modelagem melhor.
Registrar o motivo e preservar a base. Comparar geometria, transforms e materiais
dos componentes fora do escopo, além da revisão visual dos alterados.

`component_fingerprint.py` e os relatórios B32/B33 registram a preservação do
terreno/colisor B30 e da modelagem B23 recuperada. Essa conferência localizada
não substitui avaliação arquitetônica ou teste dinâmico de carros.

O guard foi exercitado com B23 aberta e recusou a chamada antes de executar o
script. Sem npm, build, CI ou testes gerais nesta organização. A B33 ainda não
é exterior final aprovado e não foi exportada ao runtime. A B30 não aprova
o circuito da Conceição ou a circulação do ônibus.

## Passe arquitetônico B34

Nove fotos do usuário: uso interno, sem texturas fotográficas. Planta do palácio
preservada; alturas/profundidades candidatas. Galerias alinhadas aos controles
herdados, extensão parcial. A contenção exigiu duas correções locais de perfil
no terreno/proxy, com lajes e colisores separados mantendo o piso da praça.
Não tratar como aprovação geral do relevo ou gameplay. Detalhes/recuperação e
conferência em `palacio_rio_branco_r30b34.json`. Preservar B33 e o backup local
pré-refinamento; não reexecutar passes já aplicados para apenas trocar número.
