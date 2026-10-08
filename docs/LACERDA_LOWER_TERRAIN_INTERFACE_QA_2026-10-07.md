# Interface entre terreno e saguão inferior — controle B97

## Resultado medido

Consulta em modo **somente leitura** na única janela Blender PID 16912, cena
`SALVADOR | ESBOCO OFICIAL`, arquivo
`salvador_lacerda_r30b97_limites_vestibulos_superiores.blend`,
SHA-256 registrado `0454f0cec2d8d65b4f127f635d59a217f4b62bae83d43d5e9769b541581543b5`.
A sessão não apresentava alterações não salvas.

Foram reutilizados os quatro controles `lower_floor` do relatório
`docs/reports/blender/lacerda-lower-structure-b93/application.json` e
a transformação de medição `docs/reports/blender/lacerda-corridor/scene_b78.json`.
Os raios verticais atingiram a malha específica
`MVP | terreno corrigido | colisão estática` no mesmo XY do piso arquitetônico
`INFERIOR | piso do saguão`, cujo topo é aproximadamente Z=11,113008 m.

| Controle | XY mundial | Z terreno B97 | Piso menos terreno |
|---|---|---:|---:|
| 1 | (-31,61979; 39,01907) | 12,051285 | -0,938276 m |
| 2 | (-33,47567; 57,21959) | 7,255676 | +3,857332 m |
| 3 | (-46,45688; 49,55744) | 7,255661 | +3,857347 m |
| 4 | (-39,96627; 53,38852) | 7,255661 | +3,857347 m |

As alturas reproduzem a amostragem da B93, com diferenças de
arredondamento inferiores a 0,00002 m. Estes números são **desníveis de
superfície na mesma coordenada XY**, não prova de que o jogador possa
pisar diretamente de uma malha à outra, nem confirmação do layout real da
entrada. O primeiro controle mostra terreno acima do piso, mas não permite
inferir sozinho uma colisão porque falta validação da superfície caminhável.

## Automação

Após consolidar a autoria B97 no Git LFS, executar na mesma sessão aberta:

```powershell
python tools/blendmcp/run_script.py automation/blender/audit_lower_terrain_interface.py --port 9876 --read-only
```

O script confere arquivo, SHA-256 e a origem autoral declarada; reprojeta
os controles documentais B93, faz raios somente leitura sobre a malha e
calcula classes com `tools/terrain/surface_registration.py`.
O limite de comparação de 0,25 m corresponde à etapa candidata do
personagem proxy e serve para sinalizar necessidade de investigação, **não**
para certificar acessibilidade, malha de colisão ou movimentação contínua.

A B97 está disponível somente no workspace local neste momento; o contrato
de autoria da `main` continua separado. O auditor deve **recusar** rodar se a
cena aberta não corresponder ao ponteiro da branch de autoria em uso.
Não forçar esse guard e não promover a cena automaticamente.

## Decisão técnica

- `ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`.
- `FULL_TOME_MARKET_ROUTE = NOT_APPROVED`.
- `LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`.
- `movement_enabled = false`; produção B30 inalterada.
- Não criar rampa/escada, mover o terreno ou inventar portas para zerar
  a diferença. Primeiro validar os controles de implantação arquitetônica
  com a praça e identificar a entrada física adequada.
- Manter geometria visual, navegação e colisão em camadas distintas.

A documentação e o auditor são instrumentos de QA; não são nova fonte
única de georreferenciamento nem justificativa para liberar o runtime.
