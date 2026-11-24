<#
.SYNOPSIS
    从 AVGTemplate 初始化一个新的 Ren'Py 项目。
.EXAMPLE
    .\tools\init_project.ps1 -TargetDir "..\MyNewGame" -ProjectCode "MyNewGame" -DisplayName "我的新游戏" -EnglishTitle "MY NEW GAME"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetDir,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$ProjectCode,

    [Parameter(Mandatory = $true)]
    [string]$DisplayName,

    [string]$EnglishTitle = "",
    [string]$JapaneseTitle = "",
    [string]$Version = "0.1.0",
    [string]$PackageId = "",
    [switch]$NoGit
)

$ErrorActionPreference = "Stop"
$TemplateRoot = Split-Path -Parent $PSScriptRoot
$ResolvedTemplate = (Resolve-Path $TemplateRoot).Path

if (-not $EnglishTitle) { $EnglishTitle = $ProjectCode.ToUpperInvariant() }
if (-not $JapaneseTitle) { $JapaneseTitle = $DisplayName }
if (-not $PackageId) {
    $pkgCode = ($ProjectCode -replace '[^A-Za-z0-9]', '').ToLowerInvariant()
    if (-not $pkgCode) { $pkgCode = "avgproject" }
    $PackageId = "org.example.$pkgCode"
}

if (Test-Path $TargetDir) {
    $existing = Get-ChildItem -Force $TargetDir -ErrorAction SilentlyContinue
    if ($existing) {
        throw "目标目录非空：$TargetDir"
    }
} else {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}
$ResolvedTarget = (Resolve-Path $TargetDir).Path

Write-Host "正在从模板初始化项目：$ResolvedTarget" -ForegroundColor Cyan

# 递归复制模板（跳过 .git、缓存、存档、编译产物与构建输出）
$excludeDirs = @(".git", "saves", "cache", "tmp")
Get-ChildItem -Path $ResolvedTemplate -Recurse -Force | ForEach-Object {
    $rel = $_.FullName.Substring($ResolvedTemplate.Length).TrimStart('\', '/')
    if (-not $rel) { return }
    $parts = $rel -split '[\\/]'
    if ($parts | Where-Object { $_ -in $excludeDirs -or $_ -like "*-dists" }) { return }
    if ($_.Extension -in @(".rpyc", ".rpymc", ".rpyb", ".bak", ".new", ".old")) { return }
    if ($rel -in @("log.txt", "errors.txt", "traceback.txt", "files.txt", "image_cache.txt", "save_dump.txt", ".template-lock.json")) { return }

    $destPath = Join-Path $ResolvedTarget $rel
    if ($_.PSIsContainer) {
        New-Item -ItemType Directory -Path $destPath -Force | Out-Null
    } else {
        $parent = Split-Path -Parent $destPath
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
        Copy-Item $_.FullName $destPath -Force
    }
}

# 生成唯一存档后缀
$randSuffix = Get-Random -Minimum 1000000000 -Maximum 2147483647
$saveDir = "$ProjectCode-$randSuffix"

function Escape-RpyString([string]$s) {
    return ($s -replace '\\', '\\\\' -replace '"', '\"')
}

$escDisplay = Escape-RpyString $DisplayName
$escEn = Escape-RpyString $EnglishTitle
$escJa = Escape-RpyString $JapaneseTitle
$escVer = Escape-RpyString $Version
$escCode = Escape-RpyString $ProjectCode
$escSave = Escape-RpyString $saveDir

# 更新 game/project/00_project_config.rpy
$cfgPath = Join-Path $ResolvedTarget "game\project\00_project_config.rpy"
$cfgText = Get-Content $cfgPath -Raw -Encoding UTF8
$cfgText = $cfgText -replace 'define PROJECT_TITLE = _\(".*?"\)', "define PROJECT_TITLE = _(`"$escDisplay`")"
$cfgText = $cfgText -replace 'define PROJECT_TITLE_EN = ".*?"', "define PROJECT_TITLE_EN = `"$escEn`""
$cfgText = $cfgText -replace 'define PROJECT_TITLE_JA = ".*?"', "define PROJECT_TITLE_JA = `"$escJa`""
$cfgText = $cfgText -replace '\(_\("作品名称"\), _\(".*?"\)\)', "(_(`"作品名称`"), _(`"$escDisplay`"))"
[System.IO.File]::WriteAllText($cfgPath, $cfgText, (New-Object System.Text.UTF8Encoding $false))

# 更新 game/project/01_options_project.rpy
$optPath = Join-Path $ResolvedTarget "game\project\01_options_project.rpy"
$optText = Get-Content $optPath -Raw -Encoding UTF8
$optText = $optText -replace 'define config\.name = _\(".*?"\)', "define config.name = _(`"$escDisplay`")"
$optText = $optText -replace 'define build\.name = ".*?"', "define build.name = `"$escCode`""
$optText = $optText -replace 'define config\.version = ".*?"', "define config.version = `"$escVer`""
$optText = $optText -replace 'define config\.save_directory = ".*?"', "define config.save_directory = `"$escSave`""
[System.IO.File]::WriteAllText($optPath, $optText, (New-Object System.Text.UTF8Encoding $false))

# 更新 android.json
$androidPath = Join-Path $ResolvedTarget "android.json"
$androidObj = Get-Content $androidPath -Raw -Encoding UTF8 | ConvertFrom-Json
$androidObj.name = $DisplayName
$androidObj.icon_name = $DisplayName
$androidObj.package = $PackageId
$androidObj.version = $Version
$androidJson = $androidObj | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText($androidPath, $androidJson + "`n", (New-Object System.Text.UTF8Encoding $false))

# 写入 .template-lock.json 记录模板版本与默认上游路径
$manifest = Get-Content (Join-Path $ResolvedTemplate "template.manifest.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$lockObj = [ordered]@{
    template_name    = $manifest.template_name
    template_version = $manifest.template_version
    source           = $ResolvedTemplate
    synced_at        = (Get-Date).ToString("o")
}
$lockPath = Join-Path $ResolvedTarget ".template-lock.json"
[System.IO.File]::WriteAllText($lockPath, ($lockObj | ConvertTo-Json -Depth 4) + "`n", (New-Object System.Text.UTF8Encoding $false))

if (-not $NoGit -and (Get-Command git -ErrorAction SilentlyContinue)) {
    Push-Location $ResolvedTarget
    try {
        git init | Out-Null
        git add -A
        git commit -m "chore: initialize project from AVGTemplate v$($manifest.template_version)" | Out-Null
    } finally {
        Pop-Location
    }
}

Write-Host "项目初始化完成！" -ForegroundColor Green
Write-Host "  目录: $ResolvedTarget"
Write-Host "  存档目录: $saveDir"
Write-Host "  后续模板更新可执行: .\tools\sync_template.ps1"
