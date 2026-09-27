# Fluxo de Trabalho do Blender

## Objetivo

Este repositório armazena passes reproduzíveis de automação do Blender para o projeto de mundo aberto ambientado em Salvador.

O arquivo `.blend` de trabalho continua sendo a cena-fonte, enquanto os scripts Python em `tools/blender/` descrevem alterações controladas que podem ser aplicadas depois pelo Codex ou por um desenvolvedor executando o Blender localmente.

## Por que este fluxo existe

A cena atual já é grande e possui várias camadas históricas. Ela contém milhares de objetos, geometria de referência importada, estruturas de gameplay, modelos de marcos arquitetônicos, terreno, vias, câmeras e revisões anteriores.

Por isso, qualquer automação deve ser conservadora. Cada script deve realizar uma melhoria específica, registrar o que fez, salvar uma nova revisão e evitar limpezas globais destrutivas sem escopo e validação próprios.

## Regras de revisão

Todo script de revisão deve seguir estas regras:

1. **Nunca sobrescrever o arquivo-fonte por padrão.**
2. Salvar com um novo sufixo, como `_r28.blend`, `_r29.blend` etc.
3. Preferir metadados, coleções, guias, instâncias ou geometria derivada validada em vez de alterações destrutivas.
4. Evitar renomeações em massa, porque nomes de objetos podem ser usados por constraints, drivers, scripts, exportadores ou fluxos manuais.
5. Evitar `Join`, `Decimate`, triangulação, aplicação de transformações ou consolidação de materiais em massa sem uma revisão dedicada e validada.
6. Marcar objetos gerados com prefixo de revisão e/ou propriedades customizadas.
7. Quando possível, permitir remover e reconstruir o conteúdo gerado.
8. Manter geometria OSM/DEM/de referência distinguível da geometria autoral/pronta para jogo.
9. Armazenar um bloco de texto interno no Blender ou metadados da cena descrevendo a revisão.
10. Emitir um resumo útil no console.

## Estrutura sugerida do repositório

```text
tools/blender/
  r27_qa_review.py
  r28_gameplay_export.py
  r29_optimization.py

docs/revisions/
  R27.md
  R28.md
  R29.md
```

## Como o Codex deve aplicar uma revisão do Blender

O Codex deve usar o `.blend` validado mais recente disponível localmente e executar o Blender pela linha de comando, por exemplo:

```bash
blender current_scene.blend --python tools/blender/r28_gameplay_export.py
```

Se o Blender estiver instalado em um caminho não padrão, o Codex deve localizar o executável em vez de modificar o script.

Após a execução, o Codex deve verificar:

- se o Blender terminou sem erro;
- se o novo arquivo `_rXX.blend` esperado foi criado;
- se as coleções/blocos de texto gerados existem;
- se a contagem de objetos não caiu de forma inesperada;
- se nenhum `.blend` de origem foi sobrescrito;
- se o console não contém exceções Python;
- se o arquivo resultante pode ser reaberto.

Em revisões com alterações visuais ou espaciais, o Codex também deve abrir a cena e inspecionar a área afetada antes de considerar a revisão concluída.

## Política para arquivos binários

Arquivos `.blend` ficam ignorados por padrão.

Motivos:

- a cena pode se tornar muito grande;
- Git comum é ineficiente para sucessivas versões de binários grandes;
- arquivos Blender binários não permitem revisão de código útil em texto;
- scripts reproduzíveis são mais valiosos para o handoff entre agentes.

Se no futuro o projeto decidir versionar `.blend`, o Git LFS deve ser configurado de forma intencional e a documentação/`.gitignore` atualizada.

## Política de idioma

O **nome do jogo, Bay of All Saints, permanece em inglês**.

Toda a documentação, handoffs, relatórios e notas de desenvolvimento do repositório devem ser escritos em **português**.

Nomes reais de locais de Salvador devem permanecer com sua grafia oficial em português. Termos técnicos consolidados, nomes de APIs, propriedades, comandos e identificadores de código podem permanecer no idioma exigido pela ferramenta.

## Níveis de segurança

### Seguro / padrão

- criar coleções de guias;
- adicionar helpers que não renderizam;
- adicionar propriedades customizadas;
- gerar relatórios de auditoria;
- adicionar links de coleção para exportação sem remover os originais;
- criar câmeras de revisão;
- criar iluminação opcional de preview;
- salvar uma nova revisão.

### Exige validação

- substituir meshes repetidas por instâncias vinculadas;
- criar meshes de colisão;
- criar LODs;
- consolidar vias por chunks espaciais;
- consolidar materiais;
- aplicar transformações;
- mover objetos entre coleções canônicas.

### Exige aprovação explícita / migração dedicada

- exclusão em massa;
- renomeação em massa;
- junção destrutiva de meshes;
- exclusão de geometria-fonte de referência;
- mudanças no sistema de coordenadas;
- reescala global do mundo;
- reconstrução destrutiva de marcos arquitetônicos.

## Sequência atual

- **R27:** marcadores de QA, câmera de revisão e iluminação opcional de preview.
- **R28:** guias de rota jogável, zonas de gameplay, classificação de exportação e auditoria de performance.
- **R29:** otimização controlada baseada na auditoria real da R28.
- **R30+:** passes visuais/construção de mundo, endurecimento de colisão/exportação e expansão da área jogável.
