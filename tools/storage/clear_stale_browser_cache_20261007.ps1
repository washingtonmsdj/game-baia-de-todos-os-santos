$ErrorActionPreference = 'Stop'
$taskCacheRoot = [System.IO.Path]::GetFullPath('C:/Users/TONECOS/AppData/Local/Google/Chrome/User Data')
$taskWorkspace = [System.IO.Path]::GetFullPath('C:/Users/TONECOS/Documents/github/game-baia-de-todos-os-santos')
$taskCutoff = (Get-Date).AddDays(-2)
$taskDeleted = [System.Collections.Generic.List[object]]::new()
$taskSkipped = 0
$taskFreeBefore = [System.IO.DriveInfo]::new('C:/').AvailableFreeSpace
foreach ($taskProfile in Get-ChildItem -LiteralPath $taskCacheRoot -Directory) {
    if ($taskProfile.Name -notmatch '^(Default|Profile [0-9]+)$') { continue }
    $taskCachePath = [System.IO.Path]::GetFullPath((Join-Path $taskProfile.FullName 'Cache/Cache_Data'))
    if (-not $taskCachePath.StartsWith($taskCacheRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Cache fora do diretório permitido' }
    if (-not (Test-Path -LiteralPath $taskCachePath -PathType Container)) { continue }
    foreach ($taskFile in Get-ChildItem -LiteralPath $taskCachePath -File) {
        if ($taskFile.Name -notmatch '^f_[0-9a-f]+$' -or $taskFile.LastWriteTime -ge $taskCutoff) { continue }
        $taskTarget = [System.IO.Path]::GetFullPath($taskFile.FullName)
        if (-not $taskTarget.StartsWith($taskCachePath + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Arquivo fora do cache verificado' }
        try {
            Remove-Item -LiteralPath $taskTarget -ErrorAction Stop
            $taskDeleted.Add(@{ file=$taskTarget.Substring($taskCacheRoot.Length+1); bytes=$taskFile.Length; modified=$taskFile.LastWriteTime.ToString('o') })
        } catch { $taskSkipped++ }
    }
}
$taskReport = @{
    schema='boas/stale-browser-cache-cleanup-v1'; scope='Somente corpos f_hex de cache Chrome anteriores a 48h; sem perfis, histórico, cookies, índices, cenas ou referências';
    cutoff=$taskCutoff.ToString('o'); files=$taskDeleted; deleted_bytes=($taskDeleted | Measure-Object -Property bytes -Sum).Sum;
    skipped=$taskSkipped; free_before=$taskFreeBefore; free_after=[System.IO.DriveInfo]::new('C:/').AvailableFreeSpace
}
$taskReportPath = Join-Path $taskWorkspace 'docs/reports/storage/stale-browser-cache-20261007.json'
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($taskReportPath)) | Out-Null
$taskReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $taskReportPath -Encoding UTF8
$taskReport | Select-Object deleted_bytes,free_before,free_after,skipped | ConvertTo-Json
