param(
    [string]$BlendFile = "blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a4_semantic_layers.blend",
    [int]$Port = 9877,
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [string]$AddonPath = "$env:APPDATA\Blender Foundation\Blender\5.2\scripts\addons\blendmcp_addon.py"
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$blend = if ([IO.Path]::IsPathRooted($BlendFile)) { $BlendFile } else { Join-Path $repo $BlendFile }
$addon = (Resolve-Path $AddonPath).Path

if (-not (Test-Path $BlenderExe)) { throw "Blender nao encontrado: $BlenderExe" }
if (-not (Test-Path $blend)) { throw "Cena nao encontrada: $blend" }
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    throw "Porta $Port ja esta em uso. Escolha outra porta para o fallback."
}

$bootstrap = Join-Path $repo "automation\blender\start_blendmcp_server.py"
if (-not (Test-Path $bootstrap)) { throw "Bootstrap BlendMCP nao encontrado: $bootstrap" }
$argLine = ('"{0}" --python "{1}" -- --port {2}' -f $blend, $bootstrap, $Port)
$proc = Start-Process -FilePath $BlenderExe -ArgumentList $argLine -PassThru

$health = Join-Path $repo "tools\blendmcp\healthcheck.py"
$deadline = (Get-Date).AddSeconds(45)
$ready = $false
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 750
    & python $health --port $Port --expect-version 1.4.4 --expect-scene-contains ([IO.Path]::GetFileNameWithoutExtension($blend)) *> $null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
}

$result = [ordered]@{
    ok = $ready
    pid = $proc.Id
    port = $Port
    blend_file = $blend
    addon = $addon
    mcp_env = @{ BLENDER_HOST = "127.0.0.1"; BLENDER_PORT = "$Port" }
}
$result | ConvertTo-Json -Depth 4
if (-not $ready) { exit 1 }
