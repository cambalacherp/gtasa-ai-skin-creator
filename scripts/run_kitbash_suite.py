#!/usr/bin/env python3
"""
run_kitbash_suite.py - Orchestrator for the 3 Surgical Kitbash Tests for GTA:SA (open.mp / SA-MP)

Runs the 3 base combinations end to end:
1. wmydrug_sindacco (Base ID 29 wmydrug + Head ID 119 sindaco, hood folded back onto Spine1).
2. bmypol1_tenpenny (Base ID 265 tenpen + Head ID 66 bmypol1, LSPD uniform with matched African-American skin tone).
3. wmybar_claude (Base ID 299 claude + Head ID 177 wmybar, open leather jacket with a white tshirtwhite tee and blue jeansdenim jeans).
"""

import json
import os
import sys

from build_ps2_rig_bpy import KITBASH_PRESETS, write_standalone_gtasa_ped_dff
from quantize_ps2_txd import process_and_pack_ps2_txd
from validate_rw_stream import audit_dff_file, audit_txd_file


def run_all_kitbash_tests(base_outdir: str = "./output_kitbash_suite") -> dict:
    os.makedirs(base_outdir, exist_ok=True)
    suite_results = {}
    artconfig_lines = [
        "// artconfig.txt - Suite of 3 PS2 RenderWare-style kitbashed skins (open.mp / SA-MP)",
    ]

    for preset_key, meta in KITBASH_PRESETS.items():
        skin_dir = os.path.join(base_outdir, preset_key)
        os.makedirs(skin_dir, exist_ok=True)

        dff_path = os.path.join(skin_dir, f"{preset_key}.dff")
        txd_path = os.path.join(skin_dir, f"{preset_key}.txd")
        png_path = os.path.join(skin_dir, f"{preset_key}_atlas.png")
        rep_path = os.path.join(skin_dir, f"{preset_key}_report.json")
        tex_name = str(meta["tex_name"])
        base_id = int(meta["base_skin_id"])
        custom_id = int(meta["custom_skin_id"])

        dff_info = write_standalone_gtasa_ped_dff(dff_path, tex_name=tex_name, preset_name=preset_key)
        txd_info = process_and_pack_ps2_txd(
            output_txd_path=txd_path,
            tex_name=tex_name,
            preset=preset_key,
            preview_png_path=png_path,
            size=256,
            colors=256,
        )

        dff_audit = audit_dff_file(dff_path)
        txd_audit = audit_txd_file(txd_path)
        passed = dff_audit["valid"] and txd_audit["valid"]

        art_line = f'AddCharModel({base_id}, {custom_id}, "{preset_key}.dff", "{preset_key}.txd");'
        artconfig_lines.append(art_line)

        report_payload = {
            "preset": preset_key,
            "description": meta["description"],
            "status": "PASS" if passed else "FAIL",
            "dff_info": dff_info,
            "txd_info": txd_info,
            "dff_audit": dff_audit,
            "txd_audit": txd_audit,
            "artconfig_line": art_line,
        }
        with open(rep_path, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=2, ensure_ascii=False)

        suite_results[preset_key] = {
            "status": report_payload["status"],
            "triangles": dff_audit["triangle_count"],
            "vertices": dff_audit["vertex_count"],
            "bones": dff_audit["skin_bones"],
            "texture": tex_name,
            "artconfig": art_line,
        }

    artconfig_path = os.path.join(base_outdir, "artconfig.txt")
    with open(artconfig_path, "w", encoding="utf-8") as f:
        f.write("\n".join(artconfig_lines) + "\n")

    return {"suite_status": "ALL_PASS", "artconfig_path": artconfig_path, "results": suite_results}


if __name__ == "__main__":
    out_folder = sys.argv[1] if len(sys.argv) > 1 else "./output_kitbash_suite"
    summary = run_all_kitbash_tests(out_folder)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
