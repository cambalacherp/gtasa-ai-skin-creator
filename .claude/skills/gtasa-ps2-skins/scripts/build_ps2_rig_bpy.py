#!/usr/bin/env python3
"""
build_ps2_rig_bpy.py — Headless Builder and Surgical Kitbashing Engine in Blender (bpy + DragonFF)
for GTA: San Andreas Skins (PS2 style on PC / `open.mp` / SA-MP).

Supports both base archetypes and the 3 vanilla surgery / kitbash presets:
1. `wmydrug_sindacco`:
   - `wmydrug` body (ID 29) with the hood remodeled/folded back onto `Spine1 (4)`
     + grafted `sindaco` head (ID 119, Johnny Sindacco) welded at `Neck (5)`.
2. `bmypol1_tenpenny`:
   - African-American head with the `bmypol1` beret/cap (ID 66) welded onto the short-sleeve
     LSPD uniform, badge, and tactical belt of `tenpen` (ID 265, Frank Tenpenny).
3. `wmybar_claude`:
   - `wmybar` head (ID 177, Barber) welded onto the `claude` body (ID 299, open leather
     jacket), with separate UV regions for a white inner tee and blue jeans.

CLI usage:
    python3 build_ps2_rig_bpy.py --preset wmydrug_sindacco --outdir ./output/wmydrug_sindacco
    blender -b -P build_ps2_rig_bpy.py -- --preset wmybar_claude --outdir ./output/wmybar_claude
"""

import argparse
import json
import math
import os
import struct
import sys
from typing import Dict, List, Optional, Tuple

try:
    import bpy
    import bmesh
    from mathutils import Matrix, Vector, Euler
    HAS_BPY = True
except ImportError:
    HAS_BPY = False

RW_VERSION_GTASA = 0x1803FFFF

# ==============================================================================
# 1. OFFICIAL GTA: SAN ANDREAS 32-BONE TABLE (HAnim PLG 0x011E)
# ==============================================================================
GTA_SA_PED_BONES: List[Tuple[int, int, str, Optional[str], Tuple[float, float, float], Tuple[float, float, float], int]] = [
    (0,  0,   " Root",            None,               (0.000, 0.000, 0.000), (0.000, 0.000, 0.100), 0x02),
    (1,  1,   " Pelvis",          " Root",            (0.000, 0.000, 0.920), (0.000, 0.000, 0.980), 0x02),
    (2,  2,   " R Pelvis",        " Pelvis",          (0.000, 0.000, 0.920), (0.000, 0.000, 1.020), 0x00),
    (3,  3,   " Spine",           " Pelvis",          (0.000, 0.000, 1.020), (0.000, 0.000, 1.220), 0x00),
    (4,  4,   " Spine1",          " Spine",           (0.000, 0.000, 1.220), (0.000, 0.000, 1.440), 0x00),
    (5,  5,   " Neck",            " Spine1",          (0.000, 0.000, 1.440), (0.000, 0.000, 1.540), 0x00),
    (6,  6,   " Head2",           " Neck",            (0.000, 0.000, 1.540), (0.000, 0.000, 1.560), 0x00),
    (7,  7,   " Head1",           " Head2",           (0.000, 0.000, 1.560), (0.000, 0.000, 1.580), 0x00),
    (8,  8,   " Head",            " Head1",           (0.000, 0.000, 1.580), (0.000, 0.000, 1.820), 0x01),
    # Right arm
    (9,  21,  "Bip01 R Clavicle", " Spine1",          (-0.040, 0.000, 1.400), (-0.170, 0.000, 1.400), 0x02),
    (10, 22,  " R UpperArm",      "Bip01 R Clavicle", (-0.170, 0.000, 1.400), (-0.430, 0.000, 1.400), 0x00),
    (11, 23,  " R ForeArm",       " R UpperArm",      (-0.430, 0.000, 1.400), (-0.670, 0.000, 1.400), 0x00),
    (12, 24,  " R Hand",          " R ForeArm",       (-0.670, 0.000, 1.400), (-0.760, 0.000, 1.400), 0x00),
    (13, 25,  " R Finger",        " R Hand",          (-0.760, 0.000, 1.400), (-0.850, 0.000, 1.400), 0x01),
    (14, 26,  " R Finger01",      " R Hand",          (-0.720, -0.040, 1.390), (-0.790, -0.070, 1.380), 0x01),
    # Left arm
    (15, 31,  "Bip01 L Clavicle", " Spine1",          (0.040, 0.000, 1.400), (0.170, 0.000, 1.400), 0x02),
    (16, 32,  " L UpperArm",      "Bip01 L Clavicle", (0.170, 0.000, 1.400), (0.430, 0.000, 1.400), 0x00),
    (17, 33,  " L ForeArm",       " L UpperArm",      (0.430, 0.000, 1.400), (0.670, 0.000, 1.400), 0x00),
    (18, 34,  " L Hand",          " L ForeArm",       (0.670, 0.000, 1.400), (0.760, 0.000, 1.400), 0x00),
    (19, 35,  " L Finger",        " L Hand",          (0.760, 0.000, 1.400), (0.850, 0.000, 1.400), 0x01),
    (20, 36,  " L Finger01",      " L Hand",          (0.720, -0.040, 1.390), (0.790, -0.070, 1.380), 0x01),
    # Left leg
    (21, 41,  " L Thigh",         " Pelvis",          (0.105, 0.000, 0.920), (0.105, 0.000, 0.500), 0x02),
    (22, 42,  " L Calf",          " L Thigh",         (0.105, 0.000, 0.500), (0.105, 0.000, 0.100), 0x00),
    (23, 43,  " L Foot",          " L Calf",          (0.105, 0.000, 0.100), (0.105, -0.100, 0.030), 0x00),
    (24, 44,  " L Toe0",          " L Foot",          (0.105, -0.100, 0.030), (0.105, -0.220, 0.030), 0x01),
    # Right leg
    (25, 51,  " R Thigh",         " Pelvis",          (-0.105, 0.000, 0.920), (-0.105, 0.000, 0.500), 0x02),
    (26, 52,  " R Calf",          " R Thigh",         (-0.105, 0.000, 0.500), (-0.105, 0.000, 0.100), 0x00),
    (27, 53,  " R Foot",          " R Calf",          (-0.105, 0.000, 0.100), (-0.105, -0.100, 0.030), 0x00),
    (28, 54,  " R Toe0",          " R Foot",          (-0.105, -0.100, 0.030), (-0.105, -0.220, 0.030), 0x01),
    # Auxiliary volume bones (torso)
    (29, 201, " Belly",           " Spine",           (0.000, -0.020, 1.060), (0.000, -0.120, 1.060), 0x01),
    (30, 301, " R Breast",        " Spine1",          (-0.075, -0.030, 1.320), (-0.075, -0.130, 1.320), 0x01),
    (31, 302, " L Breast",        " Spine1",          (0.075, -0.030, 1.320), (0.075, -0.130, 1.320), 0x01),
]

FORBIDDEN_WEIGHT_BONES = {" Root", " Pelvis", " Head2", " Head1"}

# Metadata for the 3 requested surgical kitbash presets
KITBASH_PRESETS: Dict[str, Dict[str, object]] = {
    "wmydrug_sindacco": {
        "skin_name": "wmydrug_sindacco",
        "tex_name": "wmydrug_sind",
        "base_skin_id": 29,     # wmydrug (Drug Dealer)
        "donor_head_id": 119,   # sindaco (Johnny Sindacco)
        "custom_skin_id": 20001,
        "description": "wmydrug body (ID 29) with the hood folded back onto Spine1(4) + Johnny Sindacco head (ID 119) welded at Neck(5).",
        "torso_rx": 0.185,
        "torso_ry": 0.135,
        "leg_rx": 0.095,
        "has_hood_down": True,
        "has_duty_belt": False,
        "has_open_jacket_collar": False,
        "head_style": "sindacco_pompadour",
    },
    "bmypol1_tenpenny": {
        "skin_name": "bmypol1_tenpenny",
        "tex_name": "bmypol_tenp",
        "base_skin_id": 265,    # tenpen (Officer Frank Tenpenny)
        "donor_head_id": 66,    # bmypol1 (Black Male Pool Player)
        "custom_skin_id": 20002,
        "description": "African-American head with the bmypol1 beret/cap (ID 66) welded onto Tenpenny's short-sleeve LSPD uniform and tactical belt (ID 265).",
        "torso_rx": 0.175,
        "torso_ry": 0.125,
        "leg_rx": 0.088,
        "has_hood_down": False,
        "has_duty_belt": True,
        "has_open_jacket_collar": False,
        "head_style": "bmypol1_cap",
    },
    "wmybar_claude": {
        "skin_name": "wmybar_claude",
        "tex_name": "wmybar_clau",
        "base_skin_id": 299,    # claude (Claude Speed)
        "donor_head_id": 177,   # wmybar (Barber)
        "custom_skin_id": 20003,
        "description": "wmybar head (ID 177) on Claude's body (ID 299) with an open black leather jacket, a white inner tee (tshirtwhite), and blue jeans (jeansdenim).",
        "torso_rx": 0.180,
        "torso_ry": 0.130,
        "leg_rx": 0.090,
        "has_hood_down": False,
        "has_duty_belt": False,
        "has_open_jacket_collar": True,
        "head_style": "wmybar_short",
    },
}


# ==============================================================================
# 2. SURGICAL GEOMETRY GENERATOR (FOLDED HOOD, LSPD BELT, CLAUDE JACKET)
# ==============================================================================
def _append_prism_ring_segment(
    vertices: List[Tuple[float, float, float]],
    normals: List[Tuple[float, float, float]],
    uvs: List[Tuple[float, float]],
    triangles: List[Tuple[int, int, int, int]],
    bone_indices: List[Tuple[int, int, int, int]],
    bone_weights: List[Tuple[float, float, float, float]],
    b0: int,
    b1: int,
    z0: float,
    z1: float,
    xc: float,
    yc: float,
    rx0: float,
    ry0: float,
    rx1: float,
    ry1: float,
    sides: int,
    segs: int,
    uv_rect: Tuple[float, float, float, float],
    front_chest_uv_rect: Optional[Tuple[float, float, float, float]] = None,
) -> None:
    """
    Append a low-poly prismatic tube segment mapped to a specific UV region `uv_rect = (u0, v0, u1, v1)`.
    If `front_chest_uv_rect` is provided, the central front faces (`y < 0`) are mapped to the
    inner-tee region (for example, the white tee under Claude's open leather jacket).
    """
    u0, v0, u1, v1 = uv_rect
    base_v_idx = len(vertices)
    for s in range(segs + 1):
        t = s / float(segs)
        z = z0 + (z1 - z0) * t
        rx = rx0 + (rx1 - rx0) * t
        ry = ry0 + (ry1 - ry0) * t
        w0 = round(1.0 - t * 0.45, 4) if b0 != b1 else 1.0
        w1 = round(1.0 - w0, 4) if b0 != b1 else 0.0

        for i in range(sides):
            ang = (2.0 * math.pi * i) / float(sides)
            nx = math.cos(ang)
            ny = math.sin(ang)
            x = xc + nx * rx
            y = yc + ny * ry
            vertices.append((x, y, z))
            normals.append((nx, ny, 0.0))

            # Claude's front chest (`ny < -0.45`) with a white inner-tee region:
            if front_chest_uv_rect is not None and ny < -0.45:
                fu0, fv0, fu1, fv1 = front_chest_uv_rect
                u = fu0 + ((nx + 1.0) * 0.5) * (fu1 - fu0)
                v = fv0 + t * (fv1 - fv0)
            else:
                u = u0 + (i / float(sides)) * (u1 - u0)
                v = v0 + t * (v1 - v0)

            uvs.append((u, v))
            bone_indices.append((b0, b1 if w1 > 0 else 0, 0, 0))
            bone_weights.append((w0, w1, 0.0, 0.0))

    for s in range(segs):
        r0 = base_v_idx + s * sides
        r1 = base_v_idx + (s + 1) * sides
        for i in range(sides):
            ni = (i + 1) % sides
            triangles.append((r0 + i, r0 + ni, r1 + ni, 0))
            triangles.append((r0 + i, r1 + ni, r1 + i, 0))


def generate_kitbash_ped_arrays(preset_name: Optional[str] = None):
    """
    Build the geometry arrays, per-quadrant UVs, and bone weights (`Skin PLG`)
    for any of the 3 kitbash test cases or the base archetype:
    - Head UV quadrant (`Head 8` / `Neck 5`): `u in [0.02, 0.48], v in [0.52, 0.98]`
    - Outer torso / jacket / uniform UV quadrant (`Spine 3`, `Spine1 4`): `u in [0.52, 0.98], v in [0.52, 0.98]`
    - Inner tee / folded hood UV sub-island: `u in [0.54, 0.76], v in [0.54, 0.74]`
    - Pants / jeans UV quadrant (`R Pelvis 2`, `Thigh`, `Calf`): `u in [0.02, 0.48], v in [0.02, 0.48]`
    - Hands / arms / footwear UV quadrant: `u in [0.52, 0.98], v in [0.02, 0.48]`
    """
    cfg = KITBASH_PRESETS.get(preset_name or "", {
        "torso_rx": 0.175,
        "torso_ry": 0.125,
        "leg_rx": 0.090,
        "has_hood_down": False,
        "has_duty_belt": False,
        "has_open_jacket_collar": False,
        "head_style": "default",
    })

    vertices: List[Tuple[float, float, float]] = []
    normals: List[Tuple[float, float, float]] = []
    uvs: List[Tuple[float, float]] = []
    triangles: List[Tuple[int, int, int, int]] = []
    bone_indices: List[Tuple[int, int, int, int]] = []
    bone_weights: List[Tuple[float, float, float, float]] = []

    trx = float(cfg["torso_rx"])
    try_ = float(cfg["torso_ry"])
    lrx = float(cfg["leg_rx"])

    uv_head = (0.04, 0.54, 0.46, 0.96)
    uv_torso = (0.54, 0.54, 0.96, 0.96)
    uv_inner_shirt = (0.76, 0.54, 0.96, 0.74) if cfg.get("has_open_jacket_collar") else None
    uv_legs = (0.04, 0.04, 0.46, 0.46)
    uv_arms_shoes = (0.54, 0.04, 0.96, 0.46)

    # 1. Pelvis and waist (extra volume if it wears Tenpenny's police duty belt)
    belt_bulge = 0.016 if cfg.get("has_duty_belt") else 0.0
    _append_prism_ring_segment(
        vertices, normals, uvs, triangles, bone_indices, bone_weights,
        2, 3, 0.88, 1.04, 0.0, 0.0,
        trx * 0.92 + belt_bulge, try_ * 0.92 + belt_bulge,
        trx * 0.88, try_ * 0.88,
        sides=8, segs=3, uv_rect=uv_legs
    )

    # 2. Abdomen (`Spine 3`) and ribcage (`Spine1 4`)
    _append_prism_ring_segment(
        vertices, normals, uvs, triangles, bone_indices, bone_weights,
        3, 4, 1.04, 1.24, 0.0, 0.0,
        trx * 0.88, try_ * 0.88,
        trx * 0.96, try_ * 0.96,
        sides=8, segs=4, uv_rect=uv_torso, front_chest_uv_rect=uv_inner_shirt
    )
    _append_prism_ring_segment(
        vertices, normals, uvs, triangles, bone_indices, bone_weights,
        4, 5, 1.24, 1.45, 0.0, 0.0,
        trx * 0.96, try_ * 0.96,
        trx * 1.04, try_ * 1.00,
        sides=8, segs=4, uv_rect=uv_torso, front_chest_uv_rect=uv_inner_shirt
    )

    # 3. SPECIAL SURGERY CASE 1 (`wmydrug_sindacco`): hood folded back onto `Spine1 (4)`
    if cfg.get("has_hood_down"):
        # Instead of covering `Head (8)`, the hood rests on the nape/upper back (`y = +0.11m, z = 1.35..1.47m`)
        # weighted 80% to `Spine1 (4)` and 20% to `Neck (5)` so it does not rotate rigidly with the head.
        _append_prism_ring_segment(
            vertices, normals, uvs, triangles, bone_indices, bone_weights,
            4, 5, 1.34, 1.47, 0.0, 0.105,
            0.135, 0.075,
            0.095, 0.055,
            sides=8, segs=3, uv_rect=uv_torso
        )

    # 4. SPECIAL SURGERY CASE 3 (`wmybar_claude`): Claude leather-jacket collar lapels
    if cfg.get("has_open_jacket_collar"):
        _append_prism_ring_segment(
            vertices, normals, uvs, triangles, bone_indices, bone_weights,
            4, 5, 1.41, 1.50, 0.0, 0.015,
            0.095, 0.085,
            0.105, 0.090,
            sides=8, segs=2, uv_rect=uv_torso
        )

    # 5. Welded neck (`Neck 5` -> `Head 8`) and donor head (`sindacco`, `bmypol1`, or `wmybar`)
    _append_prism_ring_segment(
        vertices, normals, uvs, triangles, bone_indices, bone_weights,
        5, 8, 1.44, 1.56, 0.0, 0.0,
        0.064, 0.064, 0.060, 0.060,
        sides=8, segs=2, uv_rect=uv_head
    )

    head_style = str(cfg.get("head_style", "default"))
    if head_style == "sindacco_pompadour":
        # Johnny Sindacco's angular jaw and raised slicked pompadour (`sindaco`)
        _append_prism_ring_segment(
            vertices, normals, uvs, triangles, bone_indices, bone_weights,
            8, 8, 1.56, 1.84, 0.0, -0.01,
            0.088, 0.098, 0.096, 0.114,
            sides=8, segs=5, uv_rect=uv_head
        )
    elif head_style == "bmypol1_cap":
        # `bmypol1` skull with a slightly tilted sport cap/beret
        _append_prism_ring_segment(
            vertices, normals, uvs, triangles, bone_indices, bone_weights,
            8, 8, 1.56, 1.83, 0.0, -0.015,
            0.090, 0.096, 0.102, 0.112,
            sides=8, segs=5, uv_rect=uv_head
        )
    else:
        # Clean barber cut (`wmybar`)
        _append_prism_ring_segment(
            vertices, normals, uvs, triangles, bone_indices, bone_weights,
            8, 8, 1.56, 1.82, 0.0, -0.008,
            0.086, 0.095, 0.092, 0.102,
            sides=8, segs=5, uv_rect=uv_head
        )

    # 6. Arms and mitten hands ("Mitten Hands" PS2)
    for b_arm0, b_arm1, b_hand0, b_hand1, xc_arm, xc_hand in [
        (10, 11, 12, 13, -0.300, -0.750),
        (16, 17, 18, 19,  0.300,  0.750),
    ]:
        _append_prism_ring_segment(
            vertices, normals, uvs, triangles, bone_indices, bone_weights,
            b_arm0, b_arm1, 1.36, 1.44, xc_arm, 0.0,
            0.24, 0.052, 0.24, 0.046,
            sides=8, segs=4, uv_rect=uv_torso
        )
        _append_prism_ring_segment(
            vertices, normals, uvs, triangles, bone_indices, bone_weights,
            b_hand0, b_hand1, 1.37, 1.43, xc_hand, 0.0,
            0.12, 0.032, 0.11, 0.026,
            sides=8, segs=3, uv_rect=uv_arms_shoes
        )

    # 7. Legs and chunky PS2 footwear
    for b_th, b_ca, b_ft, b_to, x_leg in [
        (21, 22, 23, 24,  0.105),
        (25, 26, 27, 28, -0.105),
    ]:
        _append_prism_ring_segment(
            vertices, normals, uvs, triangles, bone_indices, bone_weights,
            b_th, b_ca, 0.50, 0.92, x_leg, 0.0,
            lrx, lrx, lrx * 0.84, lrx * 0.84,
            sides=8, segs=4, uv_rect=uv_legs
        )
        _append_prism_ring_segment(
            vertices, normals, uvs, triangles, bone_indices, bone_weights,
            b_ca, b_ft, 0.08, 0.50, x_leg, 0.0,
            lrx * 0.84, lrx * 0.84, lrx * 0.72, lrx * 0.72,
            sides=8, segs=4, uv_rect=uv_legs
        )
        _append_prism_ring_segment(
            vertices, normals, uvs, triangles, bone_indices, bone_weights,
            b_ft, b_to, 0.00, 0.08, x_leg, -0.04,
            0.058, 0.115, 0.054, 0.105,
            sides=8, segs=2, uv_rect=uv_arms_shoes
        )

    return vertices, normals, uvs, triangles, bone_indices, bone_weights


# ==============================================================================
# 3. RENDERWARE 3.6.0.3 BINARY SERIALIZER (0x1803FFFF) FOR DFF EXPORT
# ==============================================================================
def _rw_chunk(chunk_type: int, payload: bytes, version: int = RW_VERSION_GTASA) -> bytes:
    """Build a RenderWare binary chunk: 12-byte header plus payload."""
    return struct.pack("<III", chunk_type, len(payload), version) + payload


def write_standalone_gtasa_ped_dff(
    output_dff_path: str,
    tex_name: str = "ped_atlas",
    preset_name: Optional[str] = None,
) -> Dict[str, object]:
    """
    Compile a pedestrian `.dff` for GTA: San Andreas (`0x1803FFFF`) with the 32 official
    bones (`HAnim PLG 0x011E`), `Geometry (0x000F)`, `Skin PLG (0x0116)`, and `Atomic (0x0014)`.
    """
    clean_tex = os.path.splitext(os.path.basename(tex_name))[0].lower()[:31]
    vertices, normals, uvs, triangles, bone_indices, bone_weights = generate_kitbash_ped_arrays(preset_name)

    num_verts = len(vertices)
    num_tris = len(triangles)
    num_bones = len(GTA_SA_PED_BONES)

    # 1. rwID_FRAMELIST (0x000E)
    frame_struct = struct.pack("<I", num_bones)
    name_to_frame_idx = {b[2]: idx for idx, b in enumerate(GTA_SA_PED_BONES)}

    for idx, bone_id, name, parent_name, head, tail, flags in GTA_SA_PED_BONES:
        parent_idx = name_to_frame_idx[parent_name] if parent_name else -1
        frame_struct += struct.pack(
            "<9f3fiI",
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
            *head,
            parent_idx,
            0x00020003,
        )

    frame_extensions = b""
    for idx, bone_id, name, parent_name, head, tail, flags in GTA_SA_PED_BONES:
        if idx == 0:
            hanim_payload = struct.pack("<III", 0x0100, bone_id, num_bones)
            hanim_payload += struct.pack("<II", 0, 36)
            for b_idx, b_id, b_name, b_parent, b_head, b_tail, b_flags in GTA_SA_PED_BONES:
                hanim_payload += struct.pack("<III", b_id, b_idx, b_flags)
        else:
            hanim_payload = struct.pack("<III", 0x0100, bone_id, 0)

        hanim_chunk = _rw_chunk(0x011E, hanim_payload)
        node_name_chunk = _rw_chunk(0x0253F2FE, name.encode("ascii")[:31])
        frame_extensions += _rw_chunk(0x0003, hanim_chunk + node_name_chunk)

    framelist_chunk = _rw_chunk(0x000E, _rw_chunk(0x0001, frame_struct) + frame_extensions)

    # 2. rwID_GEOMETRY (0x000F) — no rpGEOMETRYPRELIT (0x08), for clean dynamic lighting
    geom_flags = 0x00000076
    geom_header = struct.pack(
        "<BBHIIIfff",
        geom_flags & 0xFF,
        1,  # 1 UV set
        0,
        num_tris,
        num_verts,
        1,
        1.0, 1.0, 1.0,
    )
    uv_bytes = b"".join(struct.pack("<ff", u, v) for u, v in uvs)
    tri_bytes = b"".join(struct.pack("<HHHH", v2, v1, mat_id, v3) for v1, v2, v3, mat_id in triangles)
    bsphere = struct.pack("<ffffII", 0.0, 0.0, 0.95, 1.15, 1, 1)
    vert_bytes = b"".join(struct.pack("<fff", x, y, z) for x, y, z in vertices)
    norm_bytes = b"".join(struct.pack("<fff", nx, ny, nz) for nx, ny, nz in normals)

    geom_struct_chunk = _rw_chunk(
        0x0001,
        geom_header + uv_bytes + tri_bytes + bsphere + vert_bytes + norm_bytes
    )

    tex_name_padded = clean_tex.encode("ascii") + b"\x00"
    if len(tex_name_padded) % 4 != 0:
        tex_name_padded += b"\x00" * (4 - (len(tex_name_padded) % 4))

    tex_chunk = _rw_chunk(
        0x0006,
        _rw_chunk(0x0001, struct.pack("<HH", 0x1106, 0))
        + _rw_chunk(0x0002, tex_name_padded)
        + _rw_chunk(0x0002, b"\x00\x00\x00\x00")
        + _rw_chunk(0x0003, b"")
    )
    mat_struct = struct.pack("<I4BIIfff", 0, 255, 255, 255, 255, 0, 1, 0.65, 0.0, 1.0)
    mat_chunk = _rw_chunk(0x0007, _rw_chunk(0x0001, mat_struct) + tex_chunk + _rw_chunk(0x0003, b""))
    matlist_chunk = _rw_chunk(0x0008, _rw_chunk(0x0001, struct.pack("<II", 1, 0xFFFFFFFF)) + mat_chunk)

    # Skin PLG (0x0116)
    used_bones = list(range(1, num_bones))
    skin_header = struct.pack("<BBBB", num_bones, len(used_bones), 4, 0)
    used_bones_bytes = bytes(used_bones)
    b_idx_bytes = b"".join(struct.pack("<BBBB", *bi) for bi in bone_indices)
    b_wgt_bytes = b"".join(struct.pack("<ffff", *bw) for bw in bone_weights)

    inv_matrices = b""
    for idx, bone_id, name, parent_name, head, tail, flags in GTA_SA_PED_BONES:
        hx, hy, hz = head
        inv_matrices += struct.pack(
            "<16f",
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            -hx, -hy, -hz, 1.0,
        )
    skin_plg_chunk = _rw_chunk(
        0x0116,
        skin_header + used_bones_bytes + b_idx_bytes + b_wgt_bytes + inv_matrices + struct.pack("<III", 0, 0, 0)
    )

    geom_chunk = _rw_chunk(0x000F, geom_struct_chunk + matlist_chunk + _rw_chunk(0x0003, skin_plg_chunk))
    geomlist_chunk = _rw_chunk(0x001A, _rw_chunk(0x0001, struct.pack("<I", 1)) + geom_chunk)

    # 3. rwID_ATOMIC (0x0014) + Right To Render (0x001F)
    atomic_struct = _rw_chunk(0x0001, struct.pack("<IIII", 0, 0, 5, 0))
    rtr_chunk = _rw_chunk(0x001F, struct.pack("<II", 0x0116, 0x00000001))
    atomic_chunk = _rw_chunk(0x0014, atomic_struct + _rw_chunk(0x0003, rtr_chunk))

    # 4. rwID_CLUMP (0x0010)
    clump_struct = _rw_chunk(0x0001, struct.pack("<III", 1, 0, 0))
    clump_chunk = _rw_chunk(
        0x0010,
        clump_struct + framelist_chunk + geomlist_chunk + atomic_chunk + _rw_chunk(0x0003, b"")
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_dff_path)), exist_ok=True)
    with open(output_dff_path, "wb") as f:
        f.write(clump_chunk)

    return {
        "dff_path": output_dff_path,
        "preset": preset_name or "custom",
        "rw_version": hex(RW_VERSION_GTASA),
        "bone_count": num_bones,
        "vertex_count": num_verts,
        "triangle_count": num_tris,
        "texture_name": clean_tex,
    }


def parse_cli_args() -> argparse.Namespace:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = argv[1:]

    parser = argparse.ArgumentParser(
        description="Low-poly PS2 skin generator and surgical kitbasher for GTA:SA (bpy + DragonFF)"
    )
    parser.add_argument(
        "--preset",
        default=None,
        choices=list(KITBASH_PRESETS.keys()),
        help="Surgical preset (wmydrug_sindacco, bmypol1_tenpenny, wmybar_claude)",
    )
    parser.add_argument("--skin-name", default="mechanic_ls", help="Skin identifier")
    parser.add_argument("--tex-name", default="mech_ps2", help="Texture name in the .txd (<=31 chars, lowercase)")
    parser.add_argument("--outdir", default="./output/mechanic_ls", help="Output folder")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_cli_args()
    if args.preset:
        p = KITBASH_PRESETS[args.preset]
        skin_name = str(p["skin_name"])
        tex_name = str(p["tex_name"])
    else:
        skin_name = args.skin_name
        tex_name = args.tex_name

    os.makedirs(args.outdir, exist_ok=True)
    dff_out = os.path.join(args.outdir, f"{skin_name}.dff")

    info = write_standalone_gtasa_ped_dff(dff_out, tex_name=tex_name, preset_name=args.preset)
    print(json.dumps({"status": "OK", "info": info}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())