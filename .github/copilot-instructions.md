# GTA:SA PS2 Skins — project instructions for Copilot

The canonical, full specification for this repository lives in [AGENTS.md](../AGENTS.md).
Read it and follow it for every task in this repository; this file only states the non-negotiables.

## Non-negotiable rules

1. Never generate generic high-density AI meshes or clean synthetic textures. Every asset must look like a 2004 Rockstar North ped: at most 1,600 triangles and 1,100 vertices, one unified atomic, a 32-bone HAnim rig (`0x011E`), PAL8 256-color textures, library stamp `0x1803FFFF`.
2. Every skin request must produce, in `output/<skin_name>/`: `<skin_name>.dff`, `<skin_name>.txd`, `<skin_name>_vibe_sheet.png`, and `<skin_name>_report.json` with `"status": "PASS"` from `python3 scripts/validate_rw_stream.py`.
3. Generic requests (e.g. "make me a Russian mafia skin") trigger the 4-point interview protocol from AGENTS.md before any binary is generated; specific surgical requests run straight to compilation.
4. The reusable skill `gtasa-ps2-skins` ships at `.agents/skills/gtasa-ps2-skins/SKILL.md` (mirrored to `.claude/skills/`); invoke it with `/gtasa-ps2-skins` or let relevance loading pick it up.
5. For every skin, verify and normalize exposed skin across head, neck, torso, arms and hands as part of the project workflow. The head is the default tone reference unless the user specifies otherwise. Preserve tattoos/shading and non-skin materials, and inspect the exported TXD in Blender for seams. This applies to all model pairs; prepare the correct UV mask/profile for each pair instead of waiting for another request.

## Maintenance

After editing `AGENTS.md`, any file in `scripts/`, or the skill, run `python3 scripts/sync_agent_harnesses.py` to refresh the mirrored copies. Run it with `--check` for a byte-level drift audit before committing.
