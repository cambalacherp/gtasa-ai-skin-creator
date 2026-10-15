#!/usr/bin/env python3
"""Render the actual DFF/TXD in five orthographic views, including a skinned pose.

No Blender dependency. Mesh coordinates are X=up, Y=front, Z=left. Pose Test
uses the exported Skin PLG weights, inverse bind matrices and HAnim hierarchy;
it is a deformation diagnostic, not a captured GTA animation.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from vanilla_rw_kitbash import parse_ped_dff, read_txd_textures


def posed_vertices(mesh):
    """Apply hierarchical bone rotations around pivots from inverse bind matrices."""
    ids = mesh['node_bone_ids']
    # RenderWare stores a 4x3 affine matrix with padding in the fourth column.
    bind = mesh['inv_matrices'].astype(float).copy()
    bind[:, :, 3] = [0, 0, 0, 1]
    pivots = np.linalg.inv(bind)[:, 3, :3]
    by_id = {f['bone_id']: f for f in mesh['frames'] if f['bone_id'] is not None}
    rotations = {5: (0, 25), 32: (1, 24), 22: (1, -24), 33: (1, 20), 23: (1, -20)}
    transforms = {}

    def transform(bone_id):
        if bone_id in transforms:
            return transforms[bone_id]
        frame = by_id[bone_id]
        parent_idx = frame['parent']
        parent_id = mesh['frames'][parent_idx]['bone_id'] if parent_idx >= 0 else None
        parent = transform(parent_id) if parent_id in by_id else np.eye(4)
        local = np.eye(4)
        if bone_id in rotations:
            axis, degrees = rotations[bone_id]
            a = np.deg2rad(degrees)
            c, s = np.cos(a), np.sin(a)
            r = (np.array([[1, 0, 0], [0, c, -s], [0, s, c]]) if axis == 0
                 else np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]))
            pivot = pivots[ids.index(bone_id)]
            local[:3, :3] = r
            local[:3, 3] = pivot - r @ pivot
        transforms[bone_id] = parent @ local
        return transforms[bone_id]

    matrices = np.stack([transform(b) for b in ids])
    v = np.column_stack([mesh['vertices'], np.ones(len(mesh['vertices']))])
    out = np.zeros((len(v), 3))
    for slot in range(4):
        x = np.einsum('nij,nj->ni', matrices[mesh['bone_indices'][:, slot]], v)[:, :3]
        out += x * mesh['bone_weights'][:, slot, None]
    if not np.isfinite(out).all():
        raise ValueError('Pose produced non-finite vertices')
    return out


def render_view(mesh, texture, vertices, yaw, width=360, height=660):
    """Two-sided, nearest-sampled texture rasterization with a true depth buffer."""
    a = np.deg2rad(yaw)
    right = np.array([0, np.sin(a), -np.cos(a)])
    camera = np.array([0, np.cos(a), np.sin(a)])
    reference = mesh['vertices']
    scale = (height - 65) / np.ptp(reference[:, 0])
    horizontal = vertices @ right
    scale = min(scale, (width - 30) / max(np.ptp(horizontal), 1e-6))
    px = width / 2 + (horizontal - (horizontal.max()+horizontal.min())/2) * scale
    py = height - 28 - (vertices[:, 0] - reference[:, 0].min()) * scale
    depth = vertices @ camera
    screen = np.column_stack([px, py])
    yy = np.linspace(0, 1, height)[:, None, None]
    canvas = np.broadcast_to(np.array([31, 36, 43]) + yy * np.array([12, 13, 15]),
                             (height, width, 3)).copy().astype(np.uint8)
    zbuf = np.full((height, width), -np.inf)
    triangles = mesh['triangles'][:, [1, 0, 3]].astype(int)
    tex_h, tex_w = texture.shape[:2]
    visible = 0
    light = np.array([0.35, 0.8, -0.45])
    light /= np.linalg.norm(light)
    for tri in triangles:
        p = screen[tri]
        lo = np.maximum(np.floor(p.min(0)).astype(int), [0, 0])
        hi = np.minimum(np.ceil(p.max(0)).astype(int), [width - 1, height - 1])
        if np.any(hi < lo):
            continue
        x, y = np.meshgrid(np.arange(lo[0], hi[0] + 1) + .5,
                           np.arange(lo[1], hi[1] + 1) + .5)
        den = (p[1, 1]-p[2, 1])*(p[0, 0]-p[2, 0]) + (p[2, 0]-p[1, 0])*(p[0, 1]-p[2, 1])
        if abs(den) < 1e-9:
            continue
        b0 = ((p[1, 1]-p[2, 1])*(x-p[2, 0]) + (p[2, 0]-p[1, 0])*(y-p[2, 1])) / den
        b1 = ((p[2, 1]-p[0, 1])*(x-p[2, 0]) + (p[0, 0]-p[2, 0])*(y-p[2, 1])) / den
        b2 = 1 - b0 - b1
        bary = np.stack([b0, b1, b2], axis=-1)
        z = bary @ depth[tri]
        sl = np.s_[lo[1]:hi[1]+1, lo[0]:hi[0]+1]
        mask = (bary.min(-1) >= -1e-7) & (z > zbuf[sl])
        if not mask.any():
            continue
        uv = bary @ mesh['uvs'][tri]
        # RW UV v=0 is the top row of the packed raster.
        tx = np.clip((uv[..., 0] * tex_w).astype(int), 0, tex_w-1)
        ty = np.clip((uv[..., 1] * tex_h).astype(int), 0, tex_h-1)
        normal = np.cross(vertices[tri[1]]-vertices[tri[0]], vertices[tri[2]]-vertices[tri[0]])
        normal /= max(np.linalg.norm(normal), 1e-12)
        shade = .78 + .22 * abs(normal @ light)
        colors = np.clip(texture[ty, tx] * shade, 0, 255).astype(np.uint8)
        canvas[sl][mask] = colors[mask]
        zbuf[sl][mask] = z[mask]
        visible += 1
    if np.isfinite(zbuf).sum() < 500:
        raise ValueError('Render is empty or incorrectly projected')
    return Image.fromarray(canvas), visible


def font(size):
    for path in ('C:/Windows/Fonts/consola.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dff', required=True)
    parser.add_argument('--txd', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    mesh = parse_ped_dff(Path(args.dff).read_bytes())
    textures = dict(read_txd_textures(Path(args.txd).read_bytes()))
    texture = textures[mesh['texture_name']]
    posed = posed_vertices(mesh)
    sheet = Image.new('RGB', (1800, 824), (20, 24, 30))
    draw = ImageDraw.Draw(sheet)
    draw.text((28, 18), Path(args.dff).stem.upper(), fill=(237, 224, 190), font=font(30))
    draw.text((28, 58), f'SINDACO HEAD / LSV2 BODY   |   {len(mesh["vertices"])} VERTICES / {len(mesh["triangles"])} TRIANGLES',
              fill=(158, 171, 184), font=font(17))
    stats = []
    for i, (label, yaw, vertices) in enumerate([
        ('Front', 0, mesh['vertices']), ('Side', 90, mesh['vertices']),
        ('Back', 180, mesh['vertices']), ('3/4', 35, mesh['vertices']), ('Pose Test', 25, posed),
    ]):
        panel, count = render_view(mesh, texture, vertices, yaw)
        sheet.paste(panel, (i*360, 110))
        draw.text((i*360+18, 86), label, fill=(223, 221, 209), font=font(19))
        stats.append({'view': label, 'triangles_rasterized': count})
    draw.text((28, 786), 'ACTUAL DFF + TXD | Pose: weighted bone rotations, not an in-game capture',
              fill=(158, 171, 184), font=font(17))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    print(json.dumps({'output': args.output, 'views': stats,
                      'pose_max_displacement': float(np.linalg.norm(posed-mesh['vertices'], axis=1).max())}, indent=2))


if __name__ == '__main__':
    main()
