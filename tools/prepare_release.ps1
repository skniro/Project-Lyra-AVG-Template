<#
.SYNOPSIS
    发布前检查、字节码编译、Lint 验证与可选多平台打包脚本。
.EXAMPLE
    .\tools\prepare_release.ps1
    .\tools\prepare_release.ps1 -Clean -Distribute -Packages @("pc","mac")
#>
[CmdletBinding()]
param(
    [string]$ProjectDir = "",
    [string]$RenpyExe = "",
    [switch]$Clean,
    [switch]$Distribute,
    [string[]]$Packages = @("pc", "mac"),
    [string]$Destination = ""
)

$ErrorActionPreference = "Stop"

if (-not $ProjectDir) {
    $ProjectDir = Split-Path -Parent $PSScriptRoot
}
$ResolvedProject = (Resolve-Path $ProjectDir).Path

function Find-RenpyExe([string]$explicit) {
    if ($explicit -and (Test-Path $explicit)) { return (Resolve-Path $explicit).Path }
    if ($env:RENPY_EXE -and (Test-Path $env:RENPY_EXE)) { return (Resolve-Path $env:RENPY_EXE).Path }
    $cmd = Get-Command renpy.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $candidates = @(
        "D:\Program_Files\renpy-8.5.3-sdk\renpy.exe",
        "C:\renpy\renpy.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    $found = Get-ChildItem -Path "C:\", "D:\", "G:\" -Filter "renpy.exe" -Recurse -Depth 3 -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { return $found.FullName }
    throw "未找到 renpy.exe，请通过 -RenpyExe 或 `$env:RENPY_EXE 指定。"
}

$RenpyPath = Find-RenpyExe $RenpyExe
$SdkRoot = Split-Path -Parent $RenpyPath
$LauncherDir = Join-Path $SdkRoot "launcher"
Write-Host "使用 Ren'Py SDK: $RenpyPath" -ForegroundColor Cyan

# 1. 基础项目标识检查
$optProj = Join-Path $ResolvedProject "game\project\01_options_project.rpy"
$issues = @()
if (Test-Path $optProj) {
    $optText = Get-Content $optProj -Raw -Encoding UTF8
    if ($optText -match 'AVGProject-0000000000') {
        $issues += "game/project/01_options_project.rpy 中的 config.save_directory 仍为模板占位值 AVGProject-0000000000。"
    }
    if ($optText -match 'define build\.name = "AVGProject"') {
        $issues += "game/project/01_options_project.rpy 中的 build.name 仍为模板占位值 AVGProject。"
    }
}
$savesDir = Join-Path $ResolvedProject "game\saves"
if (Test-Path $savesDir) {
    $saveFiles = Get-ChildItem $savesDir -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -eq ".save" }
    if ($saveFiles) {
        $issues += "game/saves/ 中存在 $($saveFiles.Count) 个开发期存档文件（打包配置已默认排除，仍建议定期清理）。"
    }
}

if ($issues.Count -gt 0) {
    Write-Host "发布前检查发现提醒项：" -ForegroundColor Yellow
    foreach ($i in $issues) { Write-Host "  - $i" -ForegroundColor Yellow }
}

# 2. 清理缓存与旧编译产物
if ($Clean) {
    Write-Host "正在清理 game/cache 与旧 .rpyc/.rpymc..." -ForegroundColor Cyan
    $cacheDir = Join-Path $ResolvedProject "game\cache"
    if (Test-Path $cacheDir) { Remove-Item -Recurse -Force $cacheDir }
    Get-ChildItem -Path (Join-Path $ResolvedProject "game") -Recurse -Include *.rpyc,*.rpymc -File -ErrorAction SilentlyContinue | Remove-Item -Force
}

# 3. 执行 compile 与 lint
Write-Host "正在编译脚本 (renpy compile)..." -ForegroundColor Cyan
$compileOut = & $RenpyPath $ResolvedProject compile | Out-String
if ($LASTEXITCODE -ne 0) {
    Write-Host $compileOut
    throw "Ren'Py compile 失败 (exit=$LASTEXITCODE)"
}

Write-Host "正在执行静态检查 (renpy lint)..." -ForegroundColor Cyan
$lintOut = & $RenpyPath $ResolvedProject lint | Out-String
Write-Host $lintOut
if ($LASTEXITCODE -ne 0 -or $lintOut -match '(?m)^(Traceback|Full traceback|Exception:)') {
    throw "Ren'Py lint 发现异常或失败 (exit=$LASTEXITCODE)"
}

# 4. 可选多平台打包
if ($Distribute) {
    if (-not (Test-Path $LauncherDir)) {
        throw "未找到 Ren'Py launcher 目录：$LauncherDir"
    }
    $distArgs = @($LauncherDir, "distribute", "--no-update")
    foreach ($pkg in $Packages) {
        $distArgs += @("--package", $pkg)
    }
    if ($Destination) {
        $distArgs += @("--destination", $Destination)
    }
    $distArgs += $ResolvedProject
    Write-Host "正在打包发布版 ($($Packages -join ', '))..." -ForegroundColor Cyan
    $distOut = & $RenpyPath @distArgs | Out-String
    Write-Host $distOut
    if ($LASTEXITCODE -ne 0) {
        throw "Ren'Py distribute 失败 (exit=$LASTEXITCODE)"
    }
}

Write-Host "发布检查与构建流程完成。" -ForegroundColor Green
