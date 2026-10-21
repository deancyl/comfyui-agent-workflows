<#
.SYNOPSIS
  ComfyUI Silent Daemon Startup Script for AMD Radeon 780M / RDNA3 (gfx1103) with ZLUDA & ROCm 5.7
.DESCRIPTION
  Configures tensile library routing, low-vram offload buffers, disables unstable layer norms,
  and launches ComfyUI via ZLUDA without console popups.
#>

param (
    [string]$ComfyDir = "C:\Users\deanc\ComfyUI-Zluda",
    [string]$Port = "8284",
    [switch]$Foreground
)

Set-Location $ComfyDir

# 1. Hardware & Environment paths
$env:HIP_PATH = "C:\Program Files\AMD\ROCm\5.7\"
$env:ROCBLAS_TENSILE_LIBPATH = Join-Path $ComfyDir "gfx1103_libs\library"
$env:PATH = (Join-Path $ComfyDir "zluda") + ";C:\Program Files\AMD\ROCm\5.7\bin;" + $env:PATH

# 2. Stability & Logging flags
$env:ZLUDA_COMGR_LOG_LEVEL = "1"
$env:MIOPEN_FIND_MODE = "2"
$env:MIOPEN_LOG_LEVEL = "3"
$env:TORCH_BACKENDS_CUDNN_ENABLED = "0"
$env:TORCH_COMPILE_DISABLE = "1"
$env:COMFYUI_PORT = $Port

$pythonExe = Join-Path $ComfyDir "venv\Scripts\python.exe"
$zludaExe = Join-Path $ComfyDir "zluda\zluda.exe"

$argsList = @(
    "--",
    $pythonExe,
    "main.py",
    "--port", $Port,
    "--disable-auto-launch",
    "--cpu-vae",
    "--use-pytorch-cross-attention",
    "--disable-comfy-compiler",
    "--reserve-vram", "0.9",
    "--disable-async-offload",
    "--disable-pinned-memory"
)

Write-Host "[AMD 780M / ZLUDA] Starting ComfyUI server on port $Port..."
Write-Host "[AMD 780M / ZLUDA] VRAM optimization: --cpu-vae --reserve-vram 0.9"

if ($Foreground) {
    & $zludaExe @argsList
} else {
    # Silent background launch
    Start-Process -FilePath $zludaExe -ArgumentList $argsList -WindowStyle Hidden
    Write-Host "[AMD 780M / ZLUDA] ComfyUI process spawned silently in background."
}
