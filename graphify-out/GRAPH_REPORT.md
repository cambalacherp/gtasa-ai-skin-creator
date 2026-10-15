# Graph Report - gtasa-ps2-skins-repo  (2026-10-15)

## Corpus Check
- 37 files · ~67,197 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 390 nodes · 639 edges · 18 communities (17 shown, 1 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c3e60f47`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- audit_dff_file
- audit_dff_file
- audit_dff_file
- AGENTS.md Master Specification
- .agents/skills/gtasa-ps2-skins/scripts/sync_agent_harnesses.py
- .claude/skills/gtasa-ps2-skins/scripts/sync_agent_harnesses.py
- scripts/sync_agent_harnesses.py
- scripts/vanilla_rw_kitbash.py
- process_and_pack_ps2_txd
- .agents/skills/gtasa-ps2-skins/scripts/vanilla_rw_kitbash.py
- bmypol1_tenpenny Texture Atlas (256x256 PS2 Ped Skin)
- wmydrug_sindacco Texture Atlas (256x256 PS2 Ped Skin)
- wmybar_claude Texture Atlas (256x256 PS2 Ped Atlas)
- 32-Bone GTA:SA HAnim Skeleton Table
- Harness Entry Points, Mirrors, and Drift Control
- Dryxio gta-3d-ai Toolchain (GTA Scout, Ariane, GTA Stuff)
- .claude/skills/gtasa-ps2-skins/scripts/vanilla_rw_kitbash.py
- HANDOFF — Skin `sindaco_lsv2` (cabeza `sindaco` + cuerpo `lsv2`)

## God Nodes (most connected - your core abstractions)
1. `build_kitbash_skin()` - 13 edges
2. `build_kitbash_skin()` - 13 edges
3. `build_kitbash_skin()` - 13 edges
4. `audit_dff_file()` - 10 edges
5. `audit_dff_file()` - 10 edges
6. `audit_dff_file()` - 10 edges
7. `write_standalone_gtasa_ped_dff()` - 9 edges
8. `StreamRegressions` - 9 edges
9. `parse_ped_dff()` - 9 edges
10. `write_standalone_gtasa_ped_dff()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Mirror Sync Procedure (sync_agent_harnesses.py)` --semantically_similar_to--> `Harness Entry Points, Mirrors, and Drift Control`  [INFERRED] [semantically similar]
  README.md → AGENTS.md
- `4-Step Skill Pipeline (evaluate prompt, build rig, quantize TXD, validate stream)` --semantically_similar_to--> `Prompt Specificity Router (Surgical vs Generic)`  [INFERRED] [semantically similar]
  .agents/skills/gtasa-ps2-skins/SKILL.md → AGENTS.md
- `4-Step Skill Pipeline (evaluate prompt, build rig, quantize TXD, validate stream)` --conceptually_related_to--> `Required Deliverables (.dff, .txd, vibe sheet, report)`  [INFERRED]
  .agents/skills/gtasa-ps2-skins/SKILL.md → AGENTS.md
- `Copilot Non-Negotiable Rules` --conceptually_related_to--> `PS2 Topology Budget and Validator Caps`  [INFERRED]
  .github/copilot-instructions.md → AGENTS.md
- `Copilot Non-Negotiable Rules` --conceptually_related_to--> `Required Deliverables (.dff, .txd, vibe sheet, report)`  [INFERRED]
  .github/copilot-instructions.md → AGENTS.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Agent Harness Entry Points Backed by One Canonical Spec** — agents_overview, claude_overview, _github_copilot_instructions_overview, _agents_skills_gtasa_ps2_skins_skill_overview, _claude_skills_gtasa_ps2_skins_skill_overview [EXTRACTED 1.00]
- **Garment and Skin Regions Compose the PS2 Texture Atlas** — output_kitbash_suite_wmydrug_sindacco_wmydrug_sindacco_atlas_sindacco_face_region, output_kitbash_suite_wmydrug_sindacco_wmydrug_sindacco_atlas_folded_hood_region, output_kitbash_suite_wmydrug_sindacco_wmydrug_sindacco_atlas_hoodie_body_region, output_kitbash_suite_wmydrug_sindacco_wmydrug_sindacco_atlas_skin_tone_region, output_kitbash_suite_wmydrug_sindacco_wmydrug_sindacco_atlas_trouser_region [EXTRACTED 1.00]
- **Kitbash Suite of 3 Base Tests** — agents_kitbash_recipe_a, agents_kitbash_recipe_b, agents_kitbash_recipe_c, output_kitbash_suite_artconfig_addcharmodel_registry [EXTRACTED 1.00]
- **Recipe C Vanilla Texture Splice (wmybar head + Claude jacket + tee + denim)** — output_kitbash_suite_wmybar_claude_wmybar_claude_atlas, wmybar_face_region, claude_leather_jacket_region, tshirtwhite_region, jeansdenim_region [EXTRACTED 1.00]
- **bmypol1 Head Skin-Tone Matching Across Face and Limbs** — output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_face_region, output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_skin_tone_region, output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_head_swap_skin [INFERRED 0.75]
- **Tenpenny Police Uniform Composite Layout** — output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_uniform_shirt_region, output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_badge_region, output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_duty_belt_region, output_kitbash_suite_bmypol1_tenpenny_bmypol1_tenpenny_atlas_trousers_region [INFERRED 0.85]
- **Autonomous PS2 Skin Compilation Pipeline** — agents_prompt_specificity_router, agents_required_deliverables, agents_ps2_topology_budget, agents_32_bone_skeleton [INFERRED 0.85]

## Communities (18 total, 1 thin omitted)

### Community 0 - "audit_dff_file"
Cohesion: 0.07
Nodes (34): _append_prism_ring_segment(), generate_kitbash_ped_arrays(), main(), parse_cli_args(), Namespace, Append a low-poly prismatic tube segment mapped to a specific UV region…, Build the geometry arrays, per-quadrant UVs, and bone weights (`Skin PLG`) for…, Build a RenderWare binary chunk: 12-byte header plus payload. (+26 more)

### Community 1 - "audit_dff_file"
Cohesion: 0.07
Nodes (34): _append_prism_ring_segment(), generate_kitbash_ped_arrays(), main(), parse_cli_args(), Namespace, Append a low-poly prismatic tube segment mapped to a specific UV region…, Build the geometry arrays, per-quadrant UVs, and bone weights (`Skin PLG`) for…, Build a RenderWare binary chunk: 12-byte header plus payload. (+26 more)

### Community 2 - "audit_dff_file"
Cohesion: 0.10
Nodes (22): _append_prism_ring_segment(), generate_kitbash_ped_arrays(), main(), parse_cli_args(), Namespace, Append a low-poly prismatic tube segment mapped to a specific UV region…, Build the geometry arrays, per-quadrant UVs, and bone weights (`Skin PLG`) for…, Build a RenderWare binary chunk: 12-byte header plus payload. (+14 more)

### Community 3 - "AGENTS.md Master Specification"
Cohesion: 0.13
Nodes (19): AGENTS_SPEC.md Reference Copy (Canonical Skill), gtasa-ps2-skins Skill Summary (Canonical), 4-Step Skill Pipeline (evaluate prompt, build rig, quantize TXD, validate stream), AGENTS_SPEC.md Reference Copy (Claude Code Mirror), gtasa-ps2-skins Skill Summary (Claude Code Mirror), Copilot Non-Negotiable Rules, Copilot Project Instructions, DragonFF Blender GTA Exporter (+11 more)

### Community 4 - ".agents/skills/gtasa-ps2-skins/scripts/sync_agent_harnesses.py"
Cohesion: 0.23
Nodes (14): check(), copy_if_changed(), iter_bundle_files(), main(), pipeline_scripts(), Path, Byte-level drift audit across every mirror. Returns 0 when clean, 1 on any…, Every directory that must hold a byte-identical skill bundle (canonical first). (+6 more)

### Community 5 - ".claude/skills/gtasa-ps2-skins/scripts/sync_agent_harnesses.py"
Cohesion: 0.23
Nodes (14): check(), copy_if_changed(), iter_bundle_files(), main(), pipeline_scripts(), Path, Byte-level drift audit across every mirror. Returns 0 when clean, 1 on any…, Every directory that must hold a byte-identical skill bundle (canonical first). (+6 more)

### Community 6 - "scripts/sync_agent_harnesses.py"
Cohesion: 0.23
Nodes (14): check(), copy_if_changed(), iter_bundle_files(), main(), pipeline_scripts(), Path, Byte-level drift audit across every mirror. Returns 0 when clean, 1 on any…, Every directory that must hold a byte-identical skill bundle (canonical first). (+6 more)

### Community 7 - "scripts/vanilla_rw_kitbash.py"
Cohesion: 0.08
Nodes (45): apply_ps2_color_pipeline(), Resize, compress levels to `[12, 235]`, and quantize to 256 colors with Floyd-…, font(), main(), posed_vertices(), Apply hierarchical bone rotations around pivots from inverse bind matrices., Two-sided, nearest-sampled texture rasterization with a true depth buffer., render_view() (+37 more)

### Community 8 - "process_and_pack_ps2_txd"
Cohesion: 0.27
Nodes (10): build_gtasa_pc_txd_bytes(), generate_kitbash_atlas(), main(), process_and_pack_ps2_txd(), Image, Build a native `.txd` (`rwID_TEXDICTIONARY = 0x0016`) for GTA:SA PC…, Run atlas splicing/composition, PS2 quantization, and `.txd` packing., Pack a 12-byte RenderWare header (`type`, `size`, `version`) plus payload. (+2 more)

### Community 9 - ".agents/skills/gtasa-ps2-skins/scripts/vanilla_rw_kitbash.py"
Cohesion: 0.08
Nodes (43): font(), main(), posed_vertices(), Apply hierarchical bone rotations around pivots from inverse bind matrices., Two-sided, nearest-sampled texture rasterization with a true depth buffer., render_view(), build_kitbash_skin(), build_txd_8888() (+35 more)

### Community 10 - "bmypol1_tenpenny Texture Atlas (256x256 PS2 Ped Skin)"
Cohesion: 0.33
Nodes (9): bmypol1_tenpenny Texture Atlas (256x256 PS2 Ped Skin), Gold Police Badge Detail, Black Duty Belt with Silver Buckle, Face Texture Region (bmypol1 donor head, dark skin tone), bmypol1_tenpenny Head-Swap Skin Identity, PS2 Flat-Color Palette Quantized Texturing, Exposed Skin Region (forearms/hands matching face tone), Navy Blue Uniform Trousers Region with Vertical Shading (+1 more)

### Community 11 - "wmydrug_sindacco Texture Atlas (256x256 PS2 Ped Skin)"
Cohesion: 0.48
Nodes (7): wmydrug_sindacco Texture Atlas (256x256 PS2 Ped Skin), Folded-Back Hood Texture Region (light gray fabric with drawstrings), Hoodie Body Torso Texture Region (dark charcoal panel with vertical seams), Sindacco Head Face Texture Region (pale skin, dark hair, eyes, nose, mouth), Skin-Tone Block Region (forearms and mitten hands), Light Gray Trouser/Sleeve Fabric Region, wmydrug_sindacco Kitbashed Skin (wmydrug body + sindacco head)

### Community 12 - "wmybar_claude Texture Atlas (256x256 PS2 Ped Atlas)"
Cohesion: 0.53
Nodes (6): Claude Dark Leather Jacket Region, Forearm/Neck Skin Tone Band, Indigo Denim Jeans Region (with seam/pocket stitching), wmybar_claude Texture Atlas (256x256 PS2 Ped Atlas), White Cotton Tee Region (tshirtwhite, gray-white panel with fold lines), wmybar Head Face Region (eyes, nose, mouth on tan skin)

### Community 13 - "32-Bone GTA:SA HAnim Skeleton Table"
Cohesion: 0.60
Nodes (5): 32-Bone GTA:SA HAnim Skeleton Table, Recipe A: wmydrug_sindacco Hood-Down + Head Swap, Recipe B: bmypol1_tenpenny Head Swap with Ethnic Consistency, Recipe C: wmybar_claude Head Swap + Clothing-Layer Retexture, artconfig.txt AddCharModel Registry (3 Kitbash Skins)

### Community 14 - "Harness Entry Points, Mirrors, and Drift Control"
Cohesion: 0.67
Nodes (3): Agent-Agnostic Single-Source-of-Truth Design, Harness Entry Points, Mirrors, and Drift Control, Mirror Sync Procedure (sync_agent_harnesses.py)

### Community 16 - ".claude/skills/gtasa-ps2-skins/scripts/vanilla_rw_kitbash.py"
Cohesion: 0.08
Nodes (43): font(), main(), posed_vertices(), Apply hierarchical bone rotations around pivots from inverse bind matrices., Two-sided, nearest-sampled texture rasterization with a true depth buffer., render_view(), build_kitbash_skin(), build_txd_8888() (+35 more)

### Community 17 - "HANDOFF — Skin `sindaco_lsv2` (cabeza `sindaco` + cuerpo `lsv2`)"
Cohesion: 0.11
Nodes (17): 1. Objetivo, 2.1 El kitbash real ya compila end-to-end, 2.2 La estrategia de costura cambió (importante), 2.3 Verificación de malla del `.dff` actual (recién medida), 2.4 Estructura binaria verificada byte a byte, 2. Estado actual: qué está HECHO y VERIFICADO, 3. Por qué el validador da FAIL (ya diagnosticado, son 3 bugs del validador), 4. Pasos restantes (en orden) (+9 more)

## Knowledge Gaps
- **24 isolated node(s):** `1. Objetivo`, `2.1 El kitbash real ya compila end-to-end`, `2.2 La estrategia de costura cambió (importante)`, `2.3 Verificación de malla del `.dff` actual (recién medida)`, `2.4 Estructura binaria verificada byte a byte` (+19 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 144 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_ped_dff()` connect `.agents/skills/gtasa-ps2-skins/scripts/vanilla_rw_kitbash.py` to `audit_dff_file`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `parse_ped_dff()` connect `.claude/skills/gtasa-ps2-skins/scripts/vanilla_rw_kitbash.py` to `audit_dff_file`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `parse_ped_dff()` connect `scripts/vanilla_rw_kitbash.py` to `audit_dff_file`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **What connects `1. Objetivo`, `2.1 El kitbash real ya compila end-to-end`, `2.2 La estrategia de costura cambió (importante)` to the rest of the system?**
  _24 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `audit_dff_file` be split into smaller, more focused modules?**
  _Cohesion score 0.0730804810360777 - nodes in this community are weakly interconnected._
- **Should `audit_dff_file` be split into smaller, more focused modules?**
  _Cohesion score 0.0730804810360777 - nodes in this community are weakly interconnected._
- **Should `audit_dff_file` be split into smaller, more focused modules?**
  _Cohesion score 0.10338680926916222 - nodes in this community are weakly interconnected._