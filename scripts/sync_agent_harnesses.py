#!/usr/bin/env python3
"""
sync_agent_harnesses.py — Canonical-to-mirror synchronizer for every AI harness entry point

Keeps this repository discoverable by OpenCode, OpenAI Codex, VS Code + Copilot Chat,
Google Antigravity, and Claude Code without hand-maintained duplicates:

  Canonical sources (edit these):
    AGENTS.md                            master agent specification
    scripts/*.py                         pipeline code
    .agents/skills/gtasa-ps2-skins/      canonical Agent Skill (cross-tool standard)

  Generated mirrors (never edit by hand):
    .agents/skills/gtasa-ps2-skins/scripts/*.py            copies of scripts/*.py
    .agents/skills/gtasa-ps2-skins/references/AGENTS_SPEC.md   copy of AGENTS.md
    .claude/skills/gtasa-ps2-skins/                        full skill copy (Claude Code's only skill path)

Usage:
    python3 scripts/sync_agent_harnesses.py            regenerate every mirror
    python3 scripts/sync_agent_harnesses.py --check    drift audit; exit code 1 on any mismatch
"""

import argparse
import filecmp
import shutil
import sys
from pathlib import Path
from typing import List

SKILL_NAME = "gtasa-ps2-skins"

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOT_SCRIPTS = REPO_ROOT / "scripts"
ROOT_AGENTS_MD = REPO_ROOT / "AGENTS.md"
CANONICAL_SKILL = REPO_ROOT / ".agents" / "skills" / SKILL_NAME
MIRROR_SKILL = REPO_ROOT / ".claude" / "skills" / SKILL_NAME

IGNORE_PATTERNS = shutil.ignore_patterns("__pycache__", "*.pyc")


def skill_locations() -> List[Path]:
    """Every directory that must hold a byte-identical skill bundle (canonical first)."""
    return [CANONICAL_SKILL, MIRROR_SKILL]


def pipeline_scripts() -> List[Path]:
    """Canonical pipeline scripts shipped inside every skill bundle."""
    return sorted(ROOT_SCRIPTS.glob("*.py"))


def copy_if_changed(src: Path, dst: Path) -> bool:
    """Copy `src` to `dst` byte-for-byte. Returns True when the destination changed."""
    if dst.exists() and filecmp.cmp(src, dst, shallow=False):
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return True


def sync() -> int:
    """Regenerate every mirror from the canonical sources. Returns the number of files written."""
    written = 0

    # 1. Regenerate the generated files inside the canonical skill bundle.
    for script in pipeline_scripts():
        dst = CANONICAL_SKILL / "scripts" / script.name
        if copy_if_changed(script, dst):
            print(f"  synced  {dst.relative_to(REPO_ROOT)}")
            written += 1
    spec_dst = CANONICAL_SKILL / "references" / "AGENTS_SPEC.md"
    if copy_if_changed(ROOT_AGENTS_MD, spec_dst):
        print(f"  synced  {spec_dst.relative_to(REPO_ROOT)}")
        written += 1

    # 2. Rebuild the Claude Code mirror as a fresh copy of the canonical bundle
    #    (fresh copy so files deleted from the canonical bundle vanish from the mirror too).
    if MIRROR_SKILL.exists():
        shutil.rmtree(MIRROR_SKILL)
    MIRROR_SKILL.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(CANONICAL_SKILL, MIRROR_SKILL, ignore=IGNORE_PATTERNS)
    mirrored = sum(1 for p in MIRROR_SKILL.rglob("*") if p.is_file())
    print(f"  mirrored {SKILL_NAME} -> {MIRROR_SKILL.relative_to(REPO_ROOT)} ({mirrored} files)")
    written += mirrored

    if written:
        print(f"sync_agent_harnesses: {written} file(s) written.")
    else:
        print("sync_agent_harnesses: all mirrors already up to date.")
    return written


def iter_bundle_files(bundle: Path) -> List[Path]:
    """Files in a skill bundle, excluding cache artifacts, as repo-relative POSIX paths."""
    if not bundle.exists():
        return []
    return sorted(
        p.relative_to(bundle).as_posix()
        for p in bundle.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    )


def check() -> int:
    """Byte-level drift audit across every mirror. Returns 0 when clean, 1 on any mismatch."""
    problems: List[str] = []

    # 1. Pipeline scripts must match root scripts/ in every bundle.
    # 2. AGENTS_SPEC.md must match AGENTS.md in every bundle.
    for bundle in skill_locations():
        rel = bundle.relative_to(REPO_ROOT)
        if not bundle.exists():
            problems.append(f"missing skill bundle: {rel}")
            continue
        for script in pipeline_scripts():
            copy = bundle / "scripts" / script.name
            if not copy.exists():
                problems.append(f"missing: {rel / 'scripts' / script.name}")
            elif not filecmp.cmp(script, copy, shallow=False):
                problems.append(f"drifted: {rel / 'scripts' / script.name} (source: scripts/{script.name})")
        spec = bundle / "references" / "AGENTS_SPEC.md"
        if not spec.exists():
            problems.append(f"missing: {rel / 'references' / 'AGENTS_SPEC.md'}")
        elif not filecmp.cmp(ROOT_AGENTS_MD, spec, shallow=False):
            problems.append(f"drifted: {rel / 'references' / 'AGENTS_SPEC.md'} (source: AGENTS.md)")

    # 3. The mirror tree must be a byte-identical copy of the canonical bundle.
    if CANONICAL_SKILL.exists() and MIRROR_SKILL.exists():
        canonical_files = iter_bundle_files(CANONICAL_SKILL)
        mirror_files = set(iter_bundle_files(MIRROR_SKILL))
        for rel in canonical_files:
            if rel not in mirror_files:
                problems.append(f"missing in mirror: .claude/skills/{SKILL_NAME}/{rel}")
            elif not filecmp.cmp(CANONICAL_SKILL / rel, MIRROR_SKILL / rel, shallow=False):
                problems.append(f"drifted: .claude/skills/{SKILL_NAME}/{rel}")
        for rel in sorted(mirror_files - set(canonical_files)):
            problems.append(f"stale mirror-only file: .claude/skills/{SKILL_NAME}/{rel}")

    if problems:
        print(f"sync_agent_harnesses --check: {len(problems)} problem(s) found:")
        for problem in problems:
            print(f"  - {problem}")
        print("Run `python3 scripts/sync_agent_harnesses.py` to repair.")
        return 1

    print("sync_agent_harnesses --check: PASS (no drift; all harness mirrors are byte-identical).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize canonical agent files (AGENTS.md, scripts/, .agents/skills) to every harness mirror."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="audit all mirrors for drift instead of writing them (exit code 1 on mismatch)",
    )
    args = parser.parse_args()

    if not ROOT_AGENTS_MD.exists():
        print(f"error: canonical AGENTS.md not found at {ROOT_AGENTS_MD}", file=sys.stderr)
        return 2
    if not CANONICAL_SKILL.exists():
        print(f"error: canonical skill not found at {CANONICAL_SKILL}", file=sys.stderr)
        return 2

    if args.check:
        return check()
    sync()
    return 0


if __name__ == "__main__":
    sys.exit(main())
