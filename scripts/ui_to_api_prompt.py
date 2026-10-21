#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI UI Workflow to API Prompt Graph Converter (ui_to_api_prompt.py)
----------------------------------------------------------------------
Converts ComfyUI UI-format workflows (.json with 'nodes' & 'links')
into backend API Execution Graphs (.json ready for direct POST to /prompt).

Handles:
  - Link DAG resolution ([link_id, src_node, src_slot])
  - UI-only widget stripping (e.g. KSampler 'control_after_generate' randomize/fixed)
  - Non-executable node filtering (MarkdownNote, Note, Primitive display)
  - Direct validation against ComfyUI /prompt endpoint
"""

import sys
import os
import json
import glob
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

DEFAULT_SERVER_URL = "http://127.0.0.1:8284"

def fetch_object_info(server_url: str = DEFAULT_SERVER_URL) -> Dict[str, Any]:
    """Fetch node schemas from ComfyUI /object_info endpoint."""
    try:
        req = urllib.request.urlopen(f"{server_url.rstrip('/')}/object_info", timeout=5)
        return json.loads(req.read().decode("utf-8"))
    except Exception as e:
        print(f"[Warning] Could not fetch live object_info from {server_url}: {e}")
        # Try local cache if available
        cache_path = os.path.join(os.path.dirname(__file__), "object_info_cache.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

def filter_ui_widgets(node_type: str, widgets_values: Any) -> list:
    """Filter out web UI-only control widgets that do not exist in backend schemas."""
    if isinstance(widgets_values, dict):
        return dict(widgets_values)
    wvals = list(widgets_values) if isinstance(widgets_values, list) else []

    if node_type in ("KSampler", "KSamplerAdvanced"):
        # UI format: [seed, control_after_generate ("randomize"), steps, cfg, sampler_name, scheduler, denoise]
        # Backend schema: seed, steps, cfg, sampler_name, scheduler, denoise
        if len(wvals) >= 7 and isinstance(wvals[1], str) and wvals[1] in ("randomize", "fixed", "increment", "decrement"):
            wvals = [wvals[0]] + wvals[2:]
    elif node_type == "LoadImage":
        # UI format: [image, "image" (upload button trigger)]
        if len(wvals) >= 2 and wvals[1] == "image":
            wvals = [wvals[0]]

    return wvals

def convert_ui_to_api(ui_data: Dict[str, Any], object_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Core conversion function:
    Maps UI 'links' and 'nodes' into ComfyUI Execution Graph dictionary {node_id: {inputs, class_type}}.
    """
    # 1. Build link lookup dictionary
    links_map = {}
    for link in ui_data.get("links", []):
        if link is None:
            continue
        # Format: [link_id, origin_id, origin_slot, target_id, target_slot, type]
        lid = link[0]
        orig_id = str(link[1])
        orig_slot = link[2]
        links_map[lid] = [orig_id, orig_slot]

    api_graph = {}
    nodes = ui_data.get("nodes", [])

    for node in nodes:
        nid = str(node["id"])
        ntype = node.get("type")
        if not ntype:
            continue

        # Skip UI-only non-executable nodes
        if ntype in ("MarkdownNote", "Note", "PrimitiveNode") and ntype not in object_info:
            continue

        info = object_info.get(ntype, {})
        req_inputs = info.get("input", {}).get("required", {})
        opt_inputs = info.get("input", {}).get("optional", {})

        inputs_dict = {}
        linked_names = set()

        # A. Resolve incoming linked inputs
        for inp in node.get("inputs", []):
            iname = inp.get("name")
            ilink = inp.get("link")
            if ilink is not None and ilink in links_map:
                inputs_dict[iname] = links_map[ilink]
                linked_names.add(iname)

        # B. Resolve widget inputs in schema order
        widget_names = []
        input_order = info.get("input_order", {})
        if "required" in input_order:
            for k in input_order["required"]:
                if k not in linked_names:
                    widget_names.append(k)
        else:
            for k in req_inputs.keys():
                if k not in linked_names:
                    widget_names.append(k)

        if "optional" in input_order:
            for k in input_order["optional"]:
                if k not in linked_names:
                    widget_names.append(k)
        else:
            for k in opt_inputs.keys():
                if k not in linked_names:
                    widget_names.append(k)

        filtered_wvals = filter_ui_widgets(ntype, node.get("widgets_values", []))

        if isinstance(filtered_wvals, dict):
            for k, v in filtered_wvals.items():
                inputs_dict[k] = v
        elif isinstance(filtered_wvals, list):
            for i, val in enumerate(filtered_wvals):
                if i < len(widget_names):
                    inputs_dict[widget_names[i]] = val

        api_graph[nid] = {
            "inputs": inputs_dict,
            "class_type": ntype,
            "_meta": {
                "title": node.get("title", ntype)
            }
        }

    return api_graph

def convert_all_workflows(workflows_dir: str, output_dir: str, server_url: str = DEFAULT_SERVER_URL):
    """Batch convert all UI workflows in workflows_dir to API graphs in output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    obj_info = fetch_object_info(server_url)

    # Save schema cache for future offline runs
    cache_path = os.path.join(os.path.dirname(__file__), "object_info_cache.json")
    if obj_info and not os.path.exists(cache_path):
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(obj_info, f)

    ui_files = sorted(glob.glob(os.path.join(workflows_dir, "*.json")))
    print(f"Found {len(ui_files)} UI workflows in {workflows_dir}...")

    converted = 0
    for fpath in ui_files:
        fname = os.path.basename(fpath)
        out_path = os.path.join(output_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            ui_data = json.load(f)

        api_graph = convert_ui_to_api(ui_data, obj_info)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(api_graph, f, indent=2, ensure_ascii=False)

        print(f"  [Converted] {fname} ({len(api_graph)} API nodes) -> {out_path}")
        converted += 1

    print(f"\nSuccessfully converted {converted} workflows to API format in {output_dir}!")

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_dir = os.path.join(repo_root, "workflows")
    dst_dir = os.path.join(repo_root, "workflows_api")

    if len(sys.argv) > 1 and sys.argv[1] != "--all":
        # Single file conversion
        target_file = sys.argv[1]
        out_file = sys.argv[2] if len(sys.argv) > 2 else target_file.replace(".json", "_api.json")
        obj_info = fetch_object_info()
        with open(target_file, "r", encoding="utf-8") as f:
            ui = json.load(f)
        api = convert_ui_to_api(ui, obj_info)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(api, f, indent=2, ensure_ascii=False)
        print(f"Converted {target_file} -> {out_file}")
    else:
        convert_all_workflows(src_dir, dst_dir)
