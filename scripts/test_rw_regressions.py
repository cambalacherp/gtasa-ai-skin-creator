"""Regression checks against the real exported skin and corrupted weight streams."""
import struct
import os
import tempfile
import unittest
from pathlib import Path

import numpy as np

from build_ps2_rig_bpy import write_standalone_gtasa_ped_dff
from vanilla_rw_kitbash import parse_ped_dff, read_txd_textures, open_img_archive, extract_img_entry, splice_atlas
from quantize_ps2_txd import apply_ps2_color_pipeline
from match_skin_tone import load_profile, samples
from validate_rw_stream import audit_dff_file, parse_rw_chunks


def find_chunk(nodes, kind):
    for node in nodes:
        if node['type'] == kind:
            return node
        found = find_chunk(node['children'], kind)
        if found:
            return found


class StreamRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = Path(__file__).resolve().parents[1] / 'output/sindaco_lsv2/sindaco_lsv2.dff'
        cls.data = cls.output.read_bytes()
        cls.mesh = parse_ped_dff(cls.data)
        cls.skin = find_chunk(parse_rw_chunks(cls.data), 0x0116)

    def audit_mutation(self, edit):
        data = bytearray(self.data)
        payload = self.skin['offset'] + 12
        idx = payload + 4 + data[payload+1]
        weights = idx + len(self.mesh['vertices']) * 4
        edit(data, idx, weights)
        with tempfile.TemporaryDirectory(dir=self.output.parent) as tmp:
            path = Path(tmp) / 'mutated.dff'
            path.write_bytes(data)
            return audit_dff_file(str(path))

    def test_actual_skin_and_legitimate_pelvis(self):
        report = audit_dff_file(str(self.output))
        self.assertTrue(report['valid'], report['errors'])
        self.assertEqual(report['frame_count'], 33)
        self.assertEqual((report['vertex_count'], report['triangle_count']), (1080, 1165))
        self.assertGreater(self.mesh['bone_weights'][self.mesh['bone_indices'] == 1].sum(), 0)

    def test_head_keeps_original_crown_height_and_visible_neck(self):
        head = self.mesh['vertices'][self.mesh['uvs'][:, 0] < .5]
        self.assertGreater(head[:, 0].min(), .62, 'Chin must not be sunk into the shirt collar')
        self.assertAlmostEqual(head[:, 0].max(), .86963618, places=5)

    def test_body_skin_matches_head_in_exported_txd(self):
        decoded = read_txd_textures(self.output.with_suffix('.txd').read_bytes())[0][1]
        profile = load_profile('sindaco', 'lsv2')
        reference = np.median(samples(decoded[:, :256], profile['head_samples']), axis=0)
        body = np.median(samples(decoded[:, 256:384], profile['body_samples']), axis=0)
        self.assertLess(np.abs(reference-body).mean(), 4, (reference, body))
        self.assertLessEqual(len(np.unique(decoded.reshape(-1, 3), axis=0)), 256)

    def test_exported_head_and_non_skin_pixels_remain_identical(self):
        img_path = Path(os.environ.get('GTASA_GAME_DIR', 'C:/Juegos/gta clean'))/'models/gta3.img'
        if not img_path.exists():
            self.skipTest('Set GTASA_GAME_DIR to compare the vanilla atlas')
        handle, table = open_img_archive(str(img_path))
        try:
            head = read_txd_textures(extract_img_entry(handle, table, 'sindaco.txd'))[0][1]
            body = read_txd_textures(extract_img_entry(handle, table, 'lsv2.txd'))[0][1]
        finally:
            handle.close()
        atlas = splice_atlas(head, body)[0]
        baseline = np.asarray(apply_ps2_color_pipeline(atlas, target_size=(512, 256))[1])[:, :, :3]
        actual = read_txd_textures(self.output.with_suffix('.txd').read_bytes())[0][1]
        from PIL import Image
        body_mask = np.array(Image.open(self.output.with_name('sindaco_lsv2_body_skin_mask.png'))) > 0
        mask = np.zeros((256, 512), dtype=bool)
        mask[:, 256:384] = body_mask
        self.assertTrue(np.array_equal(actual[~mask], baseline[~mask]))
        original_detail = baseline[32:165, 324:384].astype(float).mean(2).ravel()
        corrected_detail = actual[32:165, 324:384].astype(float).mean(2).ravel()
        self.assertGreater(np.corrcoef(original_detail, corrected_detail)[0, 1], .98, 'Tattoo and shading detail must survive recoloring')

    def test_reject_root_weight(self):
        result = self.audit_mutation(lambda d, i, w: d.__setitem__(i, 0))
        self.assertTrue(any('Root' in e for e in result['errors']), result)

    def test_reject_invalid_index(self):
        result = self.audit_mutation(lambda d, i, w: d.__setitem__(i, 250))
        self.assertTrue(any('invalid weights or bone indices' in e for e in result['errors']), result)

    def test_reject_nan_weight(self):
        result = self.audit_mutation(lambda d, i, w: struct.pack_into('<f', d, w, float('nan')))
        self.assertFalse(result['valid'])

    def test_reject_negative_weights_even_with_unit_sum(self):
        result = self.audit_mutation(lambda d, i, w: struct.pack_into('<4f', d, w, 1.1, -.1, 0, 0))
        self.assertTrue(any('invalid weights' in e for e in result['errors']), result)

    def test_legacy_writer_geometry_offsets(self):
        with tempfile.TemporaryDirectory(dir=self.output.parent) as tmp:
            path = Path(tmp) / 'legacy.dff'
            info = write_standalone_gtasa_ped_dff(str(path), 'legacy')
            mesh = parse_ped_dff(path.read_bytes())
            self.assertEqual(len(mesh['vertices']), info['vertex_count'])
            self.assertTrue(np.isfinite(mesh['vertices']).all())
            self.assertLess(abs(mesh['vertices']).max(), 3)
            report = audit_dff_file(str(path))
            self.assertTrue(report['valid'], report['errors'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
