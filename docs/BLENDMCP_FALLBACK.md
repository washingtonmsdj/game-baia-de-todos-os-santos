# BlendMCP fallback

OrdaX/Blender Live é a rota principal de automação direta do Blender. O fallback suportado é **BlendMCP 1.4.4**, mas ele deve compartilhar a mesma janela/processo Blender sempre que a sessão visível já estiver aberta.

## Regra de janela única

- uma única janela do Blender durante alterações de cena;
- OrdaX e BlendMCP podem coexistir no mesmo processo;
- não abrir uma segunda instância para aplicar geometria;
- Blender background/headless fica restrito a validações read-only/CI;
- nunca encerrar uma sessão `is_dirty=True` sem checkpoint/salvamento.

## Estado validado

- `blendmcp`: `1.4.4`;
- Blender: `5.2.2 LTS`;
- porta fallback: `9877`;
- cena validada atual: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a6_collision_chunks.blend`;
- OrdaX e BlendMCP foram testados juntos no mesmo PID Blender.
## Acoplar à janela já aberta

Com a sessão OrdaX visível ativa, executar o script versionado:

`automation/blender/start_blendmcp_server.py`

Ele inicia o `BlendMCPServer` na porta 9877 dentro do processo Blender atual. O healthcheck deve retornar `addon_version=1.4.4` e a cena esperada.

Cliente MCP:

```text
BLENDER_HOST=127.0.0.1
BLENDER_PORT=9877
```

Healthcheck:

```powershell
python tools/blendmcp/healthcheck.py --port 9877 --expect-version 1.4.4
```
## Launcher quando não existe Blender aberto

Somente quando não houver nenhuma janela Blender ativa:

```powershell
./scripts/windows/start_blendmcp_fallback.ps1 -Port 9877
```

O launcher se recusa a abrir uma segunda instância se detectar `blender.exe`. Ele usa a cena oficial mais recente, aguarda até 120 s e grava logs em `artifacts/blendmcp-fallback/`.

## Ordem de preferência

1. uma janela visível com OrdaX + BlendMCP no mesmo processo;
2. se OrdaX falhar, continuar pela porta 9877 já acoplada à mesma janela;
3. se não existir Blender aberto, iniciar uma única janela pelo launcher;
4. usar headless somente para validações que não alterem a cena.

A porta 9876 é histórica e não deve ser usada para matar ou substituir sessões sem inspeção prévia.
