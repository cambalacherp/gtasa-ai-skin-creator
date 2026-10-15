# Graph Report - gtasa-ps2-skins-repo  (2026-10-15)

## Corpus Check
- Corpus is ~39,010 words - fits in a single context window. You may not need a graph.

## Summary
- 201 nodes · 298 edges · 16 communities (15 shown, 1 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- TXD Quantizer (Claude Mirror)
- Rig Generator (Canonical Skill)
- Ped Mesh Rig Generator (Root)
- Harness Docs & Skill Specs
- Harness Sync (Canonical Skill)
- Harness Sync (Claude Mirror)
- Harness Sync (Root)
- TXD Quantizer (Canonical Skill)
- PS2 TXD Quantizer (Root)
- Rig Generator (Claude Mirror)
- Tenpenny Police Atlas
- Sindacco Hoodie Atlas
- Claude Jacket Atlas
- Kitbash Recipes & Bone Table
- Mirror Drift-Control Design
- Dryxio Vibe Matching

## God Nodes (most connected - your core abstractions)
1. `process_and_pack_ps2_txd()` - 8 edges
2. `process_and_pack_ps2_txd()` - 8 edges
3. `process_and_pack_ps2_txd()` - 8 edges
4. `write_standalone_gtasa_ped_dff()` - 7 edges
5. `write_standalone_gtasa_ped_dff()` - 7 edges
6. `write_standalone_gtasa_ped_dff()` - 7 edges
7. `bmypol1_tenpenny Texture Atlas (256x256 PS2 Ped Skin)` - 7 edges
8. `check()` - 6 edges
9. `audit_dff_file()` - 6 edges
10. `audit_txd_file()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `4-Step Skill Pipeline (evaluate prompt, build rig, quantize TXD, validate stream)` --semantically_similar_to--> `Prompt Specificity Router (Surgical vs Generic)`  [INFERRED] [semantically similar]
  .agents/skills/gtasa-ps2-skins/SKILL.md → AGENTS.md
- `Mirror Sync Procedure (sync_agent_harnesses.py)` --semantically_similar_to--> `Harness Entry Points, Mirrors, and Drift Control`  [INFERRED] [semantically similar]
  README.md → AGENTS.md
- `4-Step Skill Pipeline (evaluate prompt, build rig, quantize TXD, validate stream)` --conceptually_related_to--> `Required Deliverables (.dff, .txd, vibe sheet, report)`  [INFERRED]
  .agents/skills/gtasa-ps2-skins/SKILL.md → AGENTS.md
- `AGENTS_SPEC.md Reference Copy (Canonical Skill)` --references--> `AGENTS.md Master Specification`  [EXTRACTED]
  .agents/skills/gtasa-ps2-skins/references/AGENTS_SPEC.md → AGENTS.md
- `Copilot Project Instructions` --references--> `AGENTS.md Master Specification`  [EXTRACTED]
  .github/copilot-instructions.md → AGENTS.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Autonomous PS2 Skin Compilation Pipeline** — agents_prompt_specificity_router, agents_required_deliverables, agents_ps2_topology_budget, agents_32_bone_skeleton [INFERRED 0.85]
- **Kitbash Suite of 3 Base Tests** — agents_kitbash_recipe_a, agents_kitbash_recipe_b, agents_kitbash_recipe_c, output_kitbash_suite_artconfig_addcharmodel_registry [EXTRACTED 1.00]
- **Agent Harness Entry Points Backed by One Canonical Spec** — agents_overview, claude_overview, _github_copilot_instructions_overview, _agents_skills_gtasa_ps2_skins_skill_overview, _claude_skills_gtasa_ps2_skins_skill_overview [EXTRACTED 1.00]
- **Tenpenny Police Uniform Composite Layout** — output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_uniform_shirt_region, output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_badge_region, output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_duty_belt_region, output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_trousers_region [INFERRED 0.85]
- **bmypol1 Head Skin-Tone Matching Across Face and Limbs** — output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_face_region, output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_skin_tone_region, output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_head_swap_skin [INFERRED 0.75]
- **Recipe C Vanilla Texture Splice (wmybar head + Claude jacket + tee + denim)** — output_kitbash_suite_wmybar_claude_wmybar_claude_atlas, wmybar_face_region, claude_leather_jacket_region, tshirtwhite_region, jeansdenim_region [EXTRACTED 1.00]
- **Garment and Skin Regions Compose the PS2 Texture Atlas** — output_kitbash_suite_wmydrug_sindacco_wmydrug_sindacco_atlas_sindacco_face_region, output_kitbash_suite_wmydrug_sindacco_wmydrug_sindacco_atlas_folded_hood_region, output_kitbash_suite_wmydrug_sindacco_wmydrug_sindacco_atlas_hoodie_body_region, output_kitbash_suite_wmydrug_sindacco_wmydrug_sindacco_atlas_skin_tone_region, output_kitbash_suite_wmydrug_sindacco_wmydrug_sindacco_atlas_trouser_region [EXTRACTED 1.00]

## Communities (16 total, 1 thin omitted)

### Community 0 - "TXD Quantizer (Claude Mirror)"
Cohesion: 0.15
Nodes (20): apply_ps2_color_pipeline(), build_gtasa_pc_txd_bytes(), generate_kitbash_atlas(), main(), process_and_pack_ps2_txd(), Image, Resize, compress levels to `[12, 235]`, and quantize to 256 colors with Floyd-…, Build a native `.txd` (`rwID_TEXDICTIONARY = 0x0016`) for GTA:SA PC… (+12 more)

### Community 1 - "Rig Generator (Canonical Skill)"
Cohesion: 0.15
Nodes (19): _append_prism_ring_segment(), generate_kitbash_ped_arrays(), main(), parse_cli_args(), Namespace, Append a low-poly prismatic tube segment mapped to a specific UV region…, Build the geometry arrays, per-quadrant UVs, and bone weights (`Skin PLG`) for…, Build a RenderWare binary chunk: 12-byte header plus payload. (+11 more)

### Community 2 - "Ped Mesh Rig Generator (Root)"
Cohesion: 0.15
Nodes (19): _append_prism_ring_segment(), generate_kitbash_ped_arrays(), main(), parse_cli_args(), Namespace, Append a low-poly prismatic tube segment mapped to a specific UV region…, Build the geometry arrays, per-quadrant UVs, and bone weights (`Skin PLG`) for…, Build a RenderWare binary chunk: 12-byte header plus payload. (+11 more)

### Community 3 - "Harness Docs & Skill Specs"
Cohesion: 0.13
Nodes (19): AGENTS_SPEC.md Reference Copy (Canonical Skill), gtasa-ps2-skins Skill Summary (Canonical), 4-Step Skill Pipeline (evaluate prompt, build rig, quantize TXD, validate stream), AGENTS_SPEC.md Reference Copy (Claude Code Mirror), gtasa-ps2-skins Skill Summary (Claude Code Mirror), Copilot Non-Negotiable Rules, Copilot Project Instructions, DragonFF Blender GTA Exporter (+11 more)

### Community 4 - "Harness Sync (Canonical Skill)"
Cohesion: 0.23
Nodes (14): check(), copy_if_changed(), iter_bundle_files(), main(), pipeline_scripts(), Path, Byte-level drift audit across every mirror. Returns 0 when clean, 1 on any…, Every directory that must hold a byte-identical skill bundle (canonical first). (+6 more)

### Community 5 - "Harness Sync (Claude Mirror)"
Cohesion: 0.23
Nodes (14): check(), copy_if_changed(), iter_bundle_files(), main(), pipeline_scripts(), Path, Byte-level drift audit across every mirror. Returns 0 when clean, 1 on any…, Every directory that must hold a byte-identical skill bundle (canonical first). (+6 more)

### Community 6 - "Harness Sync (Root)"
Cohesion: 0.23
Nodes (14): check(), copy_if_changed(), iter_bundle_files(), main(), pipeline_scripts(), Path, Byte-level drift audit across every mirror. Returns 0 when clean, 1 on any…, Every directory that must hold a byte-identical skill bundle (canonical first). (+6 more)

### Community 7 - "TXD Quantizer (Canonical Skill)"
Cohesion: 0.24
Nodes (12): apply_ps2_color_pipeline(), build_gtasa_pc_txd_bytes(), generate_kitbash_atlas(), main(), process_and_pack_ps2_txd(), Image, Resize, compress levels to `[12, 235]`, and quantize to 256 colors with Floyd-…, Build a native `.txd` (`rwID_TEXDICTIONARY = 0x0016`) for GTA:SA PC… (+4 more)

### Community 8 - "PS2 TXD Quantizer (Root)"
Cohesion: 0.24
Nodes (12): apply_ps2_color_pipeline(), build_gtasa_pc_txd_bytes(), generate_kitbash_atlas(), main(), process_and_pack_ps2_txd(), Image, Resize, compress levels to `[12, 235]`, and quantize to 256 colors with Floyd-…, Build a native `.txd` (`rwID_TEXDICTIONARY = 0x0016`) for GTA:SA PC… (+4 more)

### Community 9 - "Rig Generator (Claude Mirror)"
Cohesion: 0.24
Nodes (11): _append_prism_ring_segment(), generate_kitbash_ped_arrays(), main(), parse_cli_args(), Namespace, Append a low-poly prismatic tube segment mapped to a specific UV region…, Build the geometry arrays, per-quadrant UVs, and bone weights (`Skin PLG`) for…, Build a RenderWare binary chunk: 12-byte header plus payload. (+3 more)

### Community 10 - "Tenpenny Police Atlas"
Cohesion: 0.33
Nodes (9): bmypol1_tenpenny Texture Atlas (256x256 PS2 Ped Skin), Gold Police Badge Detail, Black Duty Belt with Silver Buckle, Face Texture Region (bmypol1 donor head, dark skin tone), bmypol1_tenpenny Head-Swap Skin Identity, PS2 Flat-Color Palette Quantized Texturing, Exposed Skin Region (forearms/hands matching face tone), Navy Blue Uniform Trousers Region with Vertical Shading (+1 more)

### Community 11 - "Sindacco Hoodie Atlas"
Cohesion: 0.48
Nodes (7): wmydrug_sindacco Texture Atlas (256x256 PS2 Ped Skin), Folded-Back Hood Texture Region (light gray fabric with drawstrings), Hoodie Body Torso Texture Region (dark charcoal panel with vertical seams), Sindacco Head Face Texture Region (pale skin, dark hair, eyes, nose, mouth), Skin-Tone Block Region (forearms and mitten hands), Light Gray Trouser/Sleeve Fabric Region, wmydrug_sindacco Kitbashed Skin (wmydrug body + sindacco head)

### Community 12 - "Claude Jacket Atlas"
Cohesion: 0.53
Nodes (6): Claude Dark Leather Jacket Region, Forearm/Neck Skin Tone Band, Indigo Denim Jeans Region (with seam/pocket stitching), wmybar_claude Texture Atlas (256x256 PS2 Ped Atlas), White Cotton Tee Region (tshirtwhite, gray-white panel with fold lines), wmybar Head Face Region (eyes, nose, mouth on tan skin)

### Community 13 - "Kitbash Recipes & Bone Table"
Cohesion: 0.60
Nodes (5): 32-Bone GTA:SA HAnim Skeleton Table, Recipe A: wmydrug_sindacco Hood-Down + Head Swap, Recipe B: bmypol1_tenpenny Head Swap with Ethnic Consistency, Recipe C: wmybar_claude Head Swap + Clothing-Layer Retexture, artconfig.txt AddCharModel Registry (3 Kitbash Skins)

### Community 14 - "Mirror Drift-Control Design"
Cohesion: 0.67
Nodes (3): Agent-Agnostic Single-Source-of-Truth Design, Harness Entry Points, Mirrors, and Drift Control, Mirror Sync Procedure (sync_agent_harnesses.py)

## Knowledge Gaps
- **11 isolated node(s):** `Dryxio gta-3d-ai Toolchain (GTA Scout, Ariane, GTA Stuff)`, `DragonFF Blender GTA Exporter`, `RenderWare 3.6.0.3 / 0x1803FFFF Library Stamp`, `open.mp and SA-MP PC Targets`, `gtasa-ps2-skins Skill Summary (Claude Code Mirror)` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 70 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `process_and_pack_ps2_txd()` connect `TXD Quantizer (Canonical Skill)` to `Rig Generator (Canonical Skill)`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `process_and_pack_ps2_txd()` connect `PS2 TXD Quantizer (Root)` to `Ped Mesh Rig Generator (Root)`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **What connects `Dryxio gta-3d-ai Toolchain (GTA Scout, Ariane, GTA Stuff)`, `DragonFF Blender GTA Exporter`, `RenderWare 3.6.0.3 / 0x1803FFFF Library Stamp` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TXD Quantizer (Claude Mirror)` be split into smaller, more focused modules?**
  _Cohesion score 0.14624505928853754 - nodes in this community are weakly interconnected._
- **Should `Rig Generator (Canonical Skill)` be split into smaller, more focused modules?**
  _Cohesion score 0.1471861471861472 - nodes in this community are weakly interconnected._
- **Should `Ped Mesh Rig Generator (Root)` be split into smaller, more focused modules?**
  _Cohesion score 0.1471861471861472 - nodes in this community are weakly interconnected._
- **Should `Harness Docs & Skill Specs` be split into smaller, more focused modules?**
  _Cohesion score 0.1286549707602339 - nodes in this community are weakly interconnected._