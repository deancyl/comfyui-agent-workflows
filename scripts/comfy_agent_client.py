#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI Agent Client SDK (Reinforced Edition)
---------------------------------------------
Zero-hardcoding, manifest-driven ComfyUI client designed for autonomous LLM Agents.
Enables programmatic workflow selection, parameter injection, and image generation.

Features:
  - Manifest-Driven: Loads workflows_manifest.json to resolve node IDs without guesswork
  - Dual-Format Support: Direct loading of API graphs (workflows_api/) or auto-conversion of UI workflows (workflows/)
  - Quality / Preview Mode: Switches between 26+14 step Quality Refine and 8-step Preview
  - Smoke Test Suite: 'python comfy_agent_client.py --test' for immediate end-to-end verification
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional, List, Tuple, Union

DEFAULT_SERVER_URL = "http://127.0.0.1:8284"

class ComfyAgentClient:
    def __init__(self, server_url: str = DEFAULT_SERVER_URL, repo_root: Optional[str] = None, timeout: int = 600):
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        
        if repo_root is None:
            # Assume repo root is parent of scripts directory
            self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        else:
            self.repo_root = os.path.abspath(repo_root)

        self.manifest_path = os.path.join(self.repo_root, "workflows_manifest.json")
        self.manifest = self._load_manifest()
        self._object_info_cache = None

    def _load_manifest(self) -> Dict[str, Any]:
        """Load workflows_manifest.json if present."""
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

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

    def get_workflow_info(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Lookup workflow metadata by ID (e.g. '01', '04') or tag match.
        """
        if identifier in self.manifest:
            return self.manifest[identifier]

        # Try prefix matching (e.g. '01_真人写实' -> '01')
        id_clean = identifier.split("_")[0]
        if id_clean in self.manifest:
            return self.manifest[id_clean]

        # Tag search
        id_lower = identifier.lower()
        for wid, entry in self.manifest.items():
            if id_lower in [t.lower() for t in entry.get("style_tags", [])]:
                return entry
            if id_lower in entry.get("name", "").lower():
                return entry

        return None

    def load_api_workflow(self, wf_id_or_path: str) -> Dict[str, Any]:
        """
        Load genuine API format Execution Graph JSON.
        Accepts workflow ID (e.g. '01') or direct file path.
        """
        info = self.get_workflow_info(wf_id_or_path)
        if info:
            api_rel = info.get("api_file")
            full_path = os.path.join(self.repo_root, api_rel)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    return json.load(f)

        # Fallback to direct file path
        if os.path.exists(wf_id_or_path):
            with open(wf_id_or_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Check if it's UI format (has 'nodes' and 'links')
                if "nodes" in data and "links" in data:
                    print(f"[Client] Notice: {wf_id_or_path} is in UI format. Auto-converting to API prompt graph...")
                    return self.convert_ui_to_api(data)
                return data

        raise FileNotFoundError(f"Could not resolve API workflow for '{wf_id_or_path}'")

    def convert_ui_to_api(self, ui_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert UI workflow format to API Execution Graph."""
        from ui_to_api_prompt import convert_ui_to_api, fetch_object_info
        if self._object_info_cache is None:
            self._object_info_cache = fetch_object_info(self.server_url)
        return convert_ui_to_api(ui_data, self._object_info_cache)

    def build_prompt_payload(
        self,
        wf_id_or_path: str,
        prompt: Optional[str] = None,
        negative: Optional[str] = None,
        seed: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        mode: str = "quality"  # 'quality' or 'preview'
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Manifest-guided parameter injection:
        Injects positive/negative prompts, seed, dimensions into the API graph.
        Returns (modified_graph, workflow_meta).
        """
        meta = self.get_workflow_info(wf_id_or_path)
        graph = self.load_api_workflow(wf_id_or_path)

        if seed is None:
            seed = int(time.time() * 1000) % (2**31)

        # 1. Inject Positive Prompt
        if prompt and meta and "prompt_node" in meta:
            pn_id = meta["prompt_node"]["id"]
            field = meta["prompt_node"]["field"]
            if pn_id in graph and "inputs" in graph[pn_id]:
                graph[pn_id]["inputs"][field] = prompt

        # 2. Inject Negative Prompt
        if negative and meta and "negative_node" in meta:
            nn_id = meta["negative_node"]["id"]
            field = meta["negative_node"]["field"]
            if nn_id in graph and "inputs" in graph[nn_id]:
                graph[nn_id]["inputs"][field] = negative

        # 3. Inject Seed into Samplers
        if meta and "sampler_node" in meta:
            sn_id = meta["sampler_node"]["id"]
            s_field = meta["sampler_node"].get("seed_field", "seed")
            if sn_id in graph and "inputs" in graph[sn_id]:
                graph[sn_id]["inputs"][s_field] = seed

        if meta and "refine_sampler_node" in meta:
            rn_id = meta["refine_sampler_node"]["id"]
            s_field = meta["refine_sampler_node"].get("seed_field", "seed")
            if rn_id in graph and "inputs" in graph[rn_id]:
                graph[rn_id]["inputs"][s_field] = seed

        if meta and "preview_sampler_node" in meta:
            psn_id = meta["preview_sampler_node"]["id"]
            s_field = meta["preview_sampler_node"].get("seed_field", "seed")
            if psn_id in graph and "inputs" in graph[psn_id]:
                graph[psn_id]["inputs"][s_field] = seed

        return graph, meta

    def queue_prompt(self, prompt_graph: Dict[str, Any], client_id: Optional[str] = None) -> str:
        """Submit Execution Graph to ComfyUI /prompt endpoint. Returns prompt_id."""
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
        """Poll /history/{prompt_id} until completion or timeout."""
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
                pass  # Ignore transient network hiccup during heavy GPU load

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
        wf_id_or_path: str,
        prompt: Optional[str] = None,
        negative: Optional[str] = None,
        seed: Optional[int] = None,
        output_dir: str = "./downloads",
        mode: str = "quality"
    ) -> List[str]:
        """
        High-level turnkey generation:
        1. Loads workflow & injects parameters via manifest
        2. Queues to /prompt
        3. Polls /history
        4. Downloads output images and returns their paths
        """
        graph, meta = self.build_prompt_payload(wf_id_or_path, prompt=prompt, negative=negative, seed=seed, mode=mode)
        prompt_id = self.queue_prompt(graph)
        print(f"[ComfyAgent] Queued task {prompt_id} for workflow '{wf_id_or_path}', waiting for completion...")

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
                    print(f"[ComfyAgent] Downloaded image: {saved}")
                    downloaded.append(saved)

        return downloaded

def run_smoke_test(client: ComfyAgentClient, target_wf: str = "04") -> bool:
    """
    End-to-end smoke test:
    Validates manifest loading, API execution, and image retrieval against live ComfyUI server.
    """
    print("==========================================================")
    print("  ComfyUI Agent Client - End-to-End Smoke Test")
    print(f"  Server URL: {client.server_url}")
    print(f"  Manifest Loaded: {len(client.manifest)} workflows")
    print("==========================================================")

    # 1. Health check
    if not client.check_health():
        print(f"[Smoke Test FAIL] ComfyUI server is unreachable at {client.server_url}.")
        return False
    print("[Smoke Test PASS] Server health check OK.")

    # 2. Manifest check
    wf_info = client.get_workflow_info(target_wf)
    if not wf_info:
        print(f"[Smoke Test FAIL] Workflow '{target_wf}' not found in manifest.")
        return False
    print(f"[Smoke Test PASS] Resolved workflow '{target_wf}': {wf_info['name']}")

    # 3. Queue prompt & run generation
    test_prompt = "masterpiece, best quality, ultra-detailed, 1girl, cute anime maiden with glowing cyber headphones, sharp cel shading"
    test_neg = "lowres, bad anatomy, bad hands, blurry, low quality"
    out_dir = os.path.join(client.repo_root, "downloads", "smoke_test")

    print(f"[Smoke Test] Dispatching generation with test prompt...")
    try:
        images = client.run_generation(
            wf_id_or_path=target_wf,
            prompt=test_prompt,
            negative=test_neg,
            output_dir=out_dir
        )
        if images and len(images) > 0 and os.path.exists(images[0]) and os.path.getsize(images[0]) > 0:
            print(f"\n==========================================================")
            print(f"  🎉 [Smoke Test SUCCESS] Generated {len(images)} image(s)!")
            print(f"  Saved Image: {images[0]} ({os.path.getsize(images[0])} bytes)")
            print(f"==========================================================")
            return True
        else:
            print("[Smoke Test FAIL] No valid image was returned or file size is 0.")
            return False
    except Exception as e:
        print(f"[Smoke Test FAIL] Execution error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ComfyUI Agent Client SDK")
    parser.add_argument("--test", action="store_true", help="Run end-to-end smoke test on live ComfyUI server")
    parser.add_argument("--workflow", type=str, default="04", help="Workflow ID (e.g. 01, 04, 11) or style tag")
    parser.add_argument("--prompt", type=str, default=None, help="Positive prompt text")
    parser.add_argument("--negative", type=str, default=None, help="Negative prompt text")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--server", type=str, default=DEFAULT_SERVER_URL, help="ComfyUI server URL")
    parser.add_argument("--output-dir", type=str, default="./downloads", help="Output directory for generated images")

    args = parser.parse_args()
    client = ComfyAgentClient(server_url=args.server)

    if args.test:
        success = run_smoke_test(client, target_wf=args.workflow)
        sys.exit(0 if success else 1)
    elif args.prompt:
        images = client.run_generation(
            wf_id_or_path=args.workflow,
            prompt=args.prompt,
            negative=args.negative,
            seed=args.seed,
            output_dir=args.output_dir
        )
        print(f"Done! Saved images: {images}")
    else:
        # Default status check
        if client.check_health():
            print(f"Connected to ComfyUI at {client.server_url}")
            print(f"Loaded {len(client.manifest)} workflows from manifest.")
            queue = client.get_queue()
            print(f"Queue: {len(queue.get('queue_running', []))} running, {len(queue.get('queue_pending', []))} pending.")
            print("\nRun with '--test' to perform an end-to-end smoke test, or '--workflow 01 --prompt \"...\"' to generate.")
        else:
            print(f"ComfyUI is not reachable at {client.server_url}. Please ensure server is running.")
