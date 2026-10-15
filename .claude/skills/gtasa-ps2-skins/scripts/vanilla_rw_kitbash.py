#!/usr/bin/env python3
"""
vanilla_rw_kitbash.py — Real vanilla asset extractor and surgical head-swap engine for GTA: SA peds.

Unlike `build_ps2_rig_bpy.py` (which synthesizes a low-poly proxy body), this engine performs the
surgery described in `AGENTS.md` §6 on the *authentic* Rockstar North meshes and textures:

1. Reads the GTA:SA `.img` archive (IMG V2) and extracts the donor `.dff`/`.txd` and body `.dff`/`.txd`.
2. Parses the RenderWare 3.6.0.3 streams (`Clump`, `FrameList` + `HAnim PLG 0x011E`, `Geometry`,
   `Bin Mesh PLG 0x050E`, `Skin PLG 0x0116`, `TextureNative 0x0015`).
3. Grafts the donor skull at the removed skull's original crown height. Preserves the body's
   cervical transition triangles, original neck weights and donor head weights; fits neck
   endpoints under the donor surface and removes LSV2's old bandana accessory.
4. Splices the two vanilla texture atlases into a single PS2-style atlas (donor head region +
   body garment region) and repacks the UVs of both halves.
5. Writes a game-loadable `.dff` (33 Frames / 32 HAnim bones, geometry flags `0x00010036`) and a
   D3D9 `.txd` whose pixels are PS2-quantized (256 colors, dynamic range `[12, 235]`).

RenderWare layout ground truth (verified byte-exactly against `lsv2.dff` / `sindaco.dff` from
`models/gta3.img`):
    Geometry struct = u32 flags, u32 numTriangles, u32 numVertices, u32 numMorphTargets,
                      then TexCoords (1 set), Triangles, MorphTarget (sphere + 2 x u32),
                      Vertices, Normals.
    Vertex bone indices reference the HAnim node table of the root frame (0..31), whose bone ids are
    [0, 1, 2, 3, 4, 5, 8, 6, 7, 31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 302, 301, 201,
     41, 42, 43, 44, 51, 52, 53, 54].

CLI usage:
    python3 scripts/vanilla_rw_kitbash.py --game-dir "C:/path/to/GTASA" \
        --head-model sindaco --body-model lsv2 --skin-name sindaco_lsv2 \
        --outdir ./output/sindaco_lsv2
"""

import argparse
import json
import math
import os
import struct
import sys
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image

# Allow running both as a repo script and from inside a skill bundle mirror.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quantize_ps2_txd import apply_ps2_color_pipeline  # noqa: E402
from match_skin_tone import load_profile, match_body_skin, palette_for_skin_edit  # noqa: E402

RW_VERSION_GTASA = 0x1803FFFF
IMG_SECTOR = 2048

# Geometry flags used by every vanilla GTA:SA ped (`rpGEOMETRYNORMALS | rpGEOMETRYTEXTURED | ...`).
PED_GEOMETRY_FLAGS = 0x00010036
# Vanilla ped material / texture filter blocks (byte-exact copies of `lsv2.dff`).
PED_MATLIST_STRUCT = struct.pack('<Ii', 1, -1)  # one new material, not a reused slot
PED_MATERIAL_STRUCT = bytes.fromhex("00000000 ffffffff 04000000 01000000 0000803f 00000000 0000803f")
PED_TEXTURE_STRUCT = bytes.fromhex("06110100")
PED_EMPTY_MASK_NAME = b"\x00\x00\x00\x00"
PED_CLUMP_STRUCT = struct.pack('<III', 1, 0, 0)  # one Atomic, no lights or cameras
PED_ATOMIC_STRUCT = bytes.fromhex("02000000 00000000 05000000 00000000")
PED_RIGHT_TO_RENDER = bytes.fromhex("16010000 01000000")
PED_PLUGIN_EXTRA = bytes.fromhex("00000000")

# Bone ids of the head chain (`Head`, `Jaw`, both `Brow`s) used to section the two meshes.
HEAD_CHAIN_BONE_IDS = {5, 6, 7, 8}
NECK_BONE_ID = 4

# Vanilla node table (node index -> bone id) shared by every GTA:SA pedestrian.
VANILLA_NODE_BONE_IDS: List[int] = [
    0, 1, 2, 3, 4, 5, 8, 6, 7, 31, 32, 33, 34, 35, 36,
    21, 22, 23, 24, 25, 26, 302, 301, 201, 41, 42, 43, 44, 51, 52, 53, 54,
]


# ==============================================================================
# 1. IMG V2 ARCHIVE READER + RENDERWARE STREAM PARSER
# ==============================================================================
def _chunks(buf: bytes, offset: int = 0, end: Optional[int] = None) -> List[Tuple[int, int, int, int, int, int]]:
    """Walk RenderWare chunks: returns `(type, size, version, start, payload_start, payload_end)`."""
    if end is None:
        end = len(buf)
    out: List[Tuple[int, int, int, int, int, int]] = []
    pos = offset
    while pos + 12 <= end:
        c_type, c_size, _ = struct.unpack_from("<III", buf, pos)
        payload_start = pos + 12
        payload_end = payload_start + c_size
        if payload_end > end:
            break
        out.append((c_type, c_size, struct.unpack_from("<I", buf, pos + 8)[0], pos, payload_start, payload_end))
        pos = payload_end
    return out


def open_img_archive(img_path: str) -> Tuple[object, Dict[str, Tuple[int, int]]]:
    """Open a GTA:SA `.img` (IMG V2) archive and return its file table `{name: (offset, size)}` in sectors."""
    handle = open(img_path, "rb")
    magic = handle.read(4)
    if magic != b"VER2":
        raise ValueError(f"{img_path} is not an IMG V2 archive (magic={magic!r})")
    count = struct.unpack("<I", handle.read(4))[0]
    table: Dict[str, Tuple[int, int]] = {}
    for _ in range(count):
        offset, size, _ = struct.unpack("<IHH", handle.read(8))
        name = handle.read(24).split(b"\x00")[0].decode("ascii", "replace").lower()
        table[name] = (offset, size)
    return handle, table


def extract_img_entry(handle, table: Dict[str, Tuple[int, int]], name: str) -> bytes:
    """Read one file out of the open `.img` archive."""
    key = name.lower()
    if key not in table:
        raise KeyError(f"{name} not found in the .img archive")
    offset, size = table[key]
    handle.seek(offset * IMG_SECTOR)
    return handle.read(size * IMG_SECTOR)


def parse_ped_dff(data: bytes) -> Dict[str, object]:
    """Parse a GTA:SA pedestrian `.dff` into geometry, skeleton, and skinning arrays."""
    root = _chunks(data)[0]
    if root[0] != 0x0010:
        raise ValueError("not a RenderWare Clump stream")
    kids = _chunks(data, root[4], root[5])

    # ---- FrameList (frames + HAnim node table) --------------------------------
    frame_list = next(c for c in kids if c[0] == 0x000E)
    frame_struct = next(c for c in _chunks(data, frame_list[4], frame_list[5]) if c[0] == 0x0001)
    frame_count = struct.unpack_from("<I", data, frame_struct[4])[0]
    frames: List[Dict[str, object]] = []
    pos = frame_struct[4] + 4
    for i in range(frame_count):
        rot = np.frombuffer(data, dtype="<f4", count=9, offset=pos).reshape(3, 3).astype(np.float64)
        tpos = np.frombuffer(data, dtype="<f4", count=3, offset=pos + 36).astype(np.float64)
        parent, flags = struct.unpack_from("<iI", data, pos + 48)
        frames.append({"index": i, "rot": rot, "pos": tpos, "parent": parent, "flags": flags,
                       "name": None, "bone_id": None})
        pos += 56
    extensions = [c for c in _chunks(data, frame_list[4], frame_list[5]) if c[0] == 0x0003]
    for i, ext in enumerate(extensions):
        if i >= frame_count:
            break
        for sub in _chunks(data, ext[4], ext[5]):
            if sub[0] == 0x011E:
                _, bone_id, node_count = struct.unpack_from("<III", data, sub[4])
                frames[i]["bone_id"] = bone_id
                if node_count > 1:
                    node_table = [
                        struct.unpack_from("<III", data, sub[4] + 20 + k * 12) for k in range(node_count)
                    ]
                    frames[i]["node_table"] = node_table
            elif sub[0] == 0x0253F2FE:
                frames[i]["name"] = data[sub[4]:sub[5]].split(b"\x00")[0].decode("ascii", "replace")

    root_frame = next((f for f in frames if f.get("node_table")), None)
    if root_frame is None:
        raise ValueError("FrameList carries no HAnim PLG node table")
    node_bone_ids = [entry[0] for entry in root_frame["node_table"]]

    # ---- Geometry -------------------------------------------------------------
    geom_list = next(c for c in kids if c[0] == 0x001A)
    geometry = next(c for c in _chunks(data, geom_list[4], geom_list[5]) if c[0] == 0x000F)
    geom_kids = _chunks(data, geometry[4], geometry[5])
    g_struct = next(c for c in geom_kids if c[0] == 0x0001)
    payload = data[g_struct[4]:g_struct[5]]
    flags, num_tris, num_verts, num_morph = struct.unpack_from("<IIII", payload, 0)
    uvs = np.frombuffer(payload, dtype="<f4", count=num_verts * 2, offset=16).reshape(-1, 2).astype(np.float64)
    tri_offset = 16 + num_verts * 8
    raw_tris = np.frombuffer(payload, dtype="<u2", count=num_tris * 4, offset=tri_offset).reshape(-1, 4)
    tri_offset += num_tris * 8
    vertex_offset = tri_offset + 24
    verts = np.frombuffer(payload, dtype="<f4", count=num_verts * 3, offset=vertex_offset).reshape(-1, 3).astype(np.float64)
    normals = np.frombuffer(
        payload, dtype="<f4", count=num_verts * 3, offset=vertex_offset + num_verts * 12
    ).reshape(-1, 3).astype(np.float64)

    # ---- Material / texture name ---------------------------------------------
    mat_list = next(c for c in geom_kids if c[0] == 0x0008)
    texture_name = None
    for mat in _chunks(data, mat_list[4], mat_list[5]):
        if mat[0] != 0x0007:
            continue
        for sub in _chunks(data, mat[4], mat[5]):
            if sub[0] == 0x0006:
                strings = [c for c in _chunks(data, sub[4], sub[5]) if c[0] == 0x0002]
                if strings:
                    texture_name = data[strings[0][4]:strings[0][5]].split(b"\x00")[0].decode("ascii", "replace")

    # ---- Skin PLG -------------------------------------------------------------
    geom_ext = next((c for c in geom_kids if c[0] == 0x0003), None)
    skin = next((c for c in _chunks(data, geom_ext[4], geom_ext[5]) if c[0] == 0x0116), None) if geom_ext else None
    if skin is None:
        raise ValueError("pedestrian .dff carries no Skin PLG (0x0116)")
    sp = data[skin[4]:skin[5]]
    skin_bones, used_count, max_weights, _ = struct.unpack_from("<BBBB", sp, 0)
    index_offset = 4 + used_count
    weight_offset = index_offset + num_verts * 4
    bone_indices = np.frombuffer(sp, dtype=np.uint8, count=num_verts * 4, offset=index_offset).reshape(-1, 4)
    bone_weights = np.frombuffer(sp, dtype="<f4", count=num_verts * 4, offset=weight_offset).reshape(-1, 4)
    matrix_offset = weight_offset + num_verts * 16
    inv_matrices = np.frombuffer(sp, dtype="<f4", count=skin_bones * 16, offset=matrix_offset).reshape(skin_bones, 4, 4)

    return {
        "frames": frames,
        "node_bone_ids": node_bone_ids,
        "geometry_flags": flags,
        "num_morph_targets": num_morph,
        # Raw triangles keep the vanilla `(vertex2, vertex1, materialId, vertex3)` packing.
        "triangles": raw_tris,
        "vertices": verts,
        "normals": normals,
        "uvs": uvs,
        "bone_indices": bone_indices,
        "bone_weights": bone_weights,
        "inv_matrices": inv_matrices,
        "texture_name": texture_name,
        "frame_list_bytes": data[frame_list[3]:frame_list[5]] + b"",
    }


# ==============================================================================
# 2. TEXTURENATIVE (D3D9) READER
# ==============================================================================
def read_txd_textures(data: bytes) -> List[Tuple[str, np.ndarray]]:
    """Decode every `TextureNative (0x0015)` of a `.txd` into `(name, RGB uint8 array)`."""
    root = _chunks(data)[0]
    if root[0] != 0x0016:
        raise ValueError("not a RenderWare TextureDictionary stream")
    textures: List[Tuple[str, np.ndarray]] = []
    for native in _chunks(data, root[4], root[5]):
        if native[0] != 0x0015:
            continue
        struct_chunk = next(c for c in _chunks(data, native[4], native[5]) if c[0] == 0x0001)
        p = data[struct_chunk[4]:struct_chunk[5]]
        name = p[8:40].split(b"\x00")[0].decode("ascii", "replace")
        raster_format, _d3d_format = struct.unpack_from("<II", p, 72)
        width, height = struct.unpack_from("<HH", p, 80)
        offset = 88
        if raster_format & 0x2000:  # rwRASTERFORMATPAL8
            palette = np.frombuffer(p, dtype=np.uint8, count=1024, offset=offset).reshape(256, 4)[:, :3]
            offset += 1024
            size = struct.unpack_from("<I", p, offset)[0]
            indices = np.frombuffer(p, dtype=np.uint8, count=width * height, offset=offset + 4).reshape(height, width)
            textures.append((name, palette[indices]))
        else:
            size = struct.unpack_from("<I", p, offset)[0]
            bgra = np.frombuffer(p, dtype=np.uint8, count=width * height * 4, offset=offset + 4).reshape(height, width, 4)
            textures.append((name, bgra[:, :, [2, 1, 0]].copy()))
    return textures


def build_txd_8888(tex_name: str, rgb: np.ndarray) -> bytes:
    """
    Pack a D3D9 `.txd` for GTA:SA PC using the exact header of the vanilla ped textures
    (`rasterFormat 0x600`, `d3dFormat 22`, 32 bpp, `filterFlags 0x1101`).
    """
    clean_name = os.path.splitext(os.path.basename(tex_name))[0].lower()[:31]
    height, width = rgb.shape[:2]
    name_32 = clean_name.encode("ascii").ljust(32, b"\x00")
    header = struct.pack(
        "<II32s32sIIHHBBBB",
        9,              # platform_id = 9 (Direct3D 9, GTA:SA PC)
        0x00001101,     # FILTERLINEAR + WRAP (vanilla ped value)
        name_32,
        b"\x00" * 32,
        0x00000600,     # rwRASTERFORMATALPHA8888
        22,             # D3DFMT_X8R8G8B8
        width,
        height,
        32,             # depth
        1,              # mip levels
        4,              # raster type
        0,              # compression / alpha flags
    )
    bgra = np.zeros((height, width, 4), dtype=np.uint8)
    bgra[:, :, :3] = np.ascontiguousarray(rgb.astype(np.uint8)[:, :, [2, 1, 0]])
    bgra[:, :, 3] = 255
    body = struct.pack("<I", bgra.nbytes) + bgra.tobytes()
    native_struct = _rw_chunk(0x0001, header + body)
    native_chunk = _rw_chunk(0x0015, native_struct + _rw_chunk(0x0003, b""))
    txd_struct = _rw_chunk(0x0001, struct.pack("<HH", 1, 2))
    return _rw_chunk(0x0016, txd_struct + native_chunk + _rw_chunk(0x0003, b""))


def _rw_chunk(chunk_type: int, payload: bytes, version: int = RW_VERSION_GTASA) -> bytes:
    """Build a RenderWare binary chunk: 12-byte header plus payload."""
    return struct.pack("<III", chunk_type, len(payload), version) + payload


# ==============================================================================
# 3. HEAD-SWAP SURGERY
# ==============================================================================
def _head_chain_mask(ped: Dict[str, object]) -> np.ndarray:
    """Per-vertex total weight on the head chain (`Head`, `Jaw`, both `Brow` bones)."""
    node_bone_ids = np.array(ped["node_bone_ids"], dtype=np.int64)
    head_nodes = np.array([i for i, bid in enumerate(node_bone_ids) if bid in HEAD_CHAIN_BONE_IDS])
    indices = np.asarray(ped["bone_indices"], dtype=np.int64)
    weights = np.asarray(ped["bone_weights"], dtype=np.float64)
    mask = np.zeros(indices.shape[0], dtype=np.float64)
    for node in head_nodes:
        hit = indices == node
        mask += (weights * hit).sum(axis=1)
    return mask


def _solid_half(ped: Dict[str, object], keep: np.ndarray, keep_mixed: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compact a cut; retain mixed neck/head triangles on the body when requested."""
    tri = np.asarray(ped["triangles"])[:, [1, 0, 3]]
    selection = keep[tri].any(axis=1) if keep_mixed else keep[tri].all(axis=1)
    kept = tri[selection]
    if len(kept) == 0:
        raise RuntimeError("head-swap cut removed every triangle from one half")
    used = np.zeros(len(keep), dtype=bool)
    used[kept.ravel()] = True
    remap = np.full(len(keep), -1, dtype=np.int64)
    remap[used] = np.arange(int(used.sum()))
    return (
        np.asarray(ped["vertices"])[used],
        np.asarray(ped["uvs"])[used],
        np.asarray(ped["bone_indices"])[used],
        np.asarray(ped["bone_weights"])[used],
        remap[kept],
    )


def graft_head(
    body: Dict[str, object],
    donor: Dict[str, object],
    head_weight_threshold: float = 0.5,
) -> Dict[str, object]:
    """
    Replace the skull while preserving the body's complete animated neck.

    Mixed neck/head triangles belong to the cervical transition and must survive
    the body cut. Fit the donor to the removed skull bounds, preserving crown
    height and head-chain weights. Never align the chin to the shirt collar.
    """
    body_keep = _head_chain_mask(body) < head_weight_threshold
    donor_keep = _head_chain_mask(donor) >= head_weight_threshold

    b_verts, b_uvs, b_idx, b_wgt, b_tris = _solid_half(body, body_keep, keep_mixed=True)
    d_verts, d_uvs, d_idx, d_wgt, d_tris = _solid_half(donor, donor_keep)

    # Scale against the head that was just cut off, so the new head fills the same collar.
    removed = np.asarray(body["vertices"])[~body_keep]
    donor_span = d_verts.max(axis=0) - d_verts.min(axis=0)
    removed_span = removed.max(axis=0) - removed.min(axis=0)
    scale = float(np.clip(
        ((removed_span[1] / max(donor_span[1], 1e-6)) + (removed_span[2] / max(donor_span[2], 1e-6))) * 0.5,
        0.90,
        1.20,
    ))

    anchor = (d_verts.min(axis=0) + d_verts.max(axis=0)) * 0.5
    target = (removed.min(axis=0) + removed.max(axis=0)) * 0.5
    anchor[0] = d_verts[:, 0].max()
    target[0] = removed[:, 0].max()
    d_verts = target + scale * (d_verts - anchor)

    # Retained neck triangles end on the old skull (including its bandana UVs).
    # Tuck only those endpoints under the donor surface, keeping the lower neck
    # and its original weights intact. This prevents old-head scraps protruding.
    neck_end = _head_chain_mask({'node_bone_ids': body['node_bone_ids'],
                                'bone_indices': b_idx, 'bone_weights': b_wgt}) >= head_weight_threshold
    faces = d_verts[d_tris]
    a, b, c = faces[:, 0], faces[:, 1], faces[:, 2]
    ab, ac = b-a, c-a
    aa, bb, cc = (ab*ab).sum(1), (ab*ac).sum(1), (ac*ac).sum(1)
    den = np.maximum(aa*cc-bb*bb, 1e-15)
    for index in np.flatnonzero(neck_end):
        point = b_verts[index]
        ap = point-a
        u = (cc*(ap*ab).sum(1)-bb*(ap*ac).sum(1))/den
        v = (aa*(ap*ac).sum(1)-bb*(ap*ab).sum(1))/den
        plane = a + u[:, None]*ab + v[:, None]*ac
        valid = (u >= 0) & (v >= 0) & (u+v <= 1)
        candidates = [plane[valid]]
        for start, end in ((a, b), (b, c), (c, a)):
            edge = end-start
            t = np.clip(((point-start)*edge).sum(1)/np.maximum((edge*edge).sum(1), 1e-15), 0, 1)
            candidates.append(start+t[:, None]*edge)
        candidates = np.vstack(candidates)
        nearest = candidates[np.argmin(((candidates-point)**2).sum(1))]
        inward = d_verts.mean(0)-nearest
        b_verts[index] = nearest + inward/max(np.linalg.norm(inward), 1e-9)*.004

    vertices = np.vstack([b_verts, d_verts])
    uvs = np.vstack([b_uvs, d_uvs])
    bone_indices = np.vstack([b_idx, d_idx])
    bone_weights = np.vstack([b_wgt, d_wgt])
    triangles = np.vstack([b_tris, d_tris + len(b_verts)])

    p0 = vertices[triangles[:, 0]]
    p1 = vertices[triangles[:, 1]]
    p2 = vertices[triangles[:, 2]]
    area2 = np.linalg.norm(np.cross(p1 - p0, p2 - p0), axis=1)
    degenerate_faces = int((area2 < 1e-12).sum())
    triangles = triangles[area2 >= 1e-12]

    is_donor = np.concatenate([np.zeros(len(b_verts), dtype=bool), np.ones(len(d_verts), dtype=bool)])
    referenced = np.zeros(len(vertices), dtype=bool)
    referenced[triangles.ravel()] = True
    orphans = int((~referenced).sum())
    if orphans:
        compact = np.full(len(vertices), -1, dtype=np.int64)
        compact[referenced] = np.arange(int(referenced.sum()))
        vertices = vertices[referenced]
        uvs = uvs[referenced]
        bone_indices = bone_indices[referenced]
        bone_weights = bone_weights[referenced]
        is_donor = is_donor[referenced]
        triangles = compact[triangles]

    normals = _smooth_normals(vertices, triangles)
    return {
        "vertices": vertices,
        "normals": normals,
        "uvs": uvs,
        "triangles": triangles,
        "bone_indices": bone_indices.astype(np.uint8),
        "bone_weights": bone_weights.astype(np.float32),
        "is_donor": is_donor,
        "stats": {
            "body_vertices_in": len(body["vertices"]),
            "donor_vertices_in": len(donor["vertices"]),
            "body_vertices_kept": int(len(b_verts)),
            "donor_head_vertices": int(len(d_verts)),
            "body_triangles_kept": int(len(b_tris)),
            "donor_head_triangles": int(len(d_tris)),
            "neck_boundary_triangles_preserved": int((body_keep[np.asarray(body['triangles'])[:, [1, 0, 3]]].any(1) & ~body_keep[np.asarray(body['triangles'])[:, [1, 0, 3]]].all(1)).sum()),
            "head_weights_rewritten": 0,
            "neck_endpoints_fitted": int(neck_end.sum()),
            "degenerate_faces_dropped": degenerate_faces,
            "orphan_vertices_dropped": orphans,
            "vertices_out": int(len(vertices)),
            "triangles_out": int(len(triangles)),
            "head_scale": round(float(scale), 5),
            "crown_target": [round(float(x), 4) for x in target],
        },
    }


def _normalize(v: np.ndarray) -> np.ndarray:
    length = np.linalg.norm(v, axis=1, keepdims=True)
    length[length < 1e-9] = 1.0
    return v / length


def _normalize_rows(v: np.ndarray) -> np.ndarray:
    total = v.sum(axis=1, keepdims=True)
    total[total < 1e-6] = 1.0
    return v / total


def _smooth_normals(vertices: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    """Area-weighted smooth normals for every vertex of the merged mesh."""
    normals = np.zeros_like(vertices)
    tri_verts = np.asarray(triangles, dtype=np.int64)
    p0 = vertices[tri_verts[:, 0]]
    p1 = vertices[tri_verts[:, 1]]
    p2 = vertices[tri_verts[:, 2]]
    face_normals = np.cross(p1 - p0, p2 - p0)
    for corner in range(3):
        np.add.at(normals, tri_verts[:, corner], face_normals)
    return _normalize(normals)


# ==============================================================================
# 4. ATLAS SPLICE (DONOR HEAD REGION + BODY GARMENT REGION)
# ==============================================================================
def splice_atlas(
    donor_rgb: np.ndarray,
    body_rgb: np.ndarray,
    atlas_size: Tuple[int, int] = (512, 256),
) -> Tuple[Image.Image, Dict[str, Tuple[float, float]]]:
    """
    Compose one PS2-style atlas: the donor texture keeps its native resolution on the left,
    the body texture sits on the right. Returns the atlas and the UV half mapping.
    """
    width, height = atlas_size
    atlas = Image.new("RGB", (width, height), (32, 32, 36))
    atlas.paste(Image.fromarray(donor_rgb), (0, 0))
    atlas.paste(Image.fromarray(body_rgb), (donor_rgb.shape[1], 0))
    mapping = {
        "donor": (0.0, donor_rgb.shape[1] / float(width)),
        "body": (donor_rgb.shape[1] / float(width), (donor_rgb.shape[1] + body_rgb.shape[1]) / float(width)),
    }
    return atlas, mapping


def remap_uvs(uvs: np.ndarray, u_range: Tuple[float, float]) -> np.ndarray:
    """Rescale the U axis of a UV set into `[u_range[0], u_range[1]]` (V is untouched)."""
    out = uvs.copy()
    out[:, 0] = u_range[0] + uvs[:, 0] * (u_range[1] - u_range[0])
    return out


# ==============================================================================
# 5. RENDERWARE WRITER (GTA:SA PC, 0x1803FFFF)
# ==============================================================================
def write_kitbash_dff(
    output_path: str,
    frame_list_chunk: bytes,
    merged: Dict[str, object],
    inv_matrices: np.ndarray,
    texture_name: str,
    geometry_flags: int = PED_GEOMETRY_FLAGS,
) -> Dict[str, object]:
    """Serialize the merged ped into a game-loadable GTA:SA `.dff`."""
    clean_tex = os.path.splitext(os.path.basename(texture_name))[0].lower()[:31]
    verts = np.asarray(merged["vertices"], dtype=np.float64)
    normals = np.asarray(merged["normals"], dtype=np.float64)
    uvs = np.asarray(merged["uvs"], dtype=np.float64)
    triangles = np.asarray(merged["triangles"], dtype=np.int64)
    bone_indices = np.asarray(merged["bone_indices"], dtype=np.uint8)
    bone_weights = np.asarray(merged["bone_weights"], dtype=np.float32)
    num_verts, num_tris = len(verts), len(triangles)

    # ---- Geometry struct (16-byte header) + UVs + triangles + morph + verts ----
    center = (verts.min(axis=0) + verts.max(axis=0)) * 0.5
    radius = float(np.linalg.norm(verts - center, axis=1).max())
    geom_struct = struct.pack("<IIII", geometry_flags, num_tris, num_verts, 1)
    geom_struct += np.ascontiguousarray(uvs.astype("<f4")).tobytes()
    # RW geometry struct packs triangles as (vert2, vert1, materialId, vert3),
    # while `triangles` here is already in render order (vert1, vert2, vert3).
    geom_tris = np.column_stack([
        triangles[:, 1], triangles[:, 0],
        np.zeros(num_tris, dtype=np.int64),
        triangles[:, 2],
    ])
    geom_struct += np.ascontiguousarray(geom_tris.astype("<u2")).tobytes()
    geom_struct += struct.pack("<4fII", *(center.tolist()), radius, 1, 1)
    geom_struct += np.ascontiguousarray(verts.astype("<f4")).tobytes()
    geom_struct += np.ascontiguousarray(normals.astype("<f4")).tobytes()

    # ---- Material list with the spliced atlas texture name --------------------
    tex_name_bytes = clean_tex.encode("ascii") + b"\x00"
    if len(tex_name_bytes) % 4:
        tex_name_bytes += b"\x00" * (4 - len(tex_name_bytes) % 4)
    tex_chunk = _rw_chunk(
        0x0006,
        _rw_chunk(0x0001, PED_TEXTURE_STRUCT)
        + _rw_chunk(0x0002, tex_name_bytes)
        + _rw_chunk(0x0002, PED_EMPTY_MASK_NAME)
        + _rw_chunk(0x0003, b""),
    )
    material = _rw_chunk(0x0007, _rw_chunk(0x0001, PED_MATERIAL_STRUCT) + tex_chunk + _rw_chunk(0x0003, b""))
    matlist = _rw_chunk(0x0008, _rw_chunk(0x0001, PED_MATLIST_STRUCT) + material)

    # ---- Skin PLG (0x0116): 32 bones, <= 4 influences, sanitized weights ------
    used_nodes = sorted({int(n) for n in np.unique(bone_indices) if n > 0})
    skin_header = struct.pack("<BBBB", len(inv_matrices), len(used_nodes), 4, 0)
    skin_payload = skin_header + bytes(used_nodes)
    skin_payload += np.ascontiguousarray(bone_indices).tobytes()
    skin_payload += np.ascontiguousarray(bone_weights).tobytes()
    skin_payload += np.ascontiguousarray(inv_matrices.astype("<f4")).tobytes()
    skin_payload += struct.pack("<III", 0, 0, 0)
    skin_chunk = _rw_chunk(0x0116, skin_payload)

    # ---- Bin Mesh PLG (0x050E): single mesh, u32 triangle indices -------------
    bin_mesh = struct.pack("<IIIII", 0, 1, num_tris * 3, num_tris * 3, 0)
    bin_mesh += np.ascontiguousarray(triangles.astype("<u4")).tobytes()
    bin_mesh_chunk = _rw_chunk(0x050E, bin_mesh)

    geom_extension = _rw_chunk(0x0003, bin_mesh_chunk + skin_chunk + _rw_chunk(0x253F2FD, PED_PLUGIN_EXTRA))
    geometry = _rw_chunk(0x000F, _rw_chunk(0x0001, geom_struct) + matlist + geom_extension)
    geom_list = _rw_chunk(0x001A, _rw_chunk(0x0001, struct.pack("<I", 1)) + geometry)
    atomic = _rw_chunk(0x0014, _rw_chunk(0x0001, PED_ATOMIC_STRUCT) + _rw_chunk(0x0003, _rw_chunk(0x001F, PED_RIGHT_TO_RENDER)))
    clump = _rw_chunk(0x0010, _rw_chunk(0x0001, PED_CLUMP_STRUCT) + frame_list_chunk + geom_list + atomic + _rw_chunk(0x0003, b""))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as handle:
        handle.write(clump)
    return {
        "dff_path": output_path,
        "rw_version": hex(RW_VERSION_GTASA),
        "geometry_flags": hex(geometry_flags),
        "vertex_count": num_verts,
        "triangle_count": num_tris,
        "texture_name": clean_tex,
    }


# ==============================================================================
# 6. PIPELINE ORCHESTRATION
# ==============================================================================
def build_kitbash_skin(
    game_dir: str,
    outdir: str,
    skin_name: str,
    head_model: str = "sindaco",
    body_model: str = "lsv2",
    tex_name: Optional[str] = None,
    atlas_size: Tuple[int, int] = (512, 256),
    match_body_skin_to_head: bool = False,
) -> Dict[str, object]:
    """Extract, splice, and compile a head-swap skin straight from a GTA:SA installation."""
    tex_name = (tex_name or skin_name).lower()
    os.makedirs(outdir, exist_ok=True)

    img_path = os.path.join(game_dir, "models", "gta3.img")
    handle, table = open_img_archive(img_path)
    try:
        head_dff = parse_ped_dff(extract_img_entry(handle, table, f"{head_model}.dff"))
        head_txd = read_txd_textures(extract_img_entry(handle, table, f"{head_model}.txd"))[0][1]
        body_dff = parse_ped_dff(extract_img_entry(handle, table, f"{body_model}.dff"))
        body_txd = read_txd_textures(extract_img_entry(handle, table, f"{body_model}.txd"))[0][1]
    finally:
        handle.close()

    # LSV2 has a yellow bandana tail crossing the head/neck cut. It is a head
    # accessory, not part of the cervical surface. Identify its vanilla yellow
    # UV island only in the upper nape; skin/clothing elsewhere stay untouched.
    accessory_faces_removed = 0
    if body_model.lower() == 'lsv2':
        raw = np.asarray(body_dff['triangles'])
        faces = raw[:, [1, 0, 3]]
        uv = np.asarray(body_dff['uvs'])[faces].mean(1)
        color = body_txd[np.clip((uv[:, 1]*body_txd.shape[0]).astype(int), 0, body_txd.shape[0]-1),
                         np.clip((uv[:, 0]*body_txd.shape[1]).astype(int), 0, body_txd.shape[1]-1)].astype(int)
        center = np.asarray(body_dff['vertices'])[faces].mean(1)
        accessory = ((color[:, 0]-color[:, 2] > 80) & (color[:, 1]-color[:, 2] > 50)
                     & (center[:, 0] > .6) & (center[:, 1] < -.06))
        accessory_faces_removed = int(accessory.sum())
        body_dff['triangles'] = raw[~accessory]
    merged = graft_head(body_dff, head_dff)
    merged['stats']['body_head_accessory_faces_removed'] = accessory_faces_removed

    tone_audit = {'enabled': False}
    if match_body_skin_to_head:
        original_atlas = splice_atlas(head_txd, body_txd, atlas_size=atlas_size)[0]
        body_txd, tone_mask, tone_audit = match_body_skin(body_txd, head_txd, load_profile(head_model, body_model))
        tone_audit['enabled'] = True
        Image.fromarray((tone_mask*255).astype(np.uint8)).save(os.path.join(outdir, f'{skin_name}_body_skin_mask.png'))

    atlas_rgb, uv_mapping = splice_atlas(head_txd, body_txd, atlas_size=atlas_size)
    donor_mask = np.asarray(merged["is_donor"])
    merged_uvs = np.asarray(merged["uvs"]).copy()
    merged_uvs[donor_mask] = remap_uvs(merged_uvs[donor_mask], uv_mapping["donor"])
    merged_uvs[~donor_mask] = remap_uvs(merged_uvs[~donor_mask], uv_mapping["body"])
    merged["uvs"] = merged_uvs

    # PS2 dynamic range `[12, 235]` + 256-color median cut (Floyd-Steinberg dithered).
    if match_body_skin_to_head:
        _, baseline_rgba = apply_ps2_color_pipeline(original_atlas, target_size=atlas_size, colors=256)
        atlas_mask = np.zeros((atlas_size[1], atlas_size[0]), dtype=bool)
        body_x = head_txd.shape[1]
        atlas_mask[:body_txd.shape[0], body_x:body_x+body_txd.shape[1]] = tone_mask
        skin_palette = palette_for_skin_edit(baseline_rgba, atlas_rgb, atlas_mask)
        _pal, rgba = apply_ps2_color_pipeline(atlas_rgb, target_size=atlas_size, colors=256, palette=skin_palette)
        # Reserve exact head/clothing colors and restore protected pixels after
        # quantization, so recoloring cannot move those colors or diffuse noise.
        locked = np.array(rgba)
        baseline = np.array(baseline_rgba)
        locked[~atlas_mask] = baseline[~atlas_mask]
        rgba = Image.fromarray(locked)
        tone_audit['final_atlas_head_pixels_changed'] = int(np.any(locked[:, :body_x] != baseline[:, :body_x], axis=2).sum())
        tone_audit['final_atlas_non_skin_pixels_changed'] = int(np.any(locked[~atlas_mask] != baseline[~atlas_mask], axis=1).sum())
        tone_audit['final_atlas_unique_colors'] = int(len(np.unique(locked[:, :, :3].reshape(-1, 3), axis=0)))
        with open(os.path.join(outdir, f'{skin_name}_tone_report.json'), 'w', encoding='utf-8') as report_file:
            json.dump(tone_audit, report_file, indent=2)
    else:
        _pal, rgba = apply_ps2_color_pipeline(atlas_rgb, target_size=atlas_size, colors=256)
    atlas_path = os.path.join(outdir, f"{skin_name}_atlas.png")
    Image.fromarray(np.asarray(rgba)[:, :, :3]).save(atlas_path, format="PNG")

    dff_path = os.path.join(outdir, f"{skin_name}.dff")
    txd_path = os.path.join(outdir, f"{skin_name}.txd")
    dff_info = write_kitbash_dff(dff_path, body_dff["frame_list_bytes"], merged, body_dff["inv_matrices"], tex_name)
    txd_bytes = build_txd_8888(tex_name, np.asarray(rgba)[:, :, :3])
    with open(txd_path, "wb") as handle:
        handle.write(txd_bytes)

    return {
        "status": "OK",
        "skin_name": skin_name,
        "head_donor": {"model": head_model, "vanilla_texture": head_dff["texture_name"]},
        "body_base": {"model": body_model, "vanilla_texture": body_dff["texture_name"]},
        "surgery": merged["stats"],
        "dff": dff_info,
        "txd": {
            "txd_path": txd_path,
            "texture_name": tex_name,
            "dimensions": f"{atlas_size[0]}x{atlas_size[1]}",
            "raster_format": "D3D9 8888 (vanilla ped format) with a PS2 256-color palette baked in",
        },
        "atlas_png": atlas_path,
        "skin_tone": tone_audit,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Real vanilla .dff/.txd head-swap kitbasher for GTA:SA pedestrians (open.mp / SA-MP)"
    )
    parser.add_argument("--game-dir", required=True, help="GTA:San Andreas installation directory")
    parser.add_argument("--head-model", default="sindaco", help="Donor head model inside models/gta3.img")
    parser.add_argument("--body-model", default="lsv2", help="Body model inside models/gta3.img")
    parser.add_argument("--skin-name", default="sindaco_lsv2", help="Output file identifier")
    parser.add_argument("--tex-name", default=None, help="Internal texture name (defaults to --skin-name)")
    parser.add_argument("--outdir", default=None, help="Output folder (defaults to ./output/<skin-name>)")
    parser.add_argument("--atlas-width", type=int, default=512, help="Spliced atlas width (power of two)")
    parser.add_argument("--atlas-height", type=int, default=256, help="Spliced atlas height (power of two)")
    parser.add_argument("--match-body-skin-to-head", action="store_true", help="Match body skin to head using an inspected UV profile")
    args = parser.parse_args()

    outdir = args.outdir or os.path.join(".", "output", args.skin_name)
    result = build_kitbash_skin(
        game_dir=args.game_dir,
        outdir=outdir,
        skin_name=args.skin_name,
        head_model=args.head_model,
        body_model=args.body_model,
        tex_name=args.tex_name,
        atlas_size=(args.atlas_width, args.atlas_height),
        match_body_skin_to_head=args.match_body_skin_to_head,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
