<#
.SYNOPSIS
  ComfyUI Dual-Track Agent Edition - Automated Model Downloader
.DESCRIPTION
  Downloads essential SD 1.5 checkpoints, LoRAs, VAE, and ControlNets directly
  from official HuggingFace repositories with resume support.
.PARAMETER TargetDir
  Target ComfyUI root directory.
.PARAMETER SkipOptional
  If set, only downloads core base models (Anything V5, Realistic Vision, more_details, VAE).
#>

param (
    [string]$TargetDir = "C:\Users\deanc\ComfyUI-Zluda",
    [switch]$SkipOptional
)

if (-not (Test-Path (Join-Path $TargetDir "models"))) {
    Write-Error "Invalid ComfyUI directory: $TargetDir (models folder missing)."
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ComfyUI Dual-Track Edition Model Downloader" -ForegroundColor Cyan
Write-Host "  Target ComfyUI: $TargetDir" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan

function Download-ModelFile {
    param (
        [string]$Url,
        [string]$DestFolder,
        [string]$FileName
    )
    $destPath = Join-Path $DestFolder $FileName
    if (Test-Path $destPath) {
        $size = (Get-Item $destPath).Length
        if ($size -gt 1000000) {
            Write-Host "  [Exists] $FileName ($([math]::Round($size/1MB, 1)) MB), skipping." -ForegroundColor Gray
            return
        }
    }
    if (-not (Test-Path $DestFolder)) {
        New-Item -ItemType Directory -Path $DestFolder -Force | Out-Null
    }
    Write-Host "  [Downloading] $FileName..." -ForegroundColor Yellow
    # Use curl with resume support
    curl.exe -C - -L --ssl-no-revoke "$Url" -o "$destPath"
    if (Test-Path $destPath) {
        Write-Host "  [Completed] $FileName" -ForegroundColor Green
    } else {
        Write-Host "  [Failed] Could not download $FileName" -ForegroundColor Red
    }
}

$ckptDir = Join-Path $TargetDir "models\checkpoints"
$vaeDir = Join-Path $TargetDir "models\vae"
$loraDir = Join-Path $TargetDir "models\loras"
$cnetDir = Join-Path $TargetDir "models\controlnet"

# 1. Base Checkpoints
Write-Host "`n[1/4] Checkpoints (Base Models)..." -ForegroundColor Cyan
Download-ModelFile "https://huggingface.co/ckpt/anything-v5.0/resolve/main/AnythingV5_PrtRE.safetensors" $ckptDir "anything-v5-PrtRE.safetensors"
Download-ModelFile "https://huggingface.co/SG161222/Realistic_Vision_V6.0_B1_noVAE/resolve/main/Realistic_Vision_V6.0_NV_B1.safetensors" $ckptDir "realisticVisionV60B1_v51VAE.safetensors"

# 2. VAE
Write-Host "`n[2/4] High-Precision VAE..." -ForegroundColor Cyan
Download-ModelFile "https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors" $vaeDir "vae-ft-mse-840000-ema-pruned.safetensors"

# 3. LoRAs
Write-Host "`n[3/4] High-Detail & Style LoRAs..." -ForegroundColor Cyan
Download-ModelFile "https://huggingface.co/latent-cat/more_details/resolve/main/more_details.safetensors" $loraDir "more_details.safetensors"
Download-ModelFile "https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SD15-8steps-CFG-lora.safetensors" $loraDir "Hyper-SD15-8steps-CFG-lora.safetensors"

if (-not $SkipOptional) {
    Download-ModelFile "https://huggingface.co/stablediffusionapi/korean-doll-likeness/resolve/main/koreanDollLikeness_v15.safetensors" $loraDir "KoreanDollLikeness_v15.safetensors"
    Download-ModelFile "https://huggingface.co/fuxin/ghibli-style-offset/resolve/main/ghibli_style_offset.safetensors" $loraDir "ghibli_style_offset.safetensors"
    Download-ModelFile "https://huggingface.co/Norod78/anime-lora-makoto-shinkai-anime-style/resolve/main/anime-lora-makoto-shinkai-anime-style.safetensors" $loraDir "anime-lora-makoto-shinkai-anime-style.safetensors"
    Download-ModelFile "https://huggingface.co/danbrown/epi_noiseoffset2/resolve/main/epi_noiseoffset2.safetensors" $loraDir "epi_noiseoffset2.safetensors"
}

# 4. ControlNet
Write-Host "`n[4/4] ControlNet Models..." -ForegroundColor Cyan
if (-not $SkipOptional) {
    Download-ModelFile "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_openpose_fp16.safetensors" $cnetDir "control_v11p_sd15_openpose_fp16.safetensors"
    Download-ModelFile "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_canny_fp16.safetensors" $cnetDir "control_v11p_sd15_canny_fp16.safetensors"
}

Write-Host "`nAll model downloads completed!" -ForegroundColor Green
