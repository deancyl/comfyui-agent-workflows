#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI Agent Workflows - GitHub Wiki Synchronizer
Pushes local wiki/*.md files to the GitHub repository's official Wiki git remote.
Note: GitHub requires the first wiki page to be created via the web UI before
the remote .wiki.git repository is initialized on GitHub servers.
"""

import os
import sys
import shutil
import tempfile
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(REPO_ROOT, "wiki")
WIKI_REMOTE = "https://github.com/deancyl/comfyui-agent-workflows.wiki.git"


def run_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def sync_wiki():
    if not os.path.exists(WIKI_DIR):
        print(f"[ERROR] Wiki directory not found: {WIKI_DIR}")
        sys.exit(1)

    print(f"==========================================================")
    print(f"  GitHub Wiki Synchronizer")
    print(f"  Source: {WIKI_DIR}")
    print(f"  Remote: {WIKI_REMOTE}")
    print(f"==========================================================")

    # 1. Test if remote wiki repository is initialized
    code, out, err = run_cmd(["git", "ls-remote", WIKI_REMOTE])
    if code != 0:
        print("\n[Notice] Remote GitHub Wiki is not initialized yet.")
        print("GitHub requires visiting https://github.com/deancyl/comfyui-agent-workflows/wiki")
        print("and clicking 'Create the first page' (or Save) once before .wiki.git is created.")
        print(f"All documentation is currently preserved in '{WIKI_DIR}' and ready to sync.")
        return False

    temp_dir = tempfile.mkdtemp(prefix="comfyui_wiki_")
    try:
        print("\n[1/3] Cloning remote wiki repository...")
        code, out, err = run_cmd(["git", "clone", WIKI_REMOTE, temp_dir])
        if code != 0:
            print(f"[FAIL] Clone failed: {err}")
            return False

        print("[2/3] Copying markdown documents...")
        for fn in os.listdir(WIKI_DIR):
            if fn.endswith(".md"):
                src = os.path.join(WIKI_DIR, fn)
                dst = os.path.join(temp_dir, fn)
                shutil.copy2(src, dst)
                print(f"  -> Synced: {fn}")

        print("[3/3] Committing and pushing to GitHub Wiki...")
        run_cmd(["git", "add", "."], cwd=temp_dir)
        code, status, _ = run_cmd(["git", "status", "--porcelain"], cwd=temp_dir)
        if not status:
            print("  -> Wiki is already up-to-date with remote.")
            return True

        run_cmd(["git", "commit", "-m", "docs: synchronize wiki documentation"], cwd=temp_dir)
        code, out, err = run_cmd(["git", "push", "origin", "master"], cwd=temp_dir)
        if code != 0:
            # Try main branch
            code, out, err = run_cmd(["git", "push", "origin", "main"], cwd=temp_dir)

        if code == 0:
            print("\n🎉 GitHub Wiki synchronized successfully!")
            return True
        else:
            print(f"[FAIL] Push failed: {err}")
            return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    success = sync_wiki()
    sys.exit(0 if success else 1)
