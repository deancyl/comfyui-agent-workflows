<#
.SYNOPSIS
  ComfyUI Dual-Track Agent Edition - Master Setup & Configuration Script
.DESCRIPTION
  Automates deploying the 17 industrial workflows, custom nodes, stability patches,
  and silent background launchers to any existing ComfyUI directory or clean installation.
.PARAMETER TargetDir
  Target ComfyUI root directory (e.g. C:\Users\deanc\ComfyUI-Zluda or G:\ComfyUI\ComfyUI-aki\...)
.PARAMETER Mode
  "Deploy" (default: sync workflows, nodes, and patches to existing ComfyUI)
  "AMD-ZLUDA" (inject ZLUDA & ROCm 5.7 configuration and silent daemon)
  "All" (full turnkey deployment)
#>

param (
    [string]$TargetDir = "",
    [ValidateSet("Deploy", "AMD-ZLUDA", "All")]
    [string]$Mode = "All"
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ComfyUI Dual-Track Agent Edition Setup & Deployer" -ForegroundColor Cyan
Write-Host "  Repo Root: $RepoRoot" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Resolve Target ComfyUI Directory
if (-not $TargetDir) {
    # Auto-detect common paths
    $commonPaths = @(
        "C:\Users\deanc\ComfyUI-Zluda",
        "G:\ComfyUI\ComfyUI-aki\ComfyUI-aki-v3.2\ComfyUI",
        "..\ComfyUI",
        ".\ComfyUI"
    )
    foreach ($p in $commonPaths) {
        if (Test-Path (Join-Path $p "main.py")) {
            $TargetDir = (Resolve-Path $p).Path
            break
        }
    }
}

if (-not $TargetDir -or -not (Test-Path (Join-Path $TargetDir "main.py"))) {
    Write-Host "`nPlease enter your ComfyUI root directory path (containing main.py):" -ForegroundColor Yellow
    $TargetDir = Read-Host "ComfyUI Root Path"
}

if (-not (Test-Path (Join-Path $TargetDir "main.py"))) {
    Write-Error "Invalid ComfyUI root directory: $TargetDir (main.py not found). Aborting."
    exit 1
}

Write-Host "`n[1/4] Target directory verified: $TargetDir" -ForegroundColor Green

# 2. Deploy 17 Workflows
Write-Host "`n[2/4] Deploying 17 Industrial Dual-Track Workflows..." -ForegroundColor Cyan
$wfDest = Join-Path $TargetDir "user\default\workflows"
if (-not (Test-Path $wfDest)) {
    New-Item -ItemType Directory -Path $wfDest -Force | Out-Null
}
$srcWorkflows = Join-Path $RepoRoot "workflows\*.json"
Copy-Item -Path $srcWorkflows -Destination $wfDest -Force
$wfCount = (Get-ChildItem -Path $wfDest -Filter "*.json").Count
Write-Host "  -> Successfully deployed $wfCount workflows to $wfDest" -ForegroundColor Green

# 3. Deploy Custom Nodes
Write-Host "`n[3/4] Installing Custom Nodes..." -ForegroundColor Cyan
$nodeDest = Join-Path $TargetDir "custom_nodes\ComfyUI-NSFW-Interrogator"
if (-not (Test-Path $nodeDest)) {
    New-Item -ItemType Directory -Path $nodeDest -Force | Out-Null
}
$srcNodes = Join-Path $RepoRoot "custom_nodes\ComfyUI-NSFW-Interrogator\*"
Copy-Item -Path $srcNodes -Destination $nodeDest -Recurse -Force
Write-Host "  -> Successfully installed ComfyUI-NSFW-Interrogator" -ForegroundColor Green

# 4. Apply Patches & Launchers
Write-Host "`n[4/4] Applying Stability Patches & Launchers..." -ForegroundColor Cyan
$pythonExe = Join-Path $TargetDir "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

# Apply LayerNorm and utils patches
$lnPatch = Join-Path $RepoRoot "patches\apply_zluda_ln_patch.py"
$utilsPatch = Join-Path $RepoRoot "patches\patch_utils.py"
if (Test-Path $lnPatch) {
    & $pythonExe $lnPatch $TargetDir
}
if (Test-Path $utilsPatch) {
    & $pythonExe $utilsPatch $TargetDir
}

# Copy launch scripts
$srcZludaScript = Join-Path $RepoRoot "scripts\start_zluda_amd.ps1"
$srcNvidiaScript = Join-Path $RepoRoot "scripts\start_nvidia.bat"
Copy-Item -Path $srcZludaScript -Destination (Join-Path $TargetDir "start_zluda_amd.ps1") -Force
Copy-Item -Path $srcNvidiaScript -Destination (Join-Path $TargetDir "start_nvidia.bat") -Force

# Create launch_gui.vbs in target
$vbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
' 1. Start server silently if not running
WshShell.Run "powershell -NoProfile -ExecutionPolicy Bypass -File ""`$TargetDir\start_zluda_amd.ps1""", 0, False
WScript.Sleep 2000
' 2. Launch edge in app mode
WshShell.Run "msedge.exe --app=http://127.0.0.1:8284", 1, False
"@
$vbsPath = Join-Path $TargetDir "launch_gui.vbs"
Set-Content -Path $vbsPath -Value $vbsContent -Encoding UTF8
Write-Host "  -> Generated desktop zero-console launcher: $vbsPath" -ForegroundColor Green

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  🎉 Setup Completed Successfully!" -ForegroundColor Green
Write-Host "  All 17 workflows, custom nodes, and patches are ready." -ForegroundColor Green
Write-Host "  To launch: double click $vbsPath or run start_zluda_amd.ps1" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
