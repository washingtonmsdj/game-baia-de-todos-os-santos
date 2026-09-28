# BlendMCP fallback

Este projeto usa OrdaX/Blender Live como rota principal de automação direta do Blender.

Quando essa rota não estiver disponível, o fallback suportado é **BlendMCP 1.4.4**.

## Estado validado

- pacote Python `blendmcp`: `1.4.4`;
- addon Blender: `1.4.4`;
- Blender: `5.2.2 LTS`;
- porta primária histórica: `9876`;
- porta fallback isolada do projeto: `9877`;
- cena validada: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a5_runtime_proxies.blend`.

A porta 9877 evita encerrar ou sobrescrever sessões MCP existentes na 9876.

## Iniciar

```powershell
./scripts/windows/start_blendmcp_fallback.ps1 -Port 9877
```

O launcher abre a cena oficial com `--factory-startup --disable-autoexec`, evitando addons globais duplicados, inicia o `BlendMCPServer` e valida a conexão antes de retornar sucesso.

A cena atual pode levar dezenas de segundos para descomprimir e abrir. O launcher aguarda até 120 segundos e grava logs em:

`artifacts/blendmcp-fallback/`

## Conectar um cliente MCP

O servidor stdio `blendmcp` deve receber:

```text
BLENDER_HOST=127.0.0.1
BLENDER_PORT=9877
```

Executável instalado:

`C:\Users\TONECOS\AppData\Roaming\Python\Python313\Scripts\blendmcp.exe`

## Healthcheck

```powershell
python tools/blendmcp/healthcheck.py \
  --port 9877 \
  --expect-version 1.4.4 \
  --expect-scene-contains r30a5_runtime_proxies
```

O healthcheck valida socket, versão do addon e cena carregada. A rota foi testada com `get_scene_info` e `get_object_info` sobre a R30A.5.

## Segurança operacional

- não encerrar automaticamente uma sessão Blender MCP que esteja `is_dirty=True`;
- preservar a cena anterior antes de qualquer mutação;
- preferir nova revisão `.blend` em vez de sobrescrever uma base validada;
- manter a porta 9877 dedicada ao fallback deste projeto;
- se a porta estiver ocupada por outra sessão, não matar o processo sem identificar sua cena/estado;
- usar scripts versionados para alterações estruturais relevantes.

## Ordem de preferência

1. OrdaX/Blender Live quando disponível;
2. BlendMCP 1.4.4 na porta 9877;
3. Blender CLI/background com scripts versionados para passes determinísticos.

A terceira rota continua válida mesmo sem MCP e foi usada para gerar a R30A.5 de forma reproduzível.
