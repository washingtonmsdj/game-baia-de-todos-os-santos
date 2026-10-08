# Integridade de revisões Blender — auditoria de 07/10/2026

## Escopo e autoridade

Esta verificação fortalece a política de revisões Blender. O contrato de produção continua em world/areas/mvp-centro-lacerda/production.json; o catálogo blender-revisions.json é a autoridade para escolher a fonte de autoria. Não usar nome, maior número, data ou janela aberta para promover arquivos.

### Auditor de pré-voo

Executar:

    python tools/blender/audit_authoring_inventory.py
    python tools/blender/audit_authoring_inventory.py --require-tracked

O script **somente lê** o repositório: compara os SHA-256 reais das fontes explícitas de produção e autoria, confirma a existência de parent/evidência, protege contra caminhos externos e detecta ponteiros LFS não materializados. A segunda forma também bloqueia referências ainda não versionadas. Retorna JSON com passed, issues e warnings; código de saída 2 significa gate não satisfeito. Não cria revisão, altera arquivos .blend, gera GLB ou modifica o Blender.

## Evidências verificadas na máquina de autoria

- Fonte de produção B30: SHA-256 **confere** com o contrato; continua em produção.
- Fonte de autoria B97: SHA-256 **confere** com o catálogo local, valor 0454f0cec2d8d65b4f127f635d59a217f4b62bae83d43d5e9769b541581543b5; **não** está pronta para produção.
- **Dívida de publicação:** B97, seu parent B96 e o relatório de evidência estão presentes no disco, mas ainda não fazem parte da branch versionada. Não reescrever o catálogo da main para apontar para uma fonte remota inexistente.
- Há 98 cenas locais do padrão salvador_lacerda_r30b*.blend, ocupando cerca de 6,7 GiB. Não subir todas indiscriminadamente, não removê-las e não refazer trabalho já concluído.
- O Blender aberto permanece sob outra sessão e não é manipulado por este auditor.

## Correção pontual de LFS

O GLB do ônibus Torino em prototypes/threejs-water-lab/public/assets/vehicles/torino-31065/onibus_torino_31065_v03.glb estava armazenado como blob Git normal, embora tenha filter=lfs. A regularização nesta branch é **aditiva ao histórico**: seu índice passa a conter ponteiro Git LFS de 132 bytes, size 4666548, com OID f3f9be5e2b6df944677348ead51f4a96d4607933f594dcfff60ba45a752a7eb7. O hash SHA-256 e os bytes no arquivo de trabalho permaneceram iguais antes/depois. Nenhum GLB foi reexportado ou recriado.

## Pendências do MVP

A B97 é candidata arquitetônica. Permanecem LACERDA_VERTICAL=BLOCKED_EXTERNAL_EVIDENCE, 27 testemunhas da B80 não resolvidas, rota física Tomé–Mercado não certificada e expansão em greybox. O controle de integridade **não** substitui testes de deslocamento/colisão, georreferenciamento ou avaliação visual. Seguir a issue #24 para publicar B42–B97 em etapas validadas, com rastreabilidade e gates.
