# GTA:SA PS2 Low-Poly Skin Agent Repository

Repository for designing, surgically kitbashing, and compiling **GTA: San Andreas** pedestrian skins (`.dff` and `.txd`) with a pure PlayStation 2 look (RenderWare 3.6.0.3 / `0x1803FFFF`), ready to run on PC under **open.mp** and **SA-MP**.

The repository is **agent-agnostic**: any LLM coding harness can open it and immediately understand the project.

## For AI agents

Start at **[AGENTS.md](AGENTS.md)** — the canonical master specification (pipeline protocol, 32-bone table, topology budgets, kitbash recipes, interview protocol). The reusable skill lives at `.agents/skills/gtasa-ps2-skins/`.

## Harness compatibility

| Harness | Instructions it reads | Skill it reads |
| :--- | :--- | :--- |
| **OpenCode** | `AGENTS.md` (automatic) | `.agents/skills/`, `.claude/skills/` |
| **OpenAI Codex** | `AGENTS.md` (automatic) | `.agents/skills/` |
| **VS Code + Copilot Chat** | `.github/copilot-instructions.md` → defers to `AGENTS.md`; `AGENTS.md` (Copilot harness) | `.agents/skills/`, `.claude/skills/` |
| **Google Antigravity** | `AGENTS.md` (automatic) | `.agents/skills/` (default location) |
| **Claude Code** | `CLAUDE.md` → `@AGENTS.md` import | `.claude/skills/` |

Single source of truth: `AGENTS.md` + `.agents/skills/gtasa-ps2-skins/`. Every other harness file is a thin import or a byte-verified mirror kept in sync by `scripts/sync_agent_harnesses.py`.

## Repository Structure

- `AGENTS.md`: Master specification, read automatically by every harness.
- `CLAUDE.md`: Claude Code shim (`@AGENTS.md` import; works on all versions, never double-read).
- `.github/copilot-instructions.md`: Always-on Copilot Chat pointer that defers to `AGENTS.md`.
- `.agents/skills/gtasa-ps2-skins/`: Canonical Agent Skill (cross-tool `.agents/skills` standard), self-contained with its own `scripts/` and `references/AGENTS_SPEC.md`.
- `.claude/skills/gtasa-ps2-skins/`: Mirrored skill copy for Claude Code (generated; do not edit).
- `scripts/build_ps2_rig_bpy.py`: 32-bone skeleton builder (`HAnim PLG 0x011E`), topological surgery engine (`hood-down`, `head-swap`, `uv-remap`), and `.dff` exporter compatible with Blender CLI (`bpy` + DragonFF) and standalone mode.
- `scripts/quantize_ps2_txd.py`: `256x256` atlas compositor, PS2 tonal compressor (`RGB 12..235`), 8-bit palette quantizer (`256 colors`, `PAL8`), and native `.txd` compiler.
- `scripts/validate_rw_stream.py`: RenderWare chunk binary validator and Pawn code generator (`AddCharModel`).
- `scripts/run_kitbash_suite.py`: Automated suite that runs and validates the 3 base tests (`wmydrug_sindacco`, `bmypol1_tenpenny`, `wmybar_claude`).
- `scripts/sync_agent_harnesses.py`: Mirror synchronizer for all harness entry points, with a `--check` drift audit.
- `output_kitbash_suite/`: Contains the already compiled and validated `.dff`, `.txd`, `_atlas.png`, `_report.json`, and `artconfig.txt` files.

## Quick Start

1. Unpack this repository and open the root folder in your agent harness of choice (OpenCode, Codex, VS Code + Copilot Chat, Antigravity, or Claude Code).
2. To regenerate and validate the full test suite from the integrated terminal:
   ```bash
   python3 scripts/run_kitbash_suite.py ./output_kitbash_suite
   ```
3. To ask the agent for new skins:
   - **Direct surgical request**: *"Take Claude's body, give him the Sindacco head, a black tee and blue jeans, and compile the .dff and .txd"*.
   - **Generic request with a guided interview**: *"Create a skin for my SA-MP Russian mafia"*.

## Keeping the Mirrors in Sync

After editing `AGENTS.md`, any file in `scripts/`, or the canonical skill, regenerate every mirror:

```bash
python3 scripts/sync_agent_harnesses.py        # rewrite mirrors
python3 scripts/sync_agent_harnesses.py --check  # byte-level drift audit (exit 1 on mismatch)
```
