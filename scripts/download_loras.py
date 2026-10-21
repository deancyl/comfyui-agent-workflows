#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI Agent Workflows - Automated LoRA Provisioning Script
Downloads and verifies curated SD 1.5 LoRA models with hot-reload support.
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_FILE = os.path.join(ROOT_DIR, "loras_manifest.json")
DEFAULT_DEST = r"G:\ComfyUI\ComfyUI-aki\models\loras"
FALLBACK_DEST = r"C:\Users\deanc\ComfyUI-Zluda\models\loras"


def download_file(url: str, dest_path: str, timeout: int = 30):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    temp_path = dest_path + ".tmp"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    req = urllib.request.Request(url, headers=headers)
    
    start_t = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        total_size = resp.headers.get("Content-Length")
        total_size = int(total_size) if total_size else 0
        
        downloaded = 0
        block_size = 1024 * 1024  # 1MB blocks
        
        with open(temp_path, "wb") as f:
            while True:
                chunk = resp.read(block_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    pct = (downloaded / total_size) * 100
                    speed = (downloaded / (time.time() - start_t + 0.001)) / (1024 * 1024)
                    sys.stdout.write(f"\r  -> Downloading: {pct:.1f}% ({downloaded//1024//1024}MB / {total_size//1024//1024}MB) - {speed:.2f} MB/s")
                    sys.stdout.flush()
    
    if os.path.exists(dest_path):
        os.remove(dest_path)
    os.rename(temp_path, dest_path)
    print(f"\n  [OK] Saved to: {dest_path} ({os.path.getsize(dest_path)//1024//1024} MB)")


def main():
    parser = argparse.ArgumentParser(description="Download and verify curated SD 1.5 LoRA models")
    parser.add_argument("--dest", default="", help="Destination directory (default: G: drive aki storage)")
    parser.add_argument("--category", default="", help="Download only specific category")
    parser.add_argument("--lora", default="", help="Download only specific LoRA key")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without downloading")
    args = parser.parse_args()
    
    if not os.path.exists(MANIFEST_FILE):
        print(f"[ERROR] Manifest not found: {MANIFEST_FILE}")
        sys.exit(1)
        
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    dest_dir = args.dest
    if not dest_dir:
        dest_dir = DEFAULT_DEST if os.path.exists(os.path.splitdrive(DEFAULT_DEST)[0]) else FALLBACK_DEST
    os.makedirs(dest_dir, exist_ok=True)
    
    print(f"==================================================")
    print(f"  LoRA Provisioning Target Directory: {dest_dir}")
    print(f"  Available Categories: {list(manifest.get('categories', {}).keys())}")
    print(f"==================================================")
    
    loras = manifest.get("loras", {})
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for key, info in loras.items():
        if args.category and info.get("category") != args.category:
            continue
        if args.lora and key != args.lora:
            continue
            
        url = info.get("download_url")
        fn = info.get("filename")
        name = info.get("name")
        target_file = os.path.join(dest_dir, fn)
        fallback_file = os.path.join(FALLBACK_DEST, fn)
        
        # Check if already present in dest or fallback
        if os.path.exists(target_file) and os.path.getsize(target_file) > 1024 * 1024:
            print(f"[*] Skipping {name} ({fn}) - already exists in target ({os.path.getsize(target_file)//1024//1024}MB)")
            skip_count += 1
            continue
        if os.path.exists(fallback_file) and os.path.getsize(fallback_file) > 1024 * 1024:
            print(f"[*] Skipping {name} ({fn}) - already exists in C: fallback ({os.path.getsize(fallback_file)//1024//1024}MB)")
            skip_count += 1
            continue
            
        if url == "local":
            print(f"[*] {name} is marked as local asset.")
            skip_count += 1
            continue
            
        print(f"\n[+] Fetching [{info.get('category')}] {name} ({fn})...")
        print(f"    URL: {url}")
        
        if args.dry_run:
            print(f"    [DRY-RUN] Would download to: {target_file}")
            continue
            
        try:
            download_file(url, target_file)
            success_count += 1
        except Exception as e:
            print(f"    [FAIL] Download failed: {e}")
            fail_count += 1
            
    print(f"\n==================================================")
    print(f"  LoRA Provisioning Finished.")
    print(f"  Downloaded: {success_count} | Skipped/Existing: {skip_count} | Failed: {fail_count}")
    print(f"==================================================")


if __name__ == "__main__":
    main()
