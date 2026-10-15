"""Skin pose deformation and compatibility entry point for local Blender CLI renders."""

import numpy as np



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


def main():
    from render_blender_cli import main as blender_main
    blender_main()


if __name__ == '__main__':
    main()
