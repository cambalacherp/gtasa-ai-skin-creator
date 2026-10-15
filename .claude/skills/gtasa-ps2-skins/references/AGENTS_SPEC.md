# AGENTS.md — Autonomous Low-Poly Skin Creation System for GTA: San Andreas (PlayStation 2 RenderWare Style + `gta-3d-ai` Flow for `open.mp` / SA-MP)

## Repository commit identity

All commits in this project must use `cambalacherp <223213695+cambalacherp@users.noreply.github.com>` as both author and committer. Do not add `Co-Authored-By`, `Co-Author`, `Co-Authors` or any other secondary authorship attribution. Configure this repository locally with `user.name=cambalacherp`, `user.email=223213695+cambalacherp@users.noreply.github.com`, `user.useConfigOnly=true` and `core.hooksPath=.githooks`. Preserve these settings and the identity-checking `commit-msg` hook; do not bypass it. Check the actual committed metadata, not just Git configuration, before reporting completion.

## 1. The Agent Must Operate Under Dryxio's Vanilla "Vibe Matching" Paradigm (`gta-3d-ai`) and Compile for PC (`open.mp` / SA-MP)

This document is the master operating protocol for any coding-agent harness — **OpenCode**, **OpenAI Codex**, **VS Code + Copilot Chat**, **Google Antigravity**, **Claude Code**, or an advanced multimodal AI model (e.g. **Gemini Argon** or **GPT-6 Astra**) — to design, model, rig, texture, and validate pedestrian skins (`peds`) for **Grand Theft Auto: San Andreas** that run on PC under [open.mp](https://open.mp/docs/scripting/resources/boneid) and [SA-MP](https://sampwiki.blast.hk/wiki/Bone_IDs), preserving 100% of the PlayStation 2 art direction, low-poly topology, and lighting on [RenderWare 3.6.0.3](https://www.grandtheftwiki.com/RenderWare).

Inspired by the classic-modding AI tool architecture created by [Dryxio](https://github.com/dryxio) — such as **GTA Scout (`gta-3d-ai`)** for Blender CLI assisted modeling, [Ariane](https://github.com/Dryxio/ariane) for contextual *vibe mapping*, and the [GTA Stuff](https://gtastuff.com/) database — the agent **must never generate generic high-density AI meshes or clean synthetic textures**. Instead, it must build assets that look as if they came straight out of Rockstar North's 2004 `gta3.img` or `player.img`.

### Project-wide requirement: coherent skin tone for every skin

This requirement applies to every model/agent and every skin created or edited in this project, not only Sindaco/LSV2. Before delivery, verify and normalize exposed skin across head, neck, torso, arms and hands so they read as one coherent skin tone. The head is the default reference unless the user explicitly chooses another reference or an intentional color difference. Matching is part of the normal workflow; do not wait for a separate user request. Already matching skin needs verification, not unnecessary recoloring.

Preserve tattoos, shading and skin texture, and protect clothing, hair and the reference head through final palette quantization. Use inspected UV/material masks; create an appropriate profile for each new donor/body pair instead of reusing Sindaco/LSV2 coordinates. For this supported recipe, include `--match-body-skin-to-head` in the build command. Inspect the exported TXD and Blender captures for color seams at the jaw, neck and shoulders before calling a skin finished.

### Required Deliverables for Every Skin Request
1. **`output/<skin_name>/<skin_name>.dff`**: Unified geometry and a 32-bone skeleton exported via the vanilla stream packer or Blender CLI (`bpy`) + [DragonFF](https://github.com/Parik27/DragonFF) with library stamp `0x1803FFFF` (GTA:SA PC / RenderWare 3.6.0.3).
2. **`output/<skin_name>/<skin_name>.txd`**: Native texture dictionary (`0x1803FFFF`, D3D9 PC) compatible with [Magic.TXD](https://github.com/FrannDzs/Magic.TXD), whose images have been quantized to an 8-bit palette (256 colors) and compressed in dynamic range to replicate the PS2 rasterizer.
3. **`output/<skin_name>/<skin_name>_vibe_sheet.png`**: Multi-angle contact sheet (`Front`, `Side`, `Back`, `3/4`, and `Pose Test`) captured from the exported DFF/TXD by local Blender CLI via `scripts/render_blender_cli.py` (never an image generation API) for visual self-critique of the model.
4. **`output/<skin_name>/<skin_name>_report.json`**: Binary certificate issued by `scripts/validate_rw_stream.py`, together with the Pawn `AddCharModel` block ready for `open.mp` / SA-MP servers.

For changes to binary serialization, verify the rebuilt DFF/TXD with an independent consumer, preferably the user's target viewer, and retain screenshot/file-hash evidence. Internal parsing and Blender previews can share an exporter bug. Clump Struct counts and MaterialList reference tables must be checked against their actual contents; see the skill's verified lessons.

## 2. Specificity Router and Customization Interview Protocol for Generic Prompts

The agent must classify each incoming prompt by how well defined it is before running any Blender code:

### Case 1: Specific or Surgical Prompt (Direct Execution)
If the user already names the parts, base models, or concrete changes (e.g. *"Take `wmydrug`, fold the hood back, and use the `sindacco` head"*), the agent **must not interrupt with questions** and must run the compile and validation phases directly.

### Case 2: Generic or Role/Faction Prompt (Interactive Consultant Mode)
If the user sends an open request (e.g. *"Create a skin for my SA-MP Russian mafia"*, *"Make me a Hispanic gangster"*, *"Build me a mechanic"*), the agent **must pause binary generation and run a short guided 4-point interview**, always proposing real pieces and IDs from the [open.mp Skins](https://open.mp/docs/scripting/resources/skins) and [SA-MP Wiki Skins:All](https://sampwiki.blast.hk/wiki/Skins:All) catalogs instead of empty questions:

1. **Rank / Archetype and Base Body (`Spine` / `Pelvis`)**:
   - Propose 3 concrete silhouette options tied to real vanilla models (for example, for *Russian Mafia*: **Street enforcer / Bratva** with the leather jacket from `maffb` ID `112` or `claude` ID `299`, or a *tracksuit* jacket on `dnb1` ID `121`; **Hitman / Collector** with the brown jacket and open shirt from `maffa` ID `111`; or **Pakhan / Boss** with the dark suit from `mafboss` ID `113` or `vmaff4` ID `127`).
2. **Head, Hairstyle, and Facial Features (`Head` Bone ID `5` + `Neck` Bone ID `4`)**:
   - Offer 2 or 3 donor heads compatible with the character's ethnicity and personality (e.g. the shaved, hard head from `maffb` ID `112`, the mature face from `mafboss` ID `113`, or the neat cut from `wmybar` ID `177`, with the option to add a full beard, scar, or mustache in the `.txd`).
3. **Clothing Palette and Vanilla Textures (`UV Splicing`)**:
   - Ask which color and `player.img` texture combination they prefer for the inner torso and legs (e.g. white tee `tshirtwhite` vs. black sweater; blue jeans `jeansdenim` vs. black dress pants or jogging pants with white stripes).
4. **Accessory Surgery and Low-Poly Details (`Mesh Surgery`)**:
   - Ask whether they want geometric mesh edits enabled (hood folded back onto `Spine1`, raised jacket collar, dark glasses, a chain across the chest, or black gloves painted onto the mitten hands `R/L Hand`).

> **Quick Confirmation Shortcut**: At the end of the questions, the agent must always offer a **Recommended Combination Ready to Compile** so the user can simply reply *"Build the recommended one"* or customize point by point.

## 3. Repository Structure Connects Headless Blender to Packers and Binary Validators

| Project File | Role in the Autonomous Pipeline | Standard Run Command |
| :--- | :--- | :--- |
| `AGENTS.md` | Master technical specification; read automatically by OpenCode, Codex, VS Code + Copilot, and Antigravity (Claude Code loads it through `CLAUDE.md`) | Automatic read at the project root |
| `CLAUDE.md` | Claude Code shim: `@AGENTS.md` import (works on every Claude Code version, never double-read) | Automatic read at the project root |
| `.github/copilot-instructions.md` | Always-on Copilot Chat pointer that defers to this file | Automatic read by VS Code + Copilot Chat |
| `.agents/skills/gtasa-ps2-skins/SKILL.md` | Canonical Agent Skill (cross-tool `.agents/skills` standard); mirrored to `.claude/skills/` for Claude Code | Auto-load by context or `/<skill-name>` |
| `scripts/sync_agent_harnesses.py` | Synchronizer that regenerates every harness mirror from the canonical sources; `--check` audits for drift | `python3 scripts/sync_agent_harnesses.py [--check]` |
| `scripts/build_ps2_rig_bpy.py` | Blender (`bpy`) generator for the official 32-bone rig, surgical *kitbashing* engine (`head-swap`, `hood-down`, `uv-remap`), weight sanitizer, and [DragonFF](https://github.com/Parik27/DragonFF) exporter | `blender -b -P scripts/build_ps2_rig_bpy.py -- --preset <preset_id> --outdir output/<id>` |
| `scripts/vanilla_rw_kitbash.py` | Real vanilla IMG extraction, head graft, original body skeleton and texture atlas | `python scripts/vanilla_rw_kitbash.py --game-dir "C:/Juegos/gta clean" --head-model sindaco --body-model lsv2 --skin-name sindaco_lsv2 --outdir output/sindaco_lsv2 --match-body-skin-to-head` |
| `scripts/render_blender_cli.py` | Local Blender CLI renderer; actual DFF/TXD, five views, neck closeups and editable .blend | `python scripts/render_blender_cli.py --dff output/sindaco_lsv2/sindaco_lsv2.dff --txd output/sindaco_lsv2/sindaco_lsv2.txd --output output/sindaco_lsv2/sindaco_lsv2_vibe_sheet.png` |
| `scripts/quantize_ps2_txd.py` | Vanilla atlas compositor (head grafts, tees, jeans, and skin-tone matching), 256-color PS2 quantizer, and binary `.txd` compiler (`0x1803FFFF`) | `python3 scripts/quantize_ps2_txd.py --preset <preset_id> --output output/<id>/<id>.txd` |
| `scripts/validate_rw_stream.py` | Binary analyzer of `.dff` and `.txd` chunks (`Clump`, `FrameList`, `HAnim PLG`, `Skin PLG`, `TextureNative`) and Pawn code generator | `python3 scripts/validate_rw_stream.py --dff output/<id>/<id>.dff --txd output/<id>/<id>.txd` |
| `scripts/run_kitbash_suite.py` | Test orchestrator that compiles, audits, and generates `artconfig.txt` | `python3 scripts/run_kitbash_suite.py ./output_kitbash_suite` |

## 4. Polygon and Topology Budget Is Governed by PS2 and PC Engine Limits

| Geometric Metric | Authentic PS2 Range (Agent Target) | Strict Validator Cap (`validate_rw_stream.py`) | Blender (`bpy`) Implementation Rule |
| :--- | :--- | :--- | :--- |
| **Total Triangles (`Triangles`)** | 850 – 1,250 triangles | `1,600` triangles | Use triangulated faces only (`BMesh` / `triangulate_faces`) |
| **Total Vertices (`Vertices`)** | 500 – 850 vertices | `1,100` vertices | Weld seams (`remove_doubles` at `0.0005m`) between torso, neck, and limbs |
| **Objects / `Atomics` per `.dff`** | Exactly `1` unified mesh | `1` `Atomic` | Join head, torso, legs, and accessories into the same `Mesh` object |
| **Bones per Vertex (`Skin PLG`)** | 1 to 2 bones (90% of vertices) | Maximum `4` bones (`limit=4`) | Run `vertex_group_limit_total(limit=4)` and `vertex_group_normalize_all()` |
| **Hand Topology** | Mitten: 4 fingers together + thumb | Do not model 5 individual tubular fingers | Weight the 4-finger block to `R Finger (25)` / `L Finger (35)` and the thumb to `R Finger01 (26)` / `L Finger01 (36)` |

The 500–850 vertex range is a visual target, not a rejection threshold. The strict vertex cap is 1,100; authentic UV seams may require more than 850 vertices.

## 5. Vanilla Skeleton: 33 Frames, 32 HAnim Nodes

Vanilla peds contain an unbound container frame plus 32 bone frames. Skin indices address the root HAnim node table, not Bone IDs or FrameList indices. Preserve the body's frame list, table order and inverse bind matrices when grafting. Mesh space is X=up, Y=front, Z=left.

The following table is read from vanilla LSV2. Root (Bone ID 0) must have zero weight; Pelvis (Bone ID 1) may carry full weight. The procedural legacy generator uses a separate 32-frame layout and must not be used as a skeleton template for vanilla surgery. Attachment API IDs are a separate namespace.

| Skin node index | HAnim Bone ID | Frame name | Parent Bone ID |
| :--- | :--- | :--- | :--- |
| 0 | 0 | `Root` | container |
| 1 | 1 | `Pelvis` | 0 |
| 2 | 2 | `Spine` | 1 |
| 3 | 3 | `Spine1` | 2 |
| 4 | 4 | `Neck` | 3 |
| 5 | 5 | `Head` | 4 |
| 6 | 8 | `Jaw` | 5 |
| 7 | 6 | `L Brow` | 5 |
| 8 | 7 | `R Brow` | 5 |
| 9 | 31 | `Bip01 L Clavicle` | 4 |
| 10 | 32 | `L UpperArm` | 31 |
| 11 | 33 | `L ForeArm` | 32 |
| 12 | 34 | `L Hand` | 33 |
| 13 | 35 | `L Finger` | 34 |
| 14 | 36 | `L Finger01` | 35 |
| 15 | 21 | `Bip01 R Clavicle` | 4 |
| 16 | 22 | `R UpperArm` | 21 |
| 17 | 23 | `R ForeArm` | 22 |
| 18 | 24 | `R Hand` | 23 |
| 19 | 25 | `R Finger` | 24 |
| 20 | 26 | `R Finger01` | 25 |
| 21 | 302 | `L breast` | 3 |
| 22 | 301 | `R breast` | 3 |
| 23 | 201 | `Belly` | 2 |
| 24 | 41 | `L Thigh` | 1 |
| 25 | 42 | `L Calf` | 41 |
| 26 | 43 | `L Foot` | 42 |
| 27 | 44 | `L Toe0` | 43 |
| 28 | 51 | `R Thigh` | 1 |
| 29 | 52 | `R Calf` | 51 |
| 30 | 53 | `R Foot` | 52 |
| 31 | 54 | `R Toe0` | 53 |

## 6. Surgical Kitbashing, Accessory Remodel, and Vanilla Texture Splicing Protocol

### Recipe A: Garment Topology Remodel + Head Swap (`wmydrug_sindacco`)
- **Source Assets**: `wmydrug` body (ID `29`) + `sindaco` head (ID `119`).
- **Geometry and Rig Surgery**: Separate the raised hood (`z = 1.56m .. 1.83m`), rotate it `-105°` on the X axis with the pivot at the nape so it rests on the upper back (`z = 1.34m .. 1.47m`), and transfer its weights from bone `Head (8)` to **`Spine1 (4)` (`0.80`) + `Neck (5)` (`0.20`)**. Graft the `sindaco` head and weld the cervical ring.

### Recipe B: Head Swap with Ethnic Consistency and Full Uniform (`bmypol1_tenpenny`)
- **Source Assets**: `bmypol1` head (ID `66`) + `tenpen` LSPD police body (ID `265`).
- **Geometry and Rig Surgery**: Keep Tenpenny's short-sleeve uniform and tactical belt, section the skull at `z = 1.50m`, weld the `bmypol1` head at `Neck (5)`, and match skin tone (`RGB 96, 62, 44`) across face, nape, and forearms.

### Recipe C: Head Swap + Selective Clothing-Layer Retexture (`wmybar_claude`)
- **Source Assets**: `wmybar` head (ID `177`) + `claude` body (ID `299`) + vanilla textures `tshirtwhite` and `jeansdenim`.
- **Geometry and UV Surgery**: Weld the `wmybar` head into the collar of Claude's leather jacket, redirect the central chest faces (`ny < -0.45`) to a UV sub-island of white cotton (`RGB 218, 216, 210`), and map the legs (`L/R Thigh`, `L/R Calf`) to indigo denim with vertical thigh wear (`RGB 48, 76, 116`).

### Recipe D: Real Vanilla Head Graft (`sindaco_lsv2`)
- Sources: Sindaco head (ID 119), LSV2 body (ID 109); custom ID 20004.
- Use `vanilla_rw_kitbash.py`, not the procedural proxy presets. Preserve the 20 cervical transition triangles after removing the old bandana tail. Scale the donor skull against the removed skull (1.08558) and retain the original crown height (mesh X=0.86963618). Fit the 18 neck endpoints just under the donor surface to hide old-head scraps. Keep the original neck and head weights. Never align the chin to the shirt collar or sink the head into the torso. Output: 1,080 vertices / 1,165 triangles.
- Preserve the body FrameList, HAnim node ordering and inverse bind matrices. Pack one textured Atomic, a D3D9 8888 atlas with a baked 256-color palette, and RenderWare stamp `0x1803FFFF`.
- Render real screenshots with local Blender CLI after rebuilding, including front/side neck closeups. Do not use image generation models for previews. Run the binary validator. A binary PASS and a diagnostic pose are not evidence of an in-game runtime test.

For the approved variant, match body skin to the Sindaco head with `--match-body-skin-to-head` and the inspected canonical UV profile. Preserve head and non-skin pixels after palette quantization. The skill reference `references/vanilla_kitbash_lessons.md` records corrected handoff findings.

## 7. Harness Entry Points, Mirrors, and Drift Control

The repository is agent-agnostic: `AGENTS.md` (this file) and `.agents/skills/gtasa-ps2-skins/` are the only canonical agent-facing sources; every other harness file is a thin import or a byte-verified mirror.

| Harness | Instructions it reads | Skill it reads |
| :--- | :--- | :--- |
| **OpenCode** | `AGENTS.md` (automatic) | `.agents/skills/` and `.claude/skills/` (compatibility sources) |
| **OpenAI Codex** | `AGENTS.md` (automatic) | `.agents/skills/` (native) |
| **VS Code + Copilot Chat** | `.github/copilot-instructions.md` → defers to this file; `AGENTS.md` (Copilot harness) | `.agents/skills/` and `.claude/skills/` |
| **Google Antigravity** | `AGENTS.md` (automatic) | `.agents/skills/` (default location) |
| **Claude Code** | `CLAUDE.md` → `@AGENTS.md` import (all versions) | `.claude/skills/` |

**Drift rule**: after editing `AGENTS.md`, any file in `scripts/`, or the canonical skill, run `python3 scripts/sync_agent_harnesses.py` to regenerate every mirror (`references/AGENTS_SPEC.md`, the skill's `scripts/` copies, and the whole `.claude/skills/` bundle). Run `python3 scripts/sync_agent_harnesses.py --check` for a byte-level drift audit (exit code `1` on mismatch) before running the kitbash suite or committing.
