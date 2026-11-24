<#
.SYNOPSIS
    从 AVGTemplate 上游同步模板核心更新到当前开发中的项目，不覆盖项目配置、剧情与素材。
.EXAMPLE
    .\tools\sync_template.ps1 -DryRun
    .\tools\sync_template.ps1 -Source "G:\new game\Project Lyra\renpy\AVGTemplate"
    .\tools\sync_template.ps1 -Source "https://github.com/yourname/AVGTemplate.git" -Branch "main"
#>
[CmdletBinding()]
param(
    [string]$Source = "",
    [string]$Branch = "",
    [string]$ProjectDir = "",
    [switch]$IncludeSeedMissing,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not $ProjectDir) {
    $ProjectDir = Split-Path -Parent $PSScriptRoot
}
$ResolvedProject = (Resolve-Path $ProjectDir).Path
$LockPath = Join-Path $ResolvedProject ".template-lock.json"

if (-not $Source) {
    if (Test-Path $LockPath) {
        $lock = Get-Content $LockPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($lock.source) { $Source = $lock.source }
    }
    if (-not $Source) {
        $sibling = Join-Path (Split-Path -Parent $ResolvedProject) "AVGTemplate"
        if (Test-Path $sibling) { $Source = $sibling }
    }
}
if (-not $Source) {
    throw "未指定模板源 (-Source)，且未找到 .template-lock.json 或同级 AVGTemplate 目录。"
}

$TempCloneDir = $null
try {
    $ResolvedSource = $Source
    if ($Source -match '^(https?://|git@|ssh://)' -or $Source.EndsWith('.git')) {
        if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
            throw "需要 git 才能从远程仓库拉取模板：$Source"
        }
        $TempCloneDir = Join-Path ([System.IO.Path]::GetTempPath()) ("avgtemplate-sync-" + [guid]::NewGuid().ToString("N"))
        $cloneArgs = @("clone", "--depth", "1")
        if ($Branch) { $cloneArgs += @("--branch", $Branch) }
        $cloneArgs += @($Source, $TempCloneDir)
        Write-Host "正在拉取模板仓库：$Source" -ForegroundColor Cyan
        & git @cloneArgs
        if ($LASTEXITCODE -ne 0) { throw "git clone 失败。" }
        $ResolvedSource = $TempCloneDir
    } else {
        $ResolvedSource = (Resolve-Path $Source).Path
    }

    if ($ResolvedSource -eq $ResolvedProject) {
        throw "模板源与目标项目是同一个目录：$ResolvedProject"
    }

    $ManifestPath = Join-Path $ResolvedSource "template.manifest.json"
    if (-not (Test-Path $ManifestPath)) {
        throw "模板源缺少 template.manifest.json：$ResolvedSource"
    }
    $Manifest = Get-Content $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json

    function Convert-GlobToRegex([string]$glob) {
        $norm = ($glob -replace '\\', '/').TrimStart('/')
        $escaped = [regex]::Escape($norm)
        $escaped = $escaped -replace '\\\*\\\*/', '(?:.+/)?'
        $escaped = $escaped -replace '\\\*\\\*', '.*'
        $escaped = $escaped -replace '\\\*', '[^/]*'
        return '^' + $escaped + '$'
    }

    function Test-MatchPatterns([string]$relUnix, [string[]]$patterns) {
        foreach ($p in $patterns) {
            $rx = Convert-GlobToRegex $p
            if ($relUnix -match $rx) { return $true }
        }
        return $false
    }

    $managedPatterns = @()
    $managedPatterns += $Manifest.template_owned
    $managedPatterns += $Manifest.tools_owned
    $seedPatterns = @($Manifest.seed_only)

    $sourceFiles = Get-ChildItem -Path $ResolvedSource -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($ResolvedSource.Length).TrimStart('\', '/').Replace('\', '/')
        [PSCustomObject]@{ FullName = $_.FullName; Rel = $rel }
    }

    $syncedFiles = New-Object System.Collections.Generic.HashSet[string]
    $copiedCount = 0
    $unchangedCount = 0
    $seededCount = 0

    foreach ($sf in $sourceFiles) {
        $rel = $sf.Rel
        if ($rel -like ".git/*" -or $rel -like "game/saves/*" -or $rel -like "game/cache/*") { continue }
        if ($rel -like "*.rpyc" -or $rel -like "*.rpymc") { continue }

        $isSeed = Test-MatchPatterns $rel $seedPatterns
        $isManaged = (-not $isSeed) -and (Test-MatchPatterns $rel $managedPatterns)

        if (-not $isManaged) {
            if ($IncludeSeedMissing -and $isSeed) {
                $dest = Join-Path $ResolvedProject ($rel -replace '/', '\')
                if (-not (Test-Path $dest)) {
                    Write-Host "[SEED+] $rel" -ForegroundColor Yellow
                    if (-not $DryRun) {
                        New-Item -ItemType Directory -Path (Split-Path -Parent $dest) -Force | Out-Null
                        Copy-Item $sf.FullName $dest -Force
                    }
                    $seededCount++
                }
            }
            continue
        }

        [void]$syncedFiles.Add($rel)
        $dest = Join-Path $ResolvedProject ($rel -replace '/', '\')
        $needCopy = $true
        if (Test-Path $dest) {
            $h1 = (Get-FileHash $sf.FullName -Algorithm SHA256).Hash
            $h2 = (Get-FileHash $dest -Algorithm SHA256).Hash
            if ($h1 -eq $h2) {
                $needCopy = $false
                $unchangedCount++
            }
        }

        if ($needCopy) {
            $tag = if (Test-Path $dest) { "[UPDATE]" } else { "[ADD]   " }
            Write-Host "$tag $rel" -ForegroundColor Green
            if (-not $DryRun) {
                New-Item -ItemType Directory -Path (Split-Path -Parent $dest) -Force | Out-Null
                Copy-Item $sf.FullName $dest -Force
            }
            $copiedCount++
        }
    }

    # 清理模板核心目录中已被上游移除的旧文件（仅限 managed_sync_clean_dirs）
    $removedCount = 0
    foreach ($cleanDir in $Manifest.managed_sync_clean_dirs) {
        $targetDir = Join-Path $ResolvedProject ($cleanDir -replace '/', '\')
        if (-not (Test-Path $targetDir)) { continue }
        Get-ChildItem -Path $targetDir -Recurse -File | ForEach-Object {
            $rel = $_.FullName.Substring($ResolvedProject.Length).TrimStart('\', '/').Replace('\', '/')
            if ($rel -like "*.rpyc" -or $rel -like "*.rpymc") { return }
            if (-not $syncedFiles.Contains($rel)) {
                Write-Host "[REMOVE] $rel" -ForegroundColor DarkYellow
                if (-not $DryRun) {
                    Remove-Item $_.FullName -Force
                }
                $removedCount++
            }
        }
    }

    # 删除已更新或核心目录中的旧 .rpyc / .rpymc，避免 Ren'Py 读取过时字节码
    if (-not $DryRun -and ($copiedCount -gt 0 -or $removedCount -gt 0)) {
        Get-ChildItem -Path (Join-Path $ResolvedProject "game") -Recurse -Include *.rpyc,*.rpymc -File -ErrorAction SilentlyContinue | Remove-Item -Force
        $newLock = [ordered]@{
            template_name    = $Manifest.template_name
            template_version = $Manifest.template_version
            source           = $Source
            synced_at        = (Get-Date).ToString("o")
        }
        [System.IO.File]::WriteAllText($LockPath, ($newLock | ConvertTo-Json -Depth 4) + "`n", (New-Object System.Text.UTF8Encoding $false))
    }

    Write-Host ""
    Write-Host "同步汇总 ($($Manifest.template_name) v$($Manifest.template_version))$(if ($DryRun) { ' [DRY-RUN]' }):" -ForegroundColor Cyan
    Write-Host "  更新/新增: $copiedCount 个文件"
    Write-Host "  未变更:    $unchangedCount 个文件"
    Write-Host "  清理过时:  $removedCount 个文件"
    if ($IncludeSeedMissing) { Write-Host "  补全缺失种子: $seededCount 个文件" }
} finally {
    if ($TempCloneDir -and (Test-Path $TempCloneDir)) {
        Remove-Item -Recurse -Force $TempCloneDir -ErrorAction SilentlyContinue
    }
}
