param(
    [string]$BlendFile = "blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a6_collision_chunks.blend",
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
$existingBlender = Get-Process blender -ErrorAction SilentlyContinue
if ($existingBlender) {
    throw "Ja existe uma janela do Blender aberta. Nao abra uma segunda instancia; use o BlendMCP acoplado a janela atual ou feche-a conscientemente antes do fallback."
}
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    throw "Porta $Port ja esta em uso. Escolha outra porta para o fallback."
}

$bootstrap = Join-Path $repo "automation\blender\start_blendmcp_server.py"
if (-not (Test-Path $bootstrap)) { throw "Bootstrap BlendMCP nao encontrado: $bootstrap" }
$logDir = Join-Path $repo "artifacts\blendmcp-fallback"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stdout = Join-Path $logDir "blendmcp-$Port.stdout.log"
$stderr = Join-Path $logDir "blendmcp-$Port.stderr.log"
Remove-Item $stdout,$stderr -Force -ErrorAction SilentlyContinue
$argLine = ('--factory-startup --disable-autoexec "{0}" --python "{1}"' -f $blend, $bootstrap)
$previousPort = $env:BOAS_BLENDMCP_PORT
$env:BOAS_BLENDMCP_PORT = [string]$Port
$proc = Start-Process -FilePath $BlenderExe -ArgumentList $argLine -PassThru `
    -RedirectStandardOutput $stdout -RedirectStandardError $stderr
if ($null -eq $previousPort) { Remove-Item Env:BOAS_BLENDMCP_PORT -ErrorAction SilentlyContinue } else { $env:BOAS_BLENDMCP_PORT = $previousPort }

$health = Join-Path $repo "tools\blendmcp\healthcheck.py"
$deadline = (Get-Date).AddSeconds(120)
$ready = $false
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 750
    & python $health --port $Port --expect-version 1.4.4 --expect-scene-contains ([IO.Path]::GetFileNameWithoutExtension($blend)) *> $null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    if ($proc.HasExited) { break }
}

$result = [ordered]@{
    ok = $ready
    pid = $proc.Id
    port = $Port
    blend_file = $blend
    addon = $addon
    stdout_log = $stdout
    stderr_log = $stderr
    process_exited = $proc.HasExited
    exit_code = if ($proc.HasExited) { $proc.ExitCode } else { $null }
    mcp_env = @{ BLENDER_HOST = "127.0.0.1"; BLENDER_PORT = "$Port" }
}
$result | ConvertTo-Json -Depth 4
if (-not $ready) { exit 1 }
