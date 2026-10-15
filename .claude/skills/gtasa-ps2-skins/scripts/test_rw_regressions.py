"""Regression checks against the real exported skin and corrupted weight streams."""
import struct
import tempfile
import unittest
from pathlib import Path

import numpy as np

from build_ps2_rig_bpy import write_standalone_gtasa_ped_dff
from vanilla_rw_kitbash import parse_ped_dff
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
        self.assertEqual((report['vertex_count'], report['triangle_count']), (1050, 1145))
        self.assertGreater(self.mesh['bone_weights'][self.mesh['bone_indices'] == 1].sum(), 0)

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
