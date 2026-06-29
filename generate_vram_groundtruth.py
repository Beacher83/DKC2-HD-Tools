"""
generate_vram_groundtruth.py
============================
Reads all gfxset_XX_vram.bin dumps from the Mesen VRAM dump folder and
generates vram_groundtruth.js — a self-contained lookup table embedded in the Viewer.

Run this script whenever new VRAM dumps are added.

Output: dkc2-viewer/vram_groundtruth.js
"""

import os
import base64
import json
from datetime import datetime

DUMP_FOLDER = r"C:\Users\beach\OneDrive\Dokumente\Mesen2\LuaScriptData\dkc2_vram_dump"
OUTPUT_JS   = os.path.join(os.path.dirname(__file__), "dkc2-viewer", "vram_groundtruth.js")

def main():
    if not os.path.isdir(DUMP_FOLDER):
        print(f"ERROR: Dump folder not found: {DUMP_FOLDER}")
        return

    ground_truth = {}
    total_bytes  = 0

    for filename in sorted(os.listdir(DUMP_FOLDER)):
        if not filename.endswith("_vram.bin"):
            continue
        gfxset_id = filename.replace("_vram.bin", "")   # e.g. "gfxset_07"
        filepath  = os.path.join(DUMP_FOLDER, filename)
        with open(filepath, "rb") as f:
            data = f.read()
        if len(data) != 65536:
            print(f"  WARNING: {filename} has unexpected size {len(data)} (expected 65536) — skipping")
            continue
        ground_truth[gfxset_id] = base64.b64encode(data).decode("ascii")
        total_bytes += len(data)
        print(f"  {gfxset_id}: {len(data):,} bytes -> {len(ground_truth[gfxset_id]):,} base64 chars")

    if not ground_truth:
        print("No VRAM dumps found!")
        return

    timestamp   = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_b64   = sum(len(v) for v in ground_truth.values())
    gfxset_list = sorted(ground_truth.keys())

    js = f"""// AUTO-GENERATED — do not edit manually.
// Run generate_vram_groundtruth.py to regenerate.
//
// Source : {DUMP_FOLDER}
// Generated: {timestamp}
// Gfxsets : {len(ground_truth)} ({', '.join(gfxset_list)})
// Raw VRAM: {total_bytes:,} bytes  |  Base64: {total_b64:,} chars
//
// Each key is a gfxset ID matching the Viewer's container setId format (e.g. "gfxset_07").
// Value is a base64-encoded 64 KB VRAM dump captured by dkc2_vram_dump.lua in Mesen2.
// The Viewer auto-applies these snapshots when a container set has no vramSnapshot stored.

const VRAM_GROUND_TRUTH = {json.dumps(ground_truth, indent=2)};
"""

    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write(js)

    print(f"\nWrote {OUTPUT_JS}")
    print(f"  {len(ground_truth)} gfxsets, {total_bytes:,} raw bytes, {total_b64:,} base64 chars")

if __name__ == "__main__":
    main()
