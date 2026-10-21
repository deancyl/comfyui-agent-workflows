#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI Agent Client SDK (Python)
---------------------------------
Designed specifically for Autonomous AI Agents (Claude, GPT, Antigravity, OpenCode, Codex).
Enables programmatic execution of ComfyUI Dual-Track workflows via REST API with:
  - Quality / Preview mode switching
  - Dynamic prompt & negative prompt injection
  - Seed randomization & reproducibility
  - Queue status tracking & polling
  - Automatic output image retrieval & error self-healing
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional, List, Tuple

DEFAULT_SERVER_URL = "http://127.0.0.1:8284"

class ComfyAgentClient:
    def __init__(self, server_url: str = DEFAULT_SERVER_URL, timeout: int = 600):
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout

    def check_health(self) -> bool:
        """Check if ComfyUI server is responsive."""
        try:
            req = urllib.request.Request(f"{self.server_url}/system_stats")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def get_queue(self) -> Dict[str, Any]:
        """Fetch current queue status (running and pending tasks)."""
        req = urllib.request.Request(f"{self.server_url}/queue")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def interrupt(self) -> bool:
        """Interrupt current running generation."""
        try:
            req = urllib.request.Request(f"{self.server_url}/interrupt", data=b"", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def load_workflow_file(self, file_path: str) -> Dict[str, Any]:
        """Load workflow JSON from local path."""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def queue_prompt(self, prompt_graph: Dict[str, Any], client_id: Optional[str] = None) -> str:
        """
        Send an execution graph to ComfyUI /prompt endpoint.
        Returns prompt_id.
        """
        payload = {"prompt": prompt_graph}
        if client_id:
            payload["client_id"] = client_id
            
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.server_url}/prompt",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res["prompt_id"]
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"ComfyUI HTTP {e.code} Error: {err_body}")

    def wait_for_completion(
        self,
        prompt_id: str,
        poll_interval: float = 3.0,
        progress_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Poll /history/{prompt_id} until completion or timeout.
        Returns the history entry for the prompt.
        """
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            req = urllib.request.Request(f"{self.server_url}/history/{prompt_id}")
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    history = json.loads(resp.read().decode("utf-8"))
                    if prompt_id in history:
                        entry = history[prompt_id]
                        status = entry.get("status", {})
                        if status.get("status_str") == "error":
                            raise RuntimeError(f"ComfyUI execution error: {status.get('messages')}")
                        return entry
            except urllib.error.URLError:
                pass  # Transient network hiccup during heavy GPU load
                
            elapsed = time.time() - start_time
            if progress_callback:
                progress_callback(elapsed)
            time.sleep(poll_interval)
            
        raise TimeoutError(f"Prompt {prompt_id} timed out after {self.timeout}s")

    def download_image(self, filename: str, subfolder: str = "", folder_type: str = "output", dest_path: str = "") -> str:
        """Download output image from /view endpoint."""
        params = urllib.parse.urlencode({
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        })
        url = f"{self.server_url}/view?{params}"
        if not dest_path:
            dest_path = filename
            
        dest_dir = os.path.dirname(dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
            
        urllib.request.urlretrieve(url, dest_path)
        return dest_path

    def run_generation(
        self,
        prompt_graph: Dict[str, Any],
        output_dir: str = "./outputs",
        filename_prefix: Optional[str] = None
    ) -> List[str]:
        """
        Convenience end-to-end method:
        1. Queues the prompt
        2. Waits for completion
        3. Downloads all resulting images to output_dir
        4. Returns list of local image paths
        """
        prompt_id = self.queue_prompt(prompt_graph)
        print(f"[ComfyAgent] Queued task {prompt_id}, waiting for generation...")
        
        def _on_progress(elapsed: float):
            print(f"[ComfyAgent] Sampling in progress... ({elapsed:.1f}s elapsed)", end="\r")
            
        history_entry = self.wait_for_completion(prompt_id, progress_callback=_on_progress)
        print(f"\n[ComfyAgent] Task {prompt_id} completed successfully!")
        
        outputs = history_entry.get("outputs", {})
        downloaded = []
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for img_info in node_output["images"]:
                    fn = img_info["filename"]
                    sub = img_info.get("subfolder", "")
                    typ = img_info.get("type", "output")
                    out_path = os.path.join(output_dir, fn)
                    saved = self.download_image(fn, sub, typ, out_path)
                    print(f"[ComfyAgent] Saved image: {saved}")
                    downloaded.append(saved)
                    
        return downloaded

if __name__ == "__main__":
    client = ComfyAgentClient()
    if client.check_health():
        print(f"Connected to ComfyUI at {client.server_url}")
        queue = client.get_queue()
        print(f"Queue status: {len(queue.get('queue_running', []))} running, {len(queue.get('queue_pending', []))} pending.")
    else:
        print(f"ComfyUI is not reachable at {client.server_url}. Please ensure the server is running.")
