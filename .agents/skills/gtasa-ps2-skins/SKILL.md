---
name: gtasa-ps2-skins
description: Create, edit, and kitbash low-poly pedestrian skins (peds) for GTA San Andreas, SA-MP, and open.mp in a pure RenderWare PS2 style using Blender CLI (bpy + DragonFF), PAL8 texture quantization (.txd), and binary validation (.dff). Use when the user asks to create a GTA SA skin, make a skin for a faction/mafia/gang, combine heads or clothing from vanilla peds (head swap, fold hoods down, change tees or jeans), pack .dff/.txd files, or generate AddCharModel lines for open.mp and SA-MP.
---

# gtasa-ps2-skins

## Summary

Design, model, surgically kitbash, and compile pedestrian skins (peds) for Grand Theft Auto: San Andreas that are compatible with PC (open.mp and SA-MP) while keeping the low-poly topology, the 32-bone skeleton, and the quantized PlayStation 2 textures on RenderWare 3.6.0.3 (`0x1803FFFF`). Includes an interactive consultant mode for generic faction or character requests.

## Steps

1. **Evaluate Prompt Specificity**:
   - If the prompt is specific (it states exactly which heads or garments to combine), run the scripts directly.
   - If the prompt is generic (e.g. "Create a skin for my SA-MP Russian mafia"), run a short 4-point interview offering options with real GTA:SA names and IDs (Rank/Base body, Donor head, Inner-clothing/pants textures, and Accessory surgery) plus a one-click ready recommendation.
2. **Build the Rig and Low-Poly Mesh**: Run `python3 scripts/build_ps2_rig_bpy.py --preset <preset> --outdir ./output/<id>`.
3. **Quantize the Texture to PS2 PAL8 and Pack the `.txd`**: Run `python3 scripts/quantize_ps2_txd.py --preset <preset> --output ./output/<id>/<id>.txd`.
4. **Validate the RenderWare Stream**: Run `python3 scripts/validate_rw_stream.py --dff ./output/<id>/<id>.dff --txd ./output/<id>/<id>.txd` and verify `"status": "PASS"`.

## Real vanilla head swaps

For a named vanilla head/body pair, use `scripts/vanilla_rw_kitbash.py` with `--game-dir`, `--head-model`, `--body-model`, `--skin-name` and `--outdir`. This preserves the real meshes, UVs and the body's 33-frame / 32-node rig. The older procedural preset generator is a proxy path.

Render the actual exported files with `python scripts/render_ps2_vibesheet.py --dff <skin>.dff --txd <skin>.txd --output <skin>_vibe_sheet.png`. This produces Front, Side, Back, 3/4 and a weighted diagnostic Pose Test. Validate with the requested `--base-skin-id` and `--custom-skin-id`; report binary/visual checks separately from in-game testing.
