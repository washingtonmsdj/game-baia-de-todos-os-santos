# Relatórios do Blender

Esta pasta recebe relatórios exportados das cenas reais do Blender depois que o Codex aplica e valida uma revisão.

O objetivo é permitir que o estado técnico da cena volte para o GitHub em formato legível, sem versionar obrigatoriamente o `.blend` binário.

## Exportação

Use:

```bash
blender cena_r29.blend --background \
  --python tools/blender/export_revision_reports.py \
  -- --output-dir docs/reports/blender/r29
```

No Windows, o comando equivalente pode ser executado em uma única linha.

O exportador gera:

- `scene_summary.json` com contagens gerais, classes da R28, totais de geometria e propriedades de revisão;
- arquivos `.txt` para datablocks internos de auditoria, relatório e README das revisões.

## Fluxo esperado para o Codex

Depois de aplicar uma revisão:

1. reabrir o `.blend` resultante;
2. validar visualmente e verificar o console;
3. executar `export_revision_reports.py`;
4. revisar os arquivos gerados;
5. salvar/commitá-los nesta pasta;
6. atualizar o documento da revisão com as métricas reais obtidas.

Assim, revisões posteriores podem usar dados reais do Blender sem depender de copiar manualmente informações da interface.

## O que não deve ser colocado aqui

- caches grandes;
- renders temporários em massa;
- `.blend` completos sem decisão explícita de versionamento;
- arquivos gerados que contenham caminhos locais sensíveis sem necessidade.
