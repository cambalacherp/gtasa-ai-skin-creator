---
name: gtasa-ps2-skins
description: Create and edit GTA San Andreas pedestrian skins for SA-MP and open.mp from real vanilla heads, bodies and textures. Use for head swaps, clothing edits, skin tone matching, DFF/TXD packing and validation, local Blender CLI previews, and AddCharModel delivery.
---

# gtasa-ps2-skins

Use real vanilla meshes and textures when a request names a source ped or head/body pair. The presets in `build_ps2_rig_bpy.py` are procedural proxies, not extracted Rockstar models.

- For named parts, execute directly. For generic character requests, follow the customization interview in [references/AGENTS_SPEC.md](references/AGENTS_SPEC.md), section 2.
- Before surgery or debugging RenderWare data, read [references/vanilla_kitbash_lessons.md](references/vanilla_kitbash_lessons.md): verified binary details, the failed neck-fitting approach and the corrected method.
- Preserve the user's chosen reference tone. Do not turn one recipe's measurements or UV boxes into rules for every ped.

## Required for every skin: coherent skin tone

Skin tone matching is a project-wide requirement for every model/agent, not an optional edit or a Sindaco/LSV2 exception. Verify exposed head, neck, torso, arms and hands, and normalize mismatches before delivery without waiting for another user request. Use the head as reference unless the user specifies another reference or an intentional difference. Already matching skin needs verification rather than needless recoloring. Preserve tattoos, shading, clothing and the reference texture through the final palette; check jaw/neck/shoulder seams in exported-TXD Blender captures.

## Build from vanilla assets

```powershell
python scripts/vanilla_rw_kitbash.py --game-dir "<GTA-SA>" --head-model sindaco --body-model lsv2 --skin-name sindaco_lsv2 --outdir output/sindaco_lsv2 --match-body-skin-to-head
```

Use `--match-body-skin-to-head` for the supported Sindaco/LSV2 recipe; its inspected profile is in `assets/tone_profiles/`. For other pairs, create suitable inspected masks and sample patches so the same project requirement is fulfilled. Preserve tattoos/shading and protect the reference head and clothing through final palette quantization. Do not recolor an entire atlas with a blanket RGB filter.

Rebuild after engine changes; stale DFF/TXD files or screenshots cannot verify current code.

## Capture and inspect exported files

```powershell
python scripts/render_blender_cli.py --dff <skin>.dff --txd <skin>.txd --output <skin>_vibe_sheet.png
```

Use local Blender CLI for previews; never an AI image generation service. Keep the raw Front, Side, Back, ThreeQuarter, PoseTest and neck closeups plus the packed `.blend` scene. The runner accepts `--blender <executable>`, bounds process lifetime and checks Blender's completion marker. The contact sheet assembles actual captures.

Inspect neck length, shoulder/nape continuity, old-head accessories, tone seams, clothing and deformation. PoseTest applies diagnostic weighted rotations; it is not GTA animation playback.

## Audit and deliver

Run `scripts/validate_rw_stream.py --dff <skin>.dff --txd <skin>.txd --base-skin-id <base> --custom-skin-id <custom>`. Deliver DFF/TXD, screenshots, binary report and AddCharModel registration; include the mask/tone audit for color edits. Distinguish binary PASS, visual review and actual in-game testing.

## Maintain the skill

Root `scripts/`, `AGENTS.md` and `.agents/skills/gtasa-ps2-skins/` are canonical. Run `scripts/sync_agent_harnesses.py`, then `--check`, and refresh the installed skill from that bundle. Keep reusable lessons in the linked reference and recipe-specific data in profile assets. Validate entrypoint changes with skill-creator's `quick_validate.py`.
