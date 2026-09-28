# BlendMCP fallback

Este projeto usa OrdaX/Blender Live como rota principal de automacao direta do Blender.

Quando essa rota nao estiver disponivel, o fallback suportado e BlendMCP 1.4.4.

## Estado validado

- pacote Python `blendmcp`: 1.4.4;
- addon Blender: 1.4.4;
- Blender: 5.2.2 LTS;
- porta primaria historica: 9876;
- porta fallback isolada do projeto: 9877;
- cena fallback atual: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a4_semantic_layers.blend`.

A porta 9877 foi escolhida para nao encerrar nem sobrescrever sessoes MCP existentes na 9876.

## Iniciar

```powershell
./scripts/windows/start_blendmcp_fallback.ps1 -Port 9877
```

O launcher abre a cena oficial, inicia diretamente a classe `BlendMCPServer` do addon instalado e valida a conexao antes de retornar sucesso.

## Conectar um cliente MCP

O servidor stdio `blendmcp` deve receber:

```text
BLENDER_HOST=127.0.0.1
BLENDER_PORT=9877
```

O executavel instalado atualmente e:

`C:\Users\TONECOS\AppData\Roaming\Python\Python313\Scripts\blendmcp.exe`

## Healthcheck

```powershell
python tools/blendmcp/healthcheck.py --port 9877 --expect-version 1.4.4 --expect-scene-contains r30a4_semantic_layers
```

O healthcheck valida cena, versao e socket. Se `get_addon_version` nao existir em uma sessao antiga, ele possui fallback somente para diagnostico.

Nao encerrar automaticamente uma sessao Blender MCP que esteja `is_dirty=True`; primeiro preservar/salvar o trabalho ou criar um checkpoint separado.
